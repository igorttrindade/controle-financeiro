import datetime
import unittest
from unittest.mock import patch

import jwt

from backend.app import app
from backend.api.routes import users
from backend.api.security.token_store import clear_revocations


class FakeCursor:
    def __init__(self, fetchone_values=None, fetchall_value=None, rowcount_sequence=None):
        self._fetchone_values = list(fetchone_values or [])
        self._fetchall_value = fetchall_value or []
        self._rowcount_sequence = list(rowcount_sequence or [])
        self.rowcount = self._rowcount_sequence[0] if self._rowcount_sequence else 1
        self.execute_calls = []

    def execute(self, query, params=None):
        self.execute_calls.append((query, params))
        if self._rowcount_sequence:
            self.rowcount = self._rowcount_sequence.pop(0)

    def fetchone(self):
        if self._fetchone_values:
            return self._fetchone_values.pop(0)
        return None

    def fetchall(self):
        return self._fetchall_value

    def close(self):
        return None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class APIMinimumTests(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key-with-at-least-32-bytes",
            JWT_ISSUER="test-issuer",
            JWT_AUDIENCE="test-audience",
        )
        clear_revocations()
        self.client = app.test_client()

    def _make_token(self, user_id):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "jti": "test-jti",
            "iat": now,
            "nbf": now,
            "exp": now + datetime.timedelta(hours=1),
            "iss": app.config["JWT_ISSUER"],
            "aud": app.config["JWT_AUDIENCE"],
        }
        return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

    def test_register_success(self):
        cursor = FakeCursor(fetchone_values=[(1,)])
        conn = FakeConnection(cursor)

        with patch("backend.api.routes.users.get_db_connection", return_value=conn), patch(
            "backend.api.routes.users.ensure_free_subscription_for_user", return_value={"id_user": 1}
        ):
            response = self.client.post(
                "/api/users/register",
                json={
                    "name_user": "Igor",
                    "email_user": "igor@example.com",
                    "dt_nascimento_user": "2000-01-01",
                    "tel_user": "11999999999",
                    "password": "Senha@123",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(conn.committed)

    def test_login_success_returns_token(self):
        password_hash = users.bcrypt.generate_password_hash("Senha@123").decode("utf-8")
        cursor = FakeCursor(fetchone_values=[(1, "igor@example.com", password_hash)])
        conn = FakeConnection(cursor)

        with patch("backend.api.routes.users.get_db_connection", return_value=conn):
            response = self.client.post(
                "/api/users/login",
                json={"email_user": "igor@example.com", "password": "Senha@123"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn("token", body)
        self.assertEqual(body["user_id"], 1)

    def test_transactions_require_authentication(self):
        response = self.client.post("/api/transaction/create", json={"id_operacao": 1})
        self.assertEqual(response.status_code, 401)

    def test_create_transaction_success(self):
        cursor = FakeCursor(fetchone_values=[(1,), (42,)])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn), patch(
            "backend.api.middlewares.plan_limit.check_transaction_limit",
            return_value={"allowed": True, "current_count": 1, "limit": 50, "plan": "free"},
        ):
            response = self.client.post(
                "/api/transaction/create",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "id_operacao": 3,
                    "valor_transacao": 100.5,
                    "descricao_transacao": "Compra de mercado",
                    "dt_transacao": "2026-02-25T14:30:00",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id_transacao"], 42)
        self.assertTrue(conn.committed)

    def test_create_transaction_forbidden_if_operation_not_owned(self):
        cursor = FakeCursor(fetchone_values=[None])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn), patch(
            "backend.api.middlewares.plan_limit.check_transaction_limit",
            return_value={"allowed": True, "current_count": 1, "limit": 50, "plan": "free"},
        ):
            response = self.client.post(
                "/api/transaction/create",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "id_operacao": 999,
                    "valor_transacao": 80,
                    "descricao_transacao": "Conta de luz",
                },
            )

        self.assertEqual(response.status_code, 403)

    def test_create_transaction_requires_description(self):
        token = self._make_token(1)
        with patch(
            "backend.api.middlewares.plan_limit.check_transaction_limit",
            return_value={"allowed": True, "current_count": 1, "limit": 50, "plan": "free"},
        ):
            response = self.client.post(
                "/api/transaction/create",
                headers={"Authorization": f"Bearer {token}"},
                json={"id_operacao": 1, "valor_transacao": 10},
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("descrição", response.get_json()["error"].lower())

    def test_create_operation_success(self):
        cursor = FakeCursor(fetchone_values=[None, (10, "Freela", "entrada")])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn):
            response = self.client.post(
                "/api/transaction/operations",
                headers={"Authorization": f"Bearer {token}"},
                json={"nome_operacao": "Freela", "tipo_operacao": "entrada"},
            )

        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body["id_operacao"], 10)
        self.assertEqual(body["tipo_operacao"], "entrada")

    def test_create_operation_returns_existing(self):
        cursor = FakeCursor(fetchone_values=[(7, "Salário", "entrada")])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn):
            response = self.client.post(
                "/api/transaction/operations",
                headers={"Authorization": f"Bearer {token}"},
                json={"nome_operacao": "Salário", "tipo_operacao": "entrada"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id_operacao"], 7)

    def test_get_transaction_by_id_success(self):
        cursor = FakeCursor(
            fetchone_values=[
                (5, 2, "2026-02-25 14:30:00", "Mercado", 149.90, "despesa", "Compra mensal"),
            ]
        )
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn):
            response = self.client.get(
                "/api/transaction/5",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id_operacao"], 2)

    def test_update_transaction_forbidden_if_operation_not_owned(self):
        cursor = FakeCursor(fetchone_values=[(1,), None])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.transactions.get_db_connection", return_value=conn):
            response = self.client.put(
                "/api/transaction/5",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "id_operacao": 999,
                    "valor_transacao": 200,
                    "descricao_transacao": "Ajuste",
                },
            )

        self.assertEqual(response.status_code, 403)

    def test_delete_user_forbidden_for_another_user(self):
        token = self._make_token(1)

        response = self.client.delete(
            "/api/users/2",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "Senha@123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("Acesso negado", response.get_json()["error"])

    def test_delete_user_success_for_owner(self):
        password_hash = users.bcrypt.generate_password_hash("Senha@123").decode("utf-8")
        cursor = FakeCursor(fetchone_values=[(password_hash,)], rowcount_sequence=[1, 1])
        conn = FakeConnection(cursor)
        token = self._make_token(1)

        with patch("backend.api.routes.users.get_db_connection", return_value=conn):
            response = self.client.delete(
                "/api/users/1",
                headers={"Authorization": f"Bearer {token}"},
                json={"password": "Senha@123"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(conn.committed)

    def test_logout_revokes_token(self):
        token = self._make_token(1)

        logout_response = self.client.post(
            "/api/users/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(logout_response.status_code, 200)

        denied_response = self.client.get(
            "/api/transaction/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(denied_response.status_code, 401)
        self.assertIn("revogado", denied_response.get_json()["message"].lower())


if __name__ == "__main__":
    unittest.main()
