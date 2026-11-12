"""Redis-backed sliding-window rate limiter with local in-memory fallback.

Uses a sorted set per key with scores = timestamps. O(log N) per op.
"""
from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from typing import Protocol

from src.utils.config_parser import get_env
from src.utils.logger import get_logger

log = get_logger(__name__)


class RateLimiter(Protocol):
    async def allow(self, key: str, *, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        ...


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def allow(self, key: str, *, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        dq = self._hits[key]
        while dq and now - dq[0] > window_seconds:
            dq.popleft()
        if len(dq) >= limit:
            retry = max(1, int(window_seconds - (now - dq[0])))
            return False, retry
        dq.append(now)
        return True, 0


class RedisRateLimiter:
    """Distributed sliding-window. Multi-replica safe."""

    def __init__(self, redis_client) -> None:  # redis.asyncio.Redis
        self._r = redis_client

    async def allow(self, key: str, *, limit: int, window_seconds: int) -> tuple[bool, int]:
        now_ms = int(time.time() * 1000)
        cutoff = now_ms - window_seconds * 1000
        redis_key = f"rl:{key}"
        pipe = self._r.pipeline()
        pipe.zremrangebyscore(redis_key, 0, cutoff)
        pipe.zadd(redis_key, {f"{now_ms}-{uuid.uuid4().hex[:8]}": now_ms})
        pipe.zcard(redis_key)
        pipe.expire(redis_key, window_seconds + 1)
        _, _, count, _ = await pipe.execute()

        if count > limit:
            # Over limit → remove the one we just added & compute retry
            oldest = await self._r.zrange(redis_key, 0, 0, withscores=True)
            retry = 1
            if oldest:
                retry = max(1, int(window_seconds - (now_ms - int(oldest[0][1])) / 1000))
            return False, retry
        return True, 0


_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is not None:
        return _limiter
    url = get_env("REDIS_URL", "")
    if url:
        try:
            import redis.asyncio as redis  # type: ignore

            client = redis.from_url(url, encoding="utf-8", decode_responses=True)
            _limiter = RedisRateLimiter(client)
            log.info("rate_limiter", backend="redis")
            return _limiter
        except Exception as e:  # noqa: BLE001
            log.warning("redis_unavailable_falling_back", error=str(e))
    _limiter = InMemoryRateLimiter()
    log.info("rate_limiter", backend="memory")
    return _limiter
