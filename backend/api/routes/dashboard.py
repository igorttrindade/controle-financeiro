import re
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from backend.api.middlewares.auth import token_required
from backend.db.connection import get_db_connection
from backend.services.aggregator import aggregate_transactions
from backend.services.ai_explainer import generate_natural_summary
from backend.services.cache import cache_backend
from backend.services.projection_engine import calculate_projection
from backend.services.recommendation_engine import generate_recommendations


dashboard_bp = Blueprint("dashboard", __name__)

INCOME_TYPES = {"entrada", "receita", "income"}
EXPENSE_TYPES = {"saida", "despesa", "expense"}
_MONTH_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
DASHBOARD_CACHE_TTL_SECONDS = 900


def _build_dashboard_cache_key(user_id: int, period: str) -> str:
    return f"dashboard:{user_id}:{period}"


def invalidate_dashboard_cache(user_id: int) -> None:
    cache_backend.delete_pattern(f"dashboard:{user_id}:*")


def _parse_month(month_param: str | None) -> tuple[str, date, date] | tuple[None, None, None]:
    if month_param is None:
        today = date.today()
        period = f"{today.year:04d}-{today.month:02d}"
    else:
        period = month_param.strip()
        if not _MONTH_REGEX.fullmatch(period):
            return None, None, None

    year, month = (int(part) for part in period.split("-"))
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    return period, start_date, end_date


def _normalize_transaction_type(raw_type):
    normalized = str(raw_type or "").strip().lower()
    if normalized in INCOME_TYPES:
        return "income"
    if normalized in EXPENSE_TYPES:
        return "expense"
    return None


def _fetch_month_transactions(cur, user_id, start_date, end_date):
    cur.execute(
        """
        SELECT
            o.nome_operacao,
            o.tipo_operacao,
            t.valor_transacao,
            t.dt_transacao
        FROM tb_transacoes t
        JOIN tb_operacoes o ON o.id_operacao = t.id_operacao_fk
        WHERE t.id_user_fk = %s
          AND t.dt_transacao >= %s
          AND t.dt_transacao < %s
        ORDER BY t.dt_transacao DESC;
        """,
        (user_id, start_date, end_date),
    )

    rows = cur.fetchall()
    normalized = []
    for row in rows:
        tx_type = _normalize_transaction_type(row[1])
        if not tx_type:
            continue

        try:
            value = float(row[2])
        except (TypeError, ValueError):
            continue

        tx_date = row[3]
        if isinstance(tx_date, datetime):
            tx_date = tx_date.strftime("%Y-%m-%d %H:%M:%S")

        normalized.append(
            {
                "type": tx_type,
                "value": value,
                "category": row[0],
                "date": tx_date,
            }
        )
    return normalized


def _fetch_monthly_goal(cur, user_id):
    cur.execute(
        """
        SELECT monthly_goal_value
        FROM tb_user_profile
        WHERE id_user_fk = %s
        LIMIT 1;
        """,
        (user_id,),
    )
    row = cur.fetchone()
    if not row or row[0] is None:
        return None
    try:
        return float(row[0])
    except (TypeError, ValueError):
        return None


@dashboard_bp.route("/intelligent-summary", methods=["GET"])
@token_required
def intelligent_summary(current_user_id):
    month_param = request.args.get("month")
    period, start_date, end_date = _parse_month(month_param)
    if not period:
        return jsonify({"error": "Parâmetro month inválido. Use YYYY-MM."}), 400

    cache_key = _build_dashboard_cache_key(current_user_id, period)
    cached_payload = cache_backend.get(cache_key)
    if cached_payload is not None:
        return jsonify(cached_payload), 200

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config["DATABASE_CONFIG"])
        if not conn:
            return jsonify({"error": "Serviço temporariamente indisponível"}), 503
        cur = conn.cursor()

        transactions = _fetch_month_transactions(cur, current_user_id, start_date, end_date)
        meta_value = _fetch_monthly_goal(cur, current_user_id)

        aggregated = aggregate_transactions(transactions)
        projection = calculate_projection(
            transactions=transactions,
            aggregated=aggregated,
            period=period,
            meta_value=meta_value,
        )
        recommendations = generate_recommendations(projection)
        natural_summary = generate_natural_summary(projection, recommendations)

        response_payload = {
            "period": period,
            "totals": aggregated,
            "projection": projection,
            "recommendations": recommendations,
            "natural_summary": natural_summary,
        }
        cache_backend.set(cache_key, response_payload, DASHBOARD_CACHE_TTL_SECONDS)

        return (
            jsonify(response_payload),
            200,
        )
    except Exception:
        current_app.logger.exception(
            "Erro ao gerar resumo inteligente do dashboard para user_id=%s", current_user_id
        )
        return jsonify({"error": "Erro interno no servidor"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
