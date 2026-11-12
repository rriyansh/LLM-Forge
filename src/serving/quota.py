"""Per-tenant daily quota enforcement backed by Redis."""
from __future__ import annotations

import os
import time

from src.utils.config_parser import load_security_config
from src.utils.exceptions import QuotaExceededError
from src.utils.logger import audit, get_logger

log = get_logger(__name__)

_redis = None


def _client():
    global _redis
    if _redis is not None:
        return _redis
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    try:
        import redis.asyncio as redis  # type: ignore

        _redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
        return _redis
    except Exception:  # noqa: BLE001
        return None


async def check_and_consume(tenant: str, tier: str, *, requests: int = 1, tokens: int = 0) -> None:
    client = _client()
    if client is None:
        return  # quota not enforced when no Redis
    cfg = load_security_config().quotas
    limit = cfg.premium if tier == "premium" else cfg.default
    day = time.strftime("%Y%m%d")
    req_key = f"quota:{tenant}:{day}:req"
    tok_key = f"quota:{tenant}:{day}:tok"
    try:
        r = await client.incrby(req_key, requests)
        if r == requests:
            await client.expire(req_key, 86400)
        t = 0
        if tokens:
            t = await client.incrby(tok_key, tokens)
            if t == tokens:
                await client.expire(tok_key, 86400)
        if r > limit.requests_per_day:
            audit.quota_exceeded(user_id=tenant, tier=tier, metric="requests")
            raise QuotaExceededError("requests_per_day")
        if tokens and t > limit.tokens_per_day:
            audit.quota_exceeded(user_id=tenant, tier=tier, metric="tokens")
            raise QuotaExceededError("tokens_per_day")
    except QuotaExceededError:
        raise
    except Exception as e:  # noqa: BLE001
        log.warning("quota_check_failed", error=str(e))  # fail-open
