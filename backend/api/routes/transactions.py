from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo
from flask import Blueprint, request, jsonify, current_app
from backend.db.connection import get_db_connection
from backend.api.middlewares.auth import token_required
from backend.api.middlewares.plan_limit import require_plan_allowance
from backend.api.routes.dashboard import invalidate_dashboard_cache

transaction_bp = Blueprint('transaction', __name__)
INCOME_TYPES = {'entrada', 'receita', 'income'}
EXPENSE_TYPES = {'saida', 'despesa', 'expense'}


def _safe_invalidate_dashboard_cache(user_id):
    try:
        invalidate_dashboard_cache(user_id)
    except Exception:
        current_app.logger.warning(
            "Falha ao invalidar cache de dashboard para user_id=%s", user_id
        )


def _format_transaction_date(raw_date):
    if raw_date is None:
        return None
    if hasattr(raw_date, "strftime"):
        return raw_date.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(raw_date, str):
        try:
            return datetime.fromisoformat(raw_date).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return raw_date
    return str(raw_date)


def _normalize_operation_type(raw_type):
    normalized = str(raw_type or '').strip().lower()
    if normalized in INCOME_TYPES:
        return 'entrada'
    if normalized in EXPENSE_TYPES:
        return 'despesa'
    return None


def _parse_positive_amount(raw_value):
    try:
        value = Decimal(str(raw_value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if value <= 0:
        return None
    return value


def _parse_transaction_datetime(raw_value):
    if raw_value in (None, ''):
        return None

    if not isinstance(raw_value, str):
        return False

    candidate = raw_value.strip()
    if not candidate:
        return None

    if candidate.endswith('Z'):
        candidate = candidate[:-1] + '+00:00'

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False

    try:
        app_tz = ZoneInfo(current_app.config.get('APP_TIMEZONE', 'America/Sao_Paulo'))
    except Exception:
        app_tz = timezone.utc

    if parsed.tzinfo is None:
        # Assume datetime-local values are in application timezone.
        return parsed

    return parsed.astimezone(app_tz).replace(tzinfo=None)


@transaction_bp.route('/operations', methods=['GET'])
@token_required
def list_operations(current_user_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id_operacao, nome_operacao, tipo_operacao
            FROM tb_operacoes
            WHERE id_user_fk = %s
            ORDER BY nome_operacao ASC;
            """,
            (current_user_id,),
        )
        rows = cur.fetchall()
        operations = [
            {
                'id_operacao': row[0],
                'nome_operacao': row[1],
                'tipo_operacao': row[2],
            }
            for row in rows
        ]
        return jsonify(operations), 200
    except Exception:
        current_app.logger.exception("Erro ao listar operações para user_id=%s", current_user_id)
        if current_app.debug:
            return jsonify({'error': 'Erro interno no servidor'}), 500
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@transaction_bp.route('/operations', methods=['POST'])
@token_required
def create_operation(current_user_id):
    data = request.get_json(silent=True) or {}
    nome_operacao = str(data.get('nome_operacao') or '').strip()
    tipo_operacao = _normalize_operation_type(data.get('tipo_operacao'))

    if not nome_operacao:
        return jsonify({'error': 'O nome da operação é obrigatório'}), 400
    if len(nome_operacao) < 2 or len(nome_operacao) > 120:
        return jsonify({'error': 'O nome da operação deve ter entre 2 e 120 caracteres'}), 400
    if not tipo_operacao:
        return jsonify({'error': 'Tipo de operação inválido'}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id_operacao, nome_operacao, tipo_operacao
            FROM tb_operacoes
            WHERE id_user_fk = %s
              AND LOWER(nome_operacao) = LOWER(%s)
              AND tipo_operacao = %s
            LIMIT 1;
            """,
            (current_user_id, nome_operacao, tipo_operacao),
        )
        existing = cur.fetchone()
        if existing:
            return (
                jsonify(
                    {
                        'id_operacao': existing[0],
                        'nome_operacao': existing[1],
                        'tipo_operacao': existing[2],
                        'message': 'Operação já existente',
                    }
                ),
                200,
            )

        cur.execute(
            """
            INSERT INTO tb_operacoes (id_user_fk, nome_operacao, tipo_operacao, dt_criacao)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id_operacao, nome_operacao, tipo_operacao;
            """,
            (current_user_id, nome_operacao, tipo_operacao),
        )
        created = cur.fetchone()
        conn.commit()
        return (
            jsonify(
                {
                    'id_operacao': created[0],
                    'nome_operacao': created[1],
                    'tipo_operacao': created[2],
                    'message': 'Operação criada com sucesso',
                }
            ),
            201,
        )
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception("Erro ao criar operação para user_id=%s", current_user_id)
        if current_app.debug:
            return jsonify({'error': 'Erro interno no servidor'}), 500
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@transaction_bp.route('/create', methods=['POST'])
@token_required
@require_plan_allowance
def create_transaction(current_user_id):
    data = request.get_json(silent=True) or {}
    id_operacao = data.get('id_operacao')
    valor_transacao = _parse_positive_amount(data.get('valor_transacao'))
    descricao_transacao = str(data.get('descricao_transacao') or '').strip()
    dt_transacao = _parse_transaction_datetime(data.get('dt_transacao'))

    if not id_operacao:
        return jsonify({'error': 'O ID da operação é obrigatório'}), 400
    try:
        id_operacao = int(id_operacao)
    except (ValueError, TypeError):
        return jsonify({'error': 'O ID da operação é inválido'}), 400
    if valor_transacao is None:
        return jsonify({'error': 'O valor da transação deve ser numérico e maior que zero'}), 400
    if len(descricao_transacao) < 3 or len(descricao_transacao) > 500:
        return jsonify({'error': 'A descrição deve ter entre 3 e 500 caracteres'}), 400
    if dt_transacao is False:
        return jsonify({'error': 'Data da transação inválida'}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        cur.execute(
            """
            SELECT 1
            FROM tb_operacoes
            WHERE id_operacao = %s AND id_user_fk = %s
            LIMIT 1;
            """,
            (id_operacao, current_user_id),
        )
        operation_exists = cur.fetchone()
        if not operation_exists:
            return jsonify({'error': 'Operação não pertence ao usuário autenticado'}), 403

        if dt_transacao is None:
            cur.execute(
                """
                INSERT INTO tb_transacoes (
                    id_operacao_fk, id_user_fk, valor_transacao, descricao_transacao, dt_transacao
                )
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id_transacao;
                """,
                (id_operacao, current_user_id, valor_transacao, descricao_transacao),
            )
        else:
            cur.execute(
                """
                INSERT INTO tb_transacoes (
                    id_operacao_fk, id_user_fk, valor_transacao, descricao_transacao, dt_transacao
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_transacao;
                """,
                (id_operacao, current_user_id, valor_transacao, descricao_transacao, dt_transacao),
            )

        new_id = cur.fetchone()[0]
        conn.commit()
        _safe_invalidate_dashboard_cache(current_user_id)
        return jsonify({'message': 'Transação concluída!', 'id_transacao': new_id}), 201
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception("Erro ao criar transação para user_id=%s", current_user_id)
        if current_app.debug:
            return jsonify({'error': 'Erro interno no servidor'}), 500
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@transaction_bp.route('/<int:id_transacao>', methods=['GET'])
@token_required
def get_transaction_by_id(current_user_id, id_transacao):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                t.id_transacao,
                t.id_operacao_fk,
                t.dt_transacao,
                o.nome_operacao,
                t.valor_transacao,
                o.tipo_operacao,
                t.descricao_transacao
            FROM tb_transacoes t
            JOIN tb_operacoes o ON o.id_operacao = t.id_operacao_fk
            WHERE t.id_transacao = %s
              AND t.id_user_fk = %s
            LIMIT 1;
            """,
            (id_transacao, current_user_id),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Transação não encontrada'}), 404

        return (
            jsonify(
                {
                    'id': row[0],
                    'id_operacao': row[1],
                    'data': _format_transaction_date(row[2]),
                    'nome': row[3],
                    'valor': float(row[4]),
                    'tipo': row[5],
                    'descricao': row[6] or '',
                }
            ),
            200,
        )
    except Exception:
        current_app.logger.exception(
            "Erro ao buscar transação id=%s para user_id=%s", id_transacao, current_user_id
        )
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@transaction_bp.route('/<int:id_transacao>', methods=['PUT'])
@token_required
def update_transaction(current_user_id, id_transacao):
    data = request.get_json(silent=True) or {}
    id_operacao = data.get('id_operacao')
    valor_transacao = _parse_positive_amount(data.get('valor_transacao'))
    descricao_transacao = str(data.get('descricao_transacao') or '').strip()
    dt_transacao = _parse_transaction_datetime(data.get('dt_transacao'))

    if not id_operacao:
        return jsonify({'error': 'O ID da operação é obrigatório'}), 400
    try:
        id_operacao = int(id_operacao)
    except (ValueError, TypeError):
        return jsonify({'error': 'O ID da operação é inválido'}), 400
    if valor_transacao is None:
        return jsonify({'error': 'O valor da transação deve ser numérico e maior que zero'}), 400
    if len(descricao_transacao) < 3 or len(descricao_transacao) > 500:
        return jsonify({'error': 'A descrição deve ter entre 3 e 500 caracteres'}), 400
    if dt_transacao is False:
        return jsonify({'error': 'Data da transação inválida'}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 1
            FROM tb_transacoes
            WHERE id_transacao = %s AND id_user_fk = %s
            LIMIT 1;
            """,
            (id_transacao, current_user_id),
        )
        transaction_exists = cur.fetchone()
        if not transaction_exists:
            return jsonify({'error': 'Transação não encontrada'}), 404

        cur.execute(
            """
            SELECT 1
            FROM tb_operacoes
            WHERE id_operacao = %s AND id_user_fk = %s
            LIMIT 1;
            """,
            (id_operacao, current_user_id),
        )
        operation_exists = cur.fetchone()
        if not operation_exists:
            return jsonify({'error': 'Operação não pertence ao usuário autenticado'}), 403

        if dt_transacao is None:
            cur.execute(
                """
                UPDATE tb_transacoes
                SET id_operacao_fk = %s,
                    valor_transacao = %s,
                    descricao_transacao = %s,
                    dt_transacao = CURRENT_TIMESTAMP
                WHERE id_transacao = %s
                  AND id_user_fk = %s;
                """,
                (id_operacao, valor_transacao, descricao_transacao, id_transacao, current_user_id),
            )
        else:
            cur.execute(
                """
                UPDATE tb_transacoes
                SET id_operacao_fk = %s,
                    valor_transacao = %s,
                    descricao_transacao = %s,
                    dt_transacao = %s
                WHERE id_transacao = %s
                  AND id_user_fk = %s;
                """,
                (id_operacao, valor_transacao, descricao_transacao, dt_transacao, id_transacao, current_user_id),
            )

        conn.commit()
        _safe_invalidate_dashboard_cache(current_user_id)
        return jsonify({'message': 'Transação atualizada com sucesso'}), 200
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception(
            "Erro ao atualizar transação id=%s para user_id=%s", id_transacao, current_user_id
        )
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@transaction_bp.route('/', methods=['GET'])
@token_required
def get_transactions(current_user_id):
    conn = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()

        query = """
            SELECT t.id_transacao, t.dt_transacao, o.nome_operacao, t.valor_transacao, o.tipo_operacao
            FROM tb_transacoes t
            JOIN tb_operacoes o ON t.id_operacao_fk = o.id_operacao
            WHERE t.id_user_fk = %s
            ORDER BY t.dt_transacao DESC;
        """
        cur.execute(query, (current_user_id,))
        rows = cur.fetchall()
        
        transactions = [
            {
                'id': row[0],
                'data': _format_transaction_date(row[1]),
                'nome': row[2],
                'valor': float(row[3]),
                'tipo': row[4]
            } for row in rows
        ]
        
        cur.close()
        return jsonify(transactions), 200
    except Exception as e:
        current_app.logger.exception("Erro ao buscar transações para user_id=%s", current_user_id)
        if current_app.debug:
            return jsonify({'error': 'Erro interno no servidor', 'detail': str(e)}), 500
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if conn:
            conn.close()


@transaction_bp.route('/<int:id_transacao>', methods=['DELETE'])
@token_required
def delete_transaction(current_user_id, id_transacao):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM tb_transacoes
            WHERE id_transacao = %s
              AND id_user_fk = %s
            RETURNING id_transacao;
            """,
            (id_transacao, current_user_id),
        )
        deleted = cur.fetchone()
        if not deleted:
            return jsonify({'error': 'Transação não encontrada'}), 404

        conn.commit()
        _safe_invalidate_dashboard_cache(current_user_id)
        return jsonify({'message': 'Transação excluída com sucesso'}), 200
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception(
            "Erro ao excluir transação id=%s para user_id=%s", id_transacao, current_user_id
        )
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
