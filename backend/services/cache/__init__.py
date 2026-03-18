from .memory_cache import MemoryCache

cache_backend = MemoryCache()

__all__ = ["cache_backend", "MemoryCache"]
