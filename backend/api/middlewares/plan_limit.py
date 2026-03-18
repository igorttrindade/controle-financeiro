from functools import wraps

from flask import jsonify

from backend.services.subscription_service import check_transaction_limit


def require_plan_allowance(f):
    @wraps(f)
    def decorated(current_user_id, *args, **kwargs):
        limits = check_transaction_limit(current_user_id)
        if limits.get('allowed'):
            return f(current_user_id, *args, **kwargs)

        limit = limits.get('limit')
        plan_name = limits.get('plan', 'free')
        return (
            jsonify(
                {
                    'error': 'transaction_limit_reached',
                    'message': (
                        f'Você atingiu o limite de {limit} transações do plano gratuito.'
                        if limit is not None
                        else 'Você atingiu o limite de transações do seu plano atual.'
                    ),
                    'current_count': limits.get('current_count', 0),
                    'limit': limit,
                    'plan': plan_name,
                    'upgrade_url': '/upgrade',
                }
            ),
            403,
        )

    return decorated
