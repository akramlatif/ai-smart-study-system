"""
Redis client — falls back to an in-memory dict when USE_MEMORY_CACHE=True.
This lets the app run without a Redis server for local development.
"""
import json
import time
from typing import Any

SESSION_TTL_SECONDS = 7200  # 2 hours


class _MemoryCache:
    """Minimal Redis-compatible in-memory cache (get/setex/delete)."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}  # key -> (value, expires_at)

    async def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def aclose(self) -> None:
        pass


_cache_instance: Any = None


async def get_redis() -> Any:
    global _cache_instance
    if _cache_instance is None:
        try:
            from app.core.config import settings
            if settings.USE_MEMORY_CACHE:
                raise ImportError("memory cache requested")
            import redis.asyncio as aioredis
            _cache_instance = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
        except Exception:
            _cache_instance = _MemoryCache()
    return _cache_instance


async def close_redis() -> None:
    global _cache_instance
    if _cache_instance is not None:
        await _cache_instance.aclose()
        _cache_instance = None
