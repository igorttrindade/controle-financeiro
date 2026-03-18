from __future__ import annotations

import time
from threading import Lock

from .base import CacheBackend


class MemoryCache(CacheBackend):
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._lock = Lock()

    def get(self, key: str) -> dict | None:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None

            if entry["expires_at"] <= now:
                self._store.pop(key, None)
                return None

            return entry["value"]

    def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        ttl = max(0, int(ttl_seconds))
        expires_at = time.time() + ttl
        with self._lock:
            self._store[key] = {"value": value, "expires_at": expires_at}

    def delete_pattern(self, pattern: str) -> None:
        prefix = pattern[:-1] if pattern.endswith("*") else pattern
        with self._lock:
            keys_to_remove = [key for key in self._store if key.startswith(prefix)]
            for key in keys_to_remove:
                self._store.pop(key, None)
