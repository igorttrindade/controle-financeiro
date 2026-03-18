import datetime
import unittest
from unittest.mock import patch

import jwt

from backend.app import app
from backend.api.security.token_store import clear_revocations
from backend.services import subscription_service


class ServiceCursorFake:
    def __init__(self, fetchone_values=None):
        self._fetchone_values = list(fetchone_values or [])
        self.execute_calls = []

    def execute(self, query, params=None):
        self.execute_calls.append((query, params))

    def fetchone(self):
        if self._fetchone_values:
            return self._fetchone_values.pop(0)
        return None

    def close(self):
        return None


class ServiceConnectionFake:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        return None


class SubscriptionServiceTests(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key-with-at-least-32-bytes",
            JWT_ISSUER="test-issuer",
            JWT_AUDIENCE="test-audience",
        )
        clear_revocations()
        self.client = app.test_client()

    def _make_token(self, user_id=1):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "jti": f"subscription-test-jti-{user_id}",
            "iat": now,
            "nbf": now,
            "exp": now + datetime.timedelta(hours=1),
            "iss": app.config["JWT_ISSUER"],
            "aud": app.config["JWT_AUDIENCE"],
        }
        return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

    def test_free_user_within_limit_is_allowed(self):
        with patch.object(
            subscription_service,
            "get_user_plan_limits",
            return_value={
                "plan_name": "free",
                "monthly_transaction_limit": 50,
                "is_pro": False,
                "status": "active",
            },
        ), patch.object(subscription_service, "count_user_transactions_this_month", return_value=10):
            result = subscription_service.check_transaction_limit(1)

        self.assertTrue(result["allowed"])
        self.assertEqual(result["plan"], "free")
        self.assertEqual(result["limit"], 50)

    def test_free_user_at_limit_is_blocked(self):
        with patch.object(
            subscription_service,
            "get_user_plan_limits",
            return_value={
                "plan_name": "free",
                "monthly_transaction_limit": 50,
                "is_pro": False,
                "status": "active",
            },
        ), patch.object(subscription_service, "count_user_transactions_this_month", return_value=50):
            result = subscription_service.check_transaction_limit(1)

        self.assertFalse(result["allowed"])
        self.assertEqual(result["current_count"], 50)
        self.assertEqual(result["limit"], 50)

    def test_pro_user_is_always_allowed(self):
        with patch.object(
            subscription_service,
            "get_user_plan_limits",
            return_value={
                "plan_name": "pro",
                "monthly_transaction_limit": None,
                "is_pro": True,
                "status": "active",
            },
        ), patch.object(subscription_service, "count_user_transactions_this_month", return_value=250):
            result = subscription_service.check_transaction_limit(1)

        self.assertTrue(result["allowed"])
        self.assertEqual(result["plan"], "pro")
        self.assertIsNone(result["limit"])

    def test_auto_creates_free_subscription_for_new_user(self):
        # fetchone call order:
        # 1) _select_user_subscription -> None
        # 2) _get_plan_id('free') -> (1,)
        # 3) _select_user_subscription after insert -> complete row
        cursor = ServiceCursorFake(
            fetchone_values=[
                None,
                (1,),
                (
                    99,
                    7,
                    "active",
                    None,
                    None,
                    None,
                    None,
                    None,
                    False,
                    None,
                    1,
                    "free",
                    "Gratuito",
                    50,
                    0,
                ),
            ]
        )
        conn = ServiceConnectionFake(cursor)

        with app.app_context():
            created = subscription_service.ensure_free_subscription_for_user(7, conn=conn, cur=cursor)

        self.assertEqual(created["plan_name"], "free")
        self.assertEqual(created["monthly_transaction_limit"], 50)

    def test_subscription_limits_route_returns_free(self):
        token = self._make_token(1)

        with patch(
            "backend.api.routes.subscriptions.get_user_plan_limits",
            return_value={
                "plan_name": "free",
                "monthly_transaction_limit": 50,
                "is_pro": False,
                "status": "active",
            },
        ), patch(
            "backend.api.routes.subscriptions.check_transaction_limit",
            return_value={"allowed": True, "current_count": 10, "limit": 50, "plan": "free"},
        ):
            response = self.client.get(
                "/api/subscription/limits",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["plan_name"], "free")
        self.assertEqual(body["monthly_transaction_limit"], 50)
        self.assertEqual(body["current_count"], 10)

    def test_subscription_limits_route_returns_pro(self):
        token = self._make_token(1)

        with patch(
            "backend.api.routes.subscriptions.get_user_plan_limits",
            return_value={
                "plan_name": "pro",
                "monthly_transaction_limit": None,
                "is_pro": True,
                "status": "active",
            },
        ), patch(
            "backend.api.routes.subscriptions.check_transaction_limit",
            return_value={"allowed": True, "current_count": 120, "limit": None, "plan": "pro"},
        ):
            response = self.client.get(
                "/api/subscription/limits",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["plan_name"], "pro")
        self.assertIsNone(body["monthly_transaction_limit"])

    def test_create_transaction_is_blocked_when_free_limit_is_reached(self):
        token = self._make_token(1)

        with patch(
            "backend.api.middlewares.plan_limit.check_transaction_limit",
            return_value={"allowed": False, "current_count": 50, "limit": 50, "plan": "free"},
        ):
            response = self.client.post(
                "/api/transaction/create",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "id_operacao": 1,
                    "valor_transacao": 10,
                    "descricao_transacao": "Teste bloqueio",
                },
            )

        self.assertEqual(response.status_code, 403)
        body = response.get_json()
        self.assertEqual(body["error"], "transaction_limit_reached")
        self.assertEqual(body["limit"], 50)


if __name__ == "__main__":
    unittest.main()
