import datetime
from threading import Lock


_LOCK = Lock()
_REVOKED_JTIS = {}


def _to_timestamp(exp):
    if isinstance(exp, datetime.datetime):
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=datetime.timezone.utc)
        return exp.timestamp()
    return float(exp)


def revoke_jti(jti, exp):
    expires_at = _to_timestamp(exp)
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if expires_at <= now:
        return

    with _LOCK:
        _prune_locked(now)
        _REVOKED_JTIS[jti] = expires_at


def is_jti_revoked(jti):
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    with _LOCK:
        _prune_locked(now)
        return jti in _REVOKED_JTIS


def _prune_locked(now_ts):
    expired = [token_jti for token_jti, exp_ts in _REVOKED_JTIS.items() if exp_ts <= now_ts]
    for token_jti in expired:
        _REVOKED_JTIS.pop(token_jti, None)


def clear_revocations():
    with _LOCK:
        _REVOKED_JTIS.clear()
