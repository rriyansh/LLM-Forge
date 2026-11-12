"""Security middleware: auth, rate limit, body cap, security headers, IP allowlist,
correlation IDs, Prometheus metrics, and request logging.
"""
from __future__ import annotations

import os
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.utils.config_parser import get_env, get_env_bool, get_env_int
from src.utils.logger import get_logger, request_id_var, user_id_var
from src.utils.metrics import HTTP_LATENCY, HTTP_REQUESTS
from src.utils.rate_limiter import get_rate_limiter
from src.utils.security import ip_in_allowlist, verify_api_key

log = get_logger(__name__)

PUBLIC_PATHS = ("/health/live", "/health/ready", "/metrics", "/docs", "/openapi.json", "/redoc")


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        rid = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex}"
        request_id_var.set(rid)
        try:
            response = await call_next(request)
        finally:
            request_id_var.set("-")
        response.headers["X-Request-ID"] = rid
        return response


class IPAllowlistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowlist: str = "") -> None:
        super().__init__(app)
        self._allowlist = allowlist

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = _client_ip(request)
        if not ip_in_allowlist(ip, self._allowlist):
            log.warning("ip_blocked", ip=ip, path=request.url.path)
            return JSONResponse({"detail": "forbidden"}, status_code=403)
        return await call_next(request)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 1_048_576) -> None:
        super().__init__(app)
        self._max = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        cl = request.headers.get("content-length")
        if cl:
            try:
                if int(cl) > self._max:
                    return JSONResponse({"detail": "request_too_large"}, status_code=413)
            except ValueError:
                return JSONResponse({"detail": "bad_content_length"}, status_code=400)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return resp


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        ip = _client_ip(request)
        limit = get_env_int("RATE_LIMIT_PER_MINUTE", 60)
        allowed, retry = await get_rate_limiter().allow(ip, limit=limit, window_seconds=60)
        if not allowed:
            log.warning("rate_limited", ip=ip, path=request.url.path)
            from src.utils.metrics import RATE_LIMITED

            RATE_LIMITED.inc()
            return JSONResponse(
                {"detail": "rate_limit_exceeded"},
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
        return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)
        method = request.method
        path = request.url.path
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            HTTP_REQUESTS.labels(method=method, path=path, status="500").inc()
            raise
        elapsed = time.perf_counter() - start
        HTTP_REQUESTS.labels(method=method, path=path, status=str(response.status_code)).inc()
        HTTP_LATENCY.labels(method=method, path=path).observe(elapsed)
        response.headers["X-Response-Time"] = f"{elapsed * 1000:.1f}ms"
        return response


class AdminAPIKeyMiddleware(BaseHTTPMiddleware):
    """For /admin/*: strict static API_KEY required, no JWT."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else None
        expected = os.getenv("API_KEY", "")
        if not verify_api_key(token, expected):
            log.warning("admin_auth_failed", ip=_client_ip(request))
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
        return await call_next(request)


def build_middleware_stack(app, *, allowlist: str = "") -> None:
    from src.serving.middleware import (  # local import to avoid circular
        CorrelationMiddleware,
        IPAllowlistMiddleware,
        MetricsMiddleware,
        SecurityHeadersMiddleware,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=get_env_int("MAX_REQUEST_BYTES", 1_048_576))
    app.add_middleware(RateLimitMiddleware)
    if allowlist:
        app.add_middleware(IPAllowlistMiddleware, allowlist=allowlist)
    app.add_middleware(AdminAPIKeyMiddleware)
    app.add_middleware(CorrelationMiddleware)
    # Silence unused import warnings
    _ = get_env_bool
