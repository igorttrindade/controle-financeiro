import datetime
import unittest
from decimal import Decimal
from unittest.mock import patch

import jwt

from backend.app import app
from backend.api.security.token_store import clear_revocations
from backend.services.cache import cache_backend
from backend.services.cache.memory_cache import MemoryCache


class DashboardCursorFake:
    def __init__(self, transactions_rows=None, goal_row=(None,)):
        self.transactions_rows = transactions_rows or []
        self.goal_row = goal_row
        self.last_query = ""

    def execute(self, query, params=None):
        self.last_query = query

    def fetchall(self):
        if "FROM tb_transacoes" in self.last_query:
            return self.transactions_rows
        return []

    def fetchone(self):
        if "FROM tb_user_profile" in self.last_query:
            return self.goal_row
        return None

    def close(self):
        return None


class DashboardConnectionFake:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def close(self):
        return None


class TransactionCursorFake:
    def __init__(self, fetchone_values=None):
        self._fetchone_values = list(fetchone_values or [])

    def execute(self, query, params=None):
        return None

    def fetchone(self):
        if self._fetchone_values:
            return self._fetchone_values.pop(0)
        return None

    def close(self):
        return None


class TransactionConnectionFake:
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


class CacheLayerTests(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key-with-at-least-32-bytes",
            JWT_ISSUER="test-issuer",
            JWT_AUDIENCE="test-audience",
        )
        clear_revocations()
        cache_backend.delete_pattern("")
        self.client = app.test_client()

    def _make_token(self, user_id=1):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "jti": f"test-cache-jti-{user_id}",
            "iat": now,
            "nbf": now,
            "exp": now + datetime.timedelta(hours=1),
            "iss": app.config["JWT_ISSUER"],
            "aud": app.config["JWT_AUDIENCE"],
        }
        return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

    def test_cache_hit(self):
        token = self._make_token(1)
        payload = {
            "period": "2026-03",
            "totals": {"total_income": 100.0, "total_expense": 50.0, "balance": 50.0},
            "projection": {"meta_value": 1000.0, "projected_total": 200.0, "category_breakdown": []},
            "recommendations": [],
            "natural_summary": "Resumo do cache",
        }
        cache_backend.set("dashboard:1:2026-03", payload, 900)

        with patch("backend.api.routes.dashboard.get_db_connection") as mocked_db:
            response = self.client.get(
                "/api/dashboard/intelligent-summary?month=2026-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), payload)
        mocked_db.assert_not_called()

    def test_cache_miss(self):
        token = self._make_token(1)
        rows = [
            ("Salario", "entrada", Decimal("2500.00"), datetime.datetime(2026, 3, 2, 10, 0, 0)),
            ("Mercado", "despesa", Decimal("300.00"), datetime.datetime(2026, 3, 3, 10, 0, 0)),
        ]
        conn = DashboardConnectionFake(
            DashboardCursorFake(transactions_rows=rows, goal_row=(Decimal("1800.00"),))
        )

        with patch("backend.api.routes.dashboard.get_db_connection", return_value=conn):
            with patch("backend.api.routes.dashboard.cache_backend.set") as mocked_set:
                response = self.client.get(
                    "/api/dashboard/intelligent-summary?month=2026-03",
                    headers={"Authorization": f"Bearer {token}"},
                )

        self.assertEqual(response.status_code, 200)
        mocked_set.assert_called_once()
        _, _, ttl_seconds = mocked_set.call_args.args
        self.assertEqual(ttl_seconds, 900)

    def test_ttl_expiration(self):
        cache = MemoryCache()

        with patch("backend.services.cache.memory_cache.time.time", return_value=1000.0):
            cache.set("k1", {"value": 1}, 1)

        with patch("backend.services.cache.memory_cache.time.time", return_value=1002.0):
            cached = cache.get("k1")

        self.assertIsNone(cached)

    def test_delete_pattern(self):
        cache = MemoryCache()
        cache.set("dashboard:1:2026-03", {"a": 1}, 900)
        cache.set("dashboard:1:2026-04", {"a": 2}, 900)
        cache.set("dashboard:2:2026-03", {"a": 3}, 900)

        cache.delete_pattern("dashboard:1:*")

        self.assertIsNone(cache.get("dashboard:1:2026-03"))
        self.assertIsNone(cache.get("dashboard:1:2026-04"))
        self.assertEqual(cache.get("dashboard:2:2026-03"), {"a": 3})

    def test_invalidation_after_transaction_change(self):
        token = self._make_token(1)
        cache_backend.set(
            "dashboard:1:2026-03",
            {
                "period": "2026-03",
                "totals": {"total_income": 0.0, "total_expense": 0.0, "balance": 0.0},
                "projection": {"meta_value": None, "projected_total": 0.0, "category_breakdown": []},
                "recommendations": [],
                "natural_summary": "stale",
            },
            900,
        )

        cursor = TransactionCursorFake(fetchone_values=[(1,), (55,)])
        conn = TransactionConnectionFake(cursor)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn), patch(
            "backend.api.middlewares.plan_limit.check_transaction_limit",
            return_value={"allowed": True, "current_count": 1, "limit": 50, "plan": "free"},
        ):
            response = self.client.post(
                "/api/transaction/create",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "id_operacao": 10,
                    "valor_transacao": 120.5,
                    "descricao_transacao": "Teste de invalidacao",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(conn.committed)
        self.assertIsNone(cache_backend.get("dashboard:1:2026-03"))


if __name__ == "__main__":
    unittest.main()
