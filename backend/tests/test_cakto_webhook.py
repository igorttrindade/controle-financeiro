import unittest
from unittest.mock import patch

from backend.app import app


class CaktoWebhookTests(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            CAKTO_WEBHOOK_SECRET='test-cakto-secret',
        )
        self.client = app.test_client()

    def _payload(self, event='purchase_approved', email='cliente@email.com'):
        return {
            'event': event,
            'secret': app.config['CAKTO_WEBHOOK_SECRET'],
            'data': {
                'id': 'order-123',
                'customer': {
                    'email': email,
                },
            },
        }

    def test_purchase_approved_valid_email_upgrades_user_and_logs_processed(self):
        with patch(
            'backend.api.routes.subscriptions.get_user_by_email',
            return_value={'id_user': 7, 'email_user': 'cliente@email.com'},
        ), patch(
            'backend.api.routes.subscriptions.upgrade_to_pro',
            return_value={'plan_name': 'pro'},
        ) as upgrade_mock, patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post('/api/subscription/webhook', json=self._payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')
        upgrade_mock.assert_called_once_with(
            7,
            gateway='cakto',
            gateway_subscription_id='order-123',
            gateway_customer_id='cliente@email.com',
        )
        self.assertEqual(log_mock.call_args.kwargs['status'], 'processed')

    def test_purchase_approved_user_not_found_returns_200_and_logs_user_not_found(self):
        with patch(
            'backend.api.routes.subscriptions.get_user_by_email',
            return_value=None,
        ), patch(
            'backend.api.routes.subscriptions.upgrade_to_pro'
        ) as upgrade_mock, patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post('/api/subscription/webhook', json=self._payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')
        upgrade_mock.assert_not_called()
        self.assertEqual(log_mock.call_args.kwargs['status'], 'user_not_found')

    def test_refund_downgrades_to_free(self):
        with patch(
            'backend.api.routes.subscriptions.get_user_by_email',
            return_value={'id_user': 9, 'email_user': 'cliente@email.com'},
        ), patch(
            'backend.api.routes.subscriptions.downgrade_to_free'
        ) as downgrade_mock, patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post(
                '/api/subscription/webhook',
                json=self._payload(event='refund'),
            )

        self.assertEqual(response.status_code, 200)
        downgrade_mock.assert_called_once_with(9)
        self.assertEqual(log_mock.call_args.kwargs['status'], 'processed')

    def test_chargeback_downgrades_to_free(self):
        with patch(
            'backend.api.routes.subscriptions.get_user_by_email',
            return_value={'id_user': 11, 'email_user': 'cliente@email.com'},
        ), patch(
            'backend.api.routes.subscriptions.downgrade_to_free'
        ) as downgrade_mock, patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post(
                '/api/subscription/webhook',
                json=self._payload(event='chargeback'),
            )

        self.assertEqual(response.status_code, 200)
        downgrade_mock.assert_called_once_with(11)
        self.assertEqual(log_mock.call_args.kwargs['status'], 'processed')

    def test_subscription_canceled_marks_canceled(self):
        with patch(
            'backend.api.routes.subscriptions.get_user_by_email',
            return_value={'id_user': 13, 'email_user': 'cliente@email.com'},
        ), patch(
            'backend.api.routes.subscriptions.cancel_subscription'
        ) as cancel_mock, patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post(
                '/api/subscription/webhook',
                json=self._payload(event='subscription_canceled'),
            )

        self.assertEqual(response.status_code, 200)
        cancel_mock.assert_called_once_with(13, at_period_end=False)
        self.assertEqual(log_mock.call_args.kwargs['status'], 'processed')

    def test_unknown_event_is_ignored(self):
        with patch(
            'backend.api.routes.subscriptions._insert_webhook_log'
        ) as log_mock:
            response = self.client.post(
                '/api/subscription/webhook',
                json=self._payload(event='other_event'),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ignored')
        self.assertEqual(response.get_json()['event'], 'other_event')
        self.assertEqual(log_mock.call_args.kwargs['status'], 'ignored')

    def test_invalid_secret_returns_401(self):
        payload = self._payload()
        payload['fields'] = {'secret': 'invalid'}
        payload['secret'] = 'invalid'

        with patch('backend.api.routes.subscriptions._insert_webhook_log') as log_mock:
            response = self.client.post('/api/subscription/webhook', json=payload)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['error'], 'invalid_webhook_secret')
        log_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
