import datetime
import unittest
from decimal import Decimal
from unittest.mock import patch

import jwt

from backend.app import app
from backend.api.security.token_store import clear_revocations
from backend.services.cache import cache_backend


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
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


class DashboardIntelligentSummaryTests(unittest.TestCase):
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
            "jti": "test-jti-dashboard",
            "iat": now,
            "nbf": now,
            "exp": now + datetime.timedelta(hours=1),
            "iss": app.config["JWT_ISSUER"],
            "aud": app.config["JWT_AUDIENCE"],
        }
        return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

    def test_month_with_data(self):
        rows = [
            ("Salario", "entrada", Decimal("4000.00"), datetime.datetime(2026, 3, 2, 10, 0, 0)),
            ("Mercado", "despesa", Decimal("800.00"), datetime.datetime(2026, 3, 3, 12, 0, 0)),
            ("Aluguel", "despesa", Decimal("1200.00"), datetime.datetime(2026, 3, 5, 12, 0, 0)),
        ]
        conn = DashboardConnectionFake(DashboardCursorFake(transactions_rows=rows, goal_row=(Decimal("3500.00"),)))
        token = self._make_token()

        with patch("backend.api.routes.dashboard.get_db_connection", return_value=conn):
            response = self.client.get(
                "/api/dashboard/intelligent-summary?month=2026-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["period"], "2026-03")
        self.assertEqual(body["totals"]["total_income"], 4000.0)
        self.assertEqual(body["totals"]["total_expense"], 2000.0)
        self.assertEqual(body["totals"]["balance"], 2000.0)
        self.assertIn("projection", body)
        self.assertIn("recommendations", body)
        self.assertIn("natural_summary", body)

    def test_month_without_data(self):
        conn = DashboardConnectionFake(DashboardCursorFake(transactions_rows=[], goal_row=(Decimal("1500.00"),)))
        token = self._make_token()

        with patch("backend.api.routes.dashboard.get_db_connection", return_value=conn):
            response = self.client.get(
                "/api/dashboard/intelligent-summary?month=2026-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["totals"]["total_income"], 0.0)
        self.assertEqual(body["totals"]["total_expense"], 0.0)
        self.assertEqual(body["totals"]["balance"], 0.0)
        self.assertEqual(body["recommendations"], [])

    def test_without_meta_defined(self):
        rows = [
            ("Mercado", "despesa", Decimal("450.00"), datetime.datetime(2026, 3, 10, 8, 0, 0)),
        ]
        conn = DashboardConnectionFake(DashboardCursorFake(transactions_rows=rows, goal_row=(None,)))
        token = self._make_token()

        with patch("backend.api.routes.dashboard.get_db_connection", return_value=conn):
            response = self.client.get(
                "/api/dashboard/intelligent-summary?month=2026-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIsNone(body["projection"]["meta_value"])

    def test_with_multiple_recommendations(self):
        rows = [
            ("Salario", "entrada", Decimal("5000.00"), datetime.datetime(2026, 3, 2, 10, 0, 0)),
            ("Moradia", "despesa", Decimal("1600.00"), datetime.datetime(2026, 3, 3, 10, 0, 0)),
            ("Lazer", "despesa", Decimal("1400.00"), datetime.datetime(2026, 3, 4, 10, 0, 0)),
        ]
        conn = DashboardConnectionFake(DashboardCursorFake(transactions_rows=rows, goal_row=(Decimal("2000.00"),)))
        token = self._make_token()

        with patch("backend.api.routes.dashboard.get_db_connection", return_value=conn):
            response = self.client.get(
                "/api/dashboard/intelligent-summary?month=2026-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()

        recommendation_types = [item["type"] for item in body["recommendations"]]
        self.assertIn("meta_alert", recommendation_types)
        self.assertIn("category_dominance", recommendation_types)
        self.assertGreaterEqual(len(body["recommendations"]), 2)


if __name__ == "__main__":
    unittest.main()
