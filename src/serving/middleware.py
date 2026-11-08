"""Security middleware: API-key auth, rate limit, size cap, headers."""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.utils.logger import get_logger
from src.utils.security import verify_api_key

log = get_logger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Requires `Authorization: Bearer <API_KEY>` on protected paths."""

    PROTECTED = ("/generate", "/v1/")

    def __init__(self, app, api_key: str | None = None) -> None:
        super().__init__(app)
        self._expected = api_key or os.getenv("API_KEY", "")
        if not self._expected or len(self._expected) < 32:
            raise RuntimeError("API_KEY must be set and >=32 chars")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not any(request.url.path.startswith(p) for p in self.PROTECTED):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else None
        if not verify_api_key(token, self._expected):
            log.warning("auth_failed", path=request.url.path, ip=request.client.host if request.client else "unknown")
            return JSONResponse({"detail": "unauthorized"}, status_code=401)

        return await call_next(request)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 1_048_576) -> None:
        super().__init__(app)
        self._max = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        cl = request.headers.get("content-length")
        if cl and int(cl) > self._max:
            return JSONResponse({"detail": "request too large"}, status_code=413)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        resp.headers["Cache-Control"] = "no-store"
        return resp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-process sliding-window rate limiter (per-IP).

    For multi-replica deployments, swap the store for Redis (see REDIS_URL).
    """

    def __init__(self, app, limit_per_minute: int = 60) -> None:
        super().__init__(app)
        self._limit = limit_per_minute
        self._window = 60.0
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        dq = self._hits[ip]
        while dq and now - dq[0] > self._window:
            dq.popleft()
        if len(dq) >= self._limit:
            retry = max(1, int(self._window - (now - dq[0])))
            return JSONResponse(
                {"detail": "rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
        dq.append(now)
        return await call_next(request)
