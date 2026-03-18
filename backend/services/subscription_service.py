from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app

from backend.db.connection import get_db_connection

ACTIVE_PRO_STATUSES = {'active', 'trialing'}


def _month_window_utc(now=None):
    now = now or datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    return start, end


def _normalize_subscription_row(row):
    if not row:
        return None
    return {
        'id_subscription': row[0],
        'id_user': row[1],
        'status': row[2],
        'gateway': row[3],
        'gateway_subscription_id': row[4],
        'gateway_customer_id': row[5],
        'current_period_start': row[6].isoformat() if row[6] else None,
        'current_period_end': row[7].isoformat() if row[7] else None,
        'cancel_at_period_end': bool(row[8]),
        'trial_ends_at': row[9].isoformat() if row[9] else None,
        'plan_id': row[10],
        'plan_name': row[11],
        'plan_display_name': row[12],
        'monthly_transaction_limit': row[13],
        'price_cents': row[14],
        'is_pro': row[11] == 'pro',
    }


def _select_user_subscription(cur, user_id):
    cur.execute(
        """
        SELECT
            s.id_subscription,
            s.id_user_fk,
            s.status,
            s.gateway,
            s.gateway_subscription_id,
            s.gateway_customer_id,
            s.current_period_start,
            s.current_period_end,
            s.cancel_at_period_end,
            s.trial_ends_at,
            p.id_plan,
            p.name,
            p.display_name,
            p.monthly_transaction_limit,
            p.price_cents
        FROM tb_subscriptions s
        JOIN tb_plans p ON p.id_plan = s.id_plan_fk
        WHERE s.id_user_fk = %s
        LIMIT 1;
        """,
        (user_id,),
    )
    return _normalize_subscription_row(cur.fetchone())


def _ensure_default_plans(cur):
    cur.execute(
        """
        INSERT INTO tb_plans (name, display_name, monthly_transaction_limit, price_cents)
        VALUES
          ('free', 'Gratuito', 50, 0),
          ('pro', 'Pro', NULL, 0)
        ON CONFLICT (name) DO UPDATE
        SET
          display_name = EXCLUDED.display_name,
          monthly_transaction_limit = EXCLUDED.monthly_transaction_limit,
          price_cents = EXCLUDED.price_cents,
          is_active = TRUE;
        """
    )


def _get_plan_id(cur, plan_name):
    cur.execute(
        """
        SELECT id_plan
        FROM tb_plans
        WHERE name = %s
          AND is_active = TRUE
        LIMIT 1;
        """,
        (plan_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def ensure_free_subscription_for_user(user_id: int, conn=None, cur=None) -> dict:
    owns_connection = conn is None or cur is None
    local_conn = conn
    local_cur = cur

    try:
        if owns_connection:
            local_conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
            if not local_conn:
                raise RuntimeError('Serviço temporariamente indisponível')
            local_cur = local_conn.cursor()

        _ensure_default_plans(local_cur)
        existing = _select_user_subscription(local_cur, user_id)
        if existing:
            if owns_connection:
                local_conn.commit()
            return existing

        free_plan_id = _get_plan_id(local_cur, 'free')
        if free_plan_id is None:
            raise RuntimeError('Plano free indisponível')

        local_cur.execute(
            """
            INSERT INTO tb_subscriptions (
                id_user_fk,
                id_plan_fk,
                status,
                current_period_start,
                created_at,
                updated_at
            )
            VALUES (%s, %s, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (id_user_fk) DO NOTHING;
            """,
            (user_id, free_plan_id),
        )

        created = _select_user_subscription(local_cur, user_id)
        if owns_connection:
            local_conn.commit()
        return created
    except Exception:
        if owns_connection and local_conn:
            local_conn.rollback()
        raise
    finally:
        if owns_connection and local_cur:
            local_cur.close()
        if owns_connection and local_conn:
            local_conn.close()


def get_user_subscription(user_id: int) -> dict:
    conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
    if not conn:
        raise RuntimeError('Serviço temporariamente indisponível')

    cur = None
    try:
        cur = conn.cursor()
        subscription = _select_user_subscription(cur, user_id)
        if subscription:
            return subscription

        return ensure_free_subscription_for_user(user_id, conn=conn, cur=cur)
    finally:
        if cur:
            cur.close()
        conn.close()


def get_user_plan_limits(user_id: int) -> dict:
    subscription = get_user_subscription(user_id)
    status = subscription.get('status')
    is_active_pro = subscription.get('plan_name') == 'pro' and status in ACTIVE_PRO_STATUSES
    if is_active_pro:
        return {
            'plan_name': 'pro',
            'monthly_transaction_limit': None,
            'is_pro': True,
            'status': status,
        }

    limit = subscription.get('monthly_transaction_limit')
    if limit is None:
        limit = 50

    return {
        'plan_name': 'free',
        'monthly_transaction_limit': int(limit),
        'is_pro': False,
        'status': status,
    }


def count_user_transactions_this_month(user_id: int) -> int:
    conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
    if not conn:
        raise RuntimeError('Serviço temporariamente indisponível')

    cur = None
    try:
        cur = conn.cursor()
        month_start, month_end = _month_window_utc()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM tb_transacoes
            WHERE id_user_fk = %s
              AND dt_transacao >= %s
              AND dt_transacao < %s;
            """,
            (user_id, month_start, month_end),
        )
        row = cur.fetchone()
        return int(row[0] or 0)
    finally:
        if cur:
            cur.close()
        conn.close()


def check_transaction_limit(user_id: int) -> dict:
    limits = get_user_plan_limits(user_id)
    plan_name = limits['plan_name']
    limit = limits['monthly_transaction_limit']

    if limits['is_pro']:
        current_count = count_user_transactions_this_month(user_id)
        return {
            'allowed': True,
            'current_count': current_count,
            'limit': None,
            'plan': plan_name,
        }

    current_count = count_user_transactions_this_month(user_id)
    allowed = limit is None or current_count < limit

    return {
        'allowed': bool(allowed),
        'current_count': current_count,
        'limit': limit,
        'plan': plan_name,
    }


def _invalidate_dashboard_cache_for_user(user_id: int):
    from backend.api.routes.dashboard import invalidate_dashboard_cache

    invalidate_dashboard_cache(user_id)


def _set_plan(user_id: int, plan_name: str, status: str, extra_fields: dict | None = None):
    conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
    if not conn:
        raise RuntimeError('Serviço temporariamente indisponível')

    cur = None
    try:
        cur = conn.cursor()
        _ensure_default_plans(cur)

        subscription = _select_user_subscription(cur, user_id)
        if not subscription:
            subscription = ensure_free_subscription_for_user(user_id, conn=conn, cur=cur)

        target_plan_id = _get_plan_id(cur, plan_name)
        if target_plan_id is None:
            raise RuntimeError(f'Plano {plan_name} indisponível')

        extra_fields = extra_fields or {}

        cur.execute(
            """
            UPDATE tb_subscriptions
            SET id_plan_fk = %s,
                status = %s,
                gateway = %s,
                gateway_subscription_id = %s,
                gateway_customer_id = %s,
                current_period_start = %s,
                current_period_end = %s,
                cancel_at_period_end = %s,
                trial_ends_at = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_user_fk = %s;
            """,
            (
                target_plan_id,
                status,
                extra_fields.get('gateway'),
                extra_fields.get('gateway_subscription_id'),
                extra_fields.get('gateway_customer_id'),
                extra_fields.get('current_period_start'),
                extra_fields.get('current_period_end'),
                bool(extra_fields.get('cancel_at_period_end', False)),
                extra_fields.get('trial_ends_at'),
                user_id,
            ),
        )

        updated = _select_user_subscription(cur, user_id)
        conn.commit()
        _invalidate_dashboard_cache_for_user(user_id)
        return updated
    except Exception:
        conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        conn.close()


def upgrade_to_pro(user_id: int, gateway: str, gateway_subscription_id: str, gateway_customer_id: str) -> dict:
    return _set_plan(
        user_id=user_id,
        plan_name='pro',
        status='active',
        extra_fields={
            'gateway': gateway,
            'gateway_subscription_id': gateway_subscription_id,
            'gateway_customer_id': gateway_customer_id,
            'current_period_start': datetime.now(timezone.utc),
            'cancel_at_period_end': False,
        },
    )


def cancel_subscription(user_id: int, at_period_end: bool = True) -> dict:
    if at_period_end:
        current = get_user_subscription(user_id)
        return _set_plan(
            user_id=user_id,
            plan_name=current['plan_name'],
            status=current['status'] if current['status'] in ACTIVE_PRO_STATUSES else 'canceled',
            extra_fields={
                'gateway': current.get('gateway'),
                'gateway_subscription_id': current.get('gateway_subscription_id'),
                'gateway_customer_id': current.get('gateway_customer_id'),
                'current_period_start': datetime.fromisoformat(current['current_period_start']) if current.get('current_period_start') else None,
                'current_period_end': datetime.fromisoformat(current['current_period_end']) if current.get('current_period_end') else None,
                'cancel_at_period_end': True,
                'trial_ends_at': datetime.fromisoformat(current['trial_ends_at']) if current.get('trial_ends_at') else None,
            },
        )

    return downgrade_to_free(user_id)


def downgrade_to_free(user_id: int) -> dict:
    return _set_plan(
        user_id=user_id,
        plan_name='free',
        status='active',
        extra_fields={
            'gateway': None,
            'gateway_subscription_id': None,
            'gateway_customer_id': None,
            'current_period_start': datetime.now(timezone.utc),
            'current_period_end': None,
            'cancel_at_period_end': False,
            'trial_ends_at': None,
        },
    )


def get_user_by_email(email: str) -> dict | None:
    normalized_email = str(email or '').strip().lower()
    if not normalized_email:
        return None

    conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
    if not conn:
        raise RuntimeError('Serviço temporariamente indisponível')

    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id_user, email_user
            FROM tb_user
            WHERE LOWER(email_user) = LOWER(%s)
            LIMIT 1;
            """,
            (normalized_email,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            'id_user': int(row[0]),
            'email_user': row[1],
        }
    finally:
        if cur:
            cur.close()
        conn.close()
