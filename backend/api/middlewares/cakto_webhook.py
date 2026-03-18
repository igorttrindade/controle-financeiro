import hmac
from functools import wraps

from flask import current_app, g, jsonify, request


def _extract_secret(payload):
    if not isinstance(payload, dict):
        return ''
    direct_secret = payload.get('secret')
    if direct_secret:
        return str(direct_secret)

    fields = payload.get('fields')
    if isinstance(fields, dict):
        return str(fields.get('secret') or '')
    return ''


def validate_cakto_secret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = request.get_json(silent=True) or {}
        payload_secret = _extract_secret(payload)
        expected_secret = str(current_app.config.get('CAKTO_WEBHOOK_SECRET') or '')

        if not expected_secret or not hmac.compare_digest(payload_secret, expected_secret):
            return jsonify({'error': 'invalid_webhook_secret'}), 401

        g.cakto_payload = payload
        return f(*args, **kwargs)
    return decorated
