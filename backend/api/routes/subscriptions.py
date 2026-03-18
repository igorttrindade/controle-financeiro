import json

from flask import Blueprint, current_app, g, jsonify

from backend.api.middlewares.auth import token_required
from backend.api.middlewares.cakto_webhook import validate_cakto_secret
from backend.db.connection import get_db_connection
from backend.services.subscription_service import (
    cancel_subscription,
    check_transaction_limit,
    downgrade_to_free,
    get_user_plan_limits,
    get_user_subscription,
    get_user_by_email,
    upgrade_to_pro,
)

subscription_bp = Blueprint('subscription', __name__)


@subscription_bp.route('', methods=['GET'])
@subscription_bp.route('/', methods=['GET'])
@token_required
def get_subscription(current_user_id):
    try:
        data = get_user_subscription(current_user_id)
        return jsonify(data), 200
    except RuntimeError as err:
        return jsonify({'error': str(err)}), 503
    except Exception:
        return jsonify({'error': 'Erro interno no servidor'}), 500


@subscription_bp.route('/limits', methods=['GET'])
@token_required
def get_subscription_limits(current_user_id):
    try:
        limits = get_user_plan_limits(current_user_id)
        usage = check_transaction_limit(current_user_id)
        return (
            jsonify(
                {
                    'plan_name': limits['plan_name'],
                    'monthly_transaction_limit': limits['monthly_transaction_limit'],
                    'is_pro': limits['is_pro'],
                    'status': limits['status'],
                    'current_count': usage['current_count'],
                    'allowed': usage['allowed'],
                }
            ),
            200,
        )
    except RuntimeError as err:
        return jsonify({'error': str(err)}), 503
    except Exception:
        return jsonify({'error': 'Erro interno no servidor'}), 500


@subscription_bp.route('/webhook', methods=['POST'])
@validate_cakto_secret
def cakto_webhook():
    payload = g.get('cakto_payload') or {}
    event_name = str(payload.get('event') or payload.get('custom_id') or '').strip().lower()
    data = payload.get('data') if isinstance(payload.get('data'), dict) else {}
    customer = data.get('customer') if isinstance(data.get('customer'), dict) else {}
    customer_email = str(customer.get('email') or '').strip().lower()
    order_id = str(data.get('id') or payload.get('id') or '')

    user_id = None
    log_status = 'ignored'
    error_message = None

    try:
        if not event_name:
            log_status = 'ignored'
            return jsonify({'status': 'ignored', 'event': event_name}), 200

        if event_name not in {'purchase_approved', 'refund', 'chargeback', 'subscription_canceled'}:
            log_status = 'ignored'
            return jsonify({'status': 'ignored', 'event': event_name}), 200

        if not customer_email:
            current_app.logger.warning(
                'Webhook Cakto sem customer.email. payload=%s',
                payload,
            )
            log_status = 'error'
            error_message = 'customer_email_missing'
            return jsonify({'status': 'ok'}), 200

        user = get_user_by_email(customer_email)
        if not user:
            current_app.logger.warning(
                'Webhook Cakto com usuário não encontrado. email=%s event=%s',
                customer_email,
                event_name,
            )
            log_status = 'user_not_found'
            return jsonify({'status': 'ok'}), 200

        user_id = int(user['id_user'])

        if event_name == 'purchase_approved':
            upgrade_to_pro(
                user_id,
                gateway='cakto',
                gateway_subscription_id=order_id,
                gateway_customer_id=customer_email,
            )
            log_status = 'processed'
            return jsonify({'status': 'ok'}), 200

        if event_name in {'refund', 'chargeback'}:
            downgrade_to_free(user_id)
            log_status = 'processed'
            return jsonify({'status': 'ok'}), 200

        if event_name == 'subscription_canceled':
            cancel_subscription(user_id, at_period_end=False)
            log_status = 'processed'
            return jsonify({'status': 'ok'}), 200

        log_status = 'ignored'
        return jsonify({'status': 'ignored', 'event': event_name}), 200
    except RuntimeError as err:
        log_status = 'error'
        error_message = str(err)
        return jsonify({'error': str(err)}), 503
    except Exception:
        current_app.logger.exception('Erro ao processar webhook da Cakto')
        log_status = 'error'
        error_message = 'Erro interno no servidor'
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        _insert_webhook_log(
            event=event_name or None,
            payload=payload,
            customer_email=customer_email or None,
            user_id=user_id,
            status=log_status,
            error_message=error_message,
        )


def _insert_webhook_log(event, payload, customer_email, user_id, status, error_message):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            current_app.logger.warning('Conexão indisponível para registrar webhook da Cakto.')
            return

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO webhook_logs (
                gateway,
                event,
                payload,
                customer_email,
                id_user_fk,
                status,
                error_message
            )
            VALUES ('cakto', %s, %s::jsonb, %s, %s, %s, %s);
            """,
            (
                event,
                json.dumps(payload, ensure_ascii=False),
                customer_email,
                user_id,
                status,
                error_message,
            ),
        )
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception('Falha ao salvar log de webhook da Cakto.')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
