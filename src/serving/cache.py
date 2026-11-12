"""Semantic + exact-hash response cache. Redis-backed with local fallback."""
from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict

from src.utils.config_parser import get_env, get_env_bool
from src.utils.logger import get_logger

log = get_logger(__name__)

_MAX_LOCAL = 1000


def _key(prompt: str, params: dict) -> str:
    raw = json.dumps({"p": prompt, "x": params}, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


class SemanticCache:
    """Exact-match cache on (prompt, sampling params) hash.

    Name kept for future embedding-based semantic extension; current impl is exact.
    """

    def __init__(self) -> None:
        self._enabled = get_env_bool("SEMANTIC_CACHE_ENABLED", False)
        self._ttl = int(get_env("SEMANTIC_CACHE_TTL_SECONDS", "3600"))
        self._local: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._redis = None
        if self._enabled:
            url = get_env("CACHE_REDIS_URL", "") or get_env("REDIS_URL", "")
            if url:
                try:
                    import redis.asyncio as redis  # type: ignore

                    self._redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
                    log.info("cache_backend", backend="redis")
                except Exception as e:  # noqa: BLE001
                    log.warning("cache_redis_failed", error=str(e))

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def get(self, prompt: str, params: dict) -> str | None:
        if not self._enabled:
            return None
        k = _key(prompt, params)
        if self._redis is not None:
            try:
                v = await self._redis.get(f"cache:{k}")
                return v
            except Exception:  # noqa: BLE001
                pass
        entry = self._local.get(k)
        if entry is None:
            return None
        ts, val = entry
        if time.monotonic() - ts > self._ttl:
            self._local.pop(k, None)
            return None
        return val

    async def set(self, prompt: str, params: dict, response: str) -> None:
        if not self._enabled:
            return
        k = _key(prompt, params)
        if self._redis is not None:
            try:
                await self._redis.setex(f"cache:{k}", self._ttl, response)
                return
            except Exception:  # noqa: BLE001
                pass
        self._local[k] = (time.monotonic(), response)
        while len(self._local) > _MAX_LOCAL:
            self._local.popitem(last=False)
