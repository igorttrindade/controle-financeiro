from __future__ import annotations

from abc import ABC, abstractmethod


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> dict | None:
        """Return cached value or None when absent/expired."""

    @abstractmethod
    def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        """Store value with a time-to-live in seconds."""

    @abstractmethod
    def delete_pattern(self, pattern: str) -> None:
        """Delete keys matching a prefix pattern."""
