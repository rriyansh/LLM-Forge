"""Auth, rate limiting, and request logging middleware."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""

    def __init__(self, app: Any, api_key: str | None = None) -> None:
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if self.api_key and request.url.path not in ("/health", "/v1/health"):
            auth = request.headers.get("authorization", "")
            if auth != f"Bearer {self.api_key}":
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""

    def __init__(self, app: Any, max_requests: int = 60, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client = request.client.host if request.client else "unknown"
        now = time.time()
        window = self.clients[client]
        self.clients[client] = [t for t in window if now - t < self.window_seconds]
        if len(self.clients[client]) >= self.max_requests:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        self.clients[client].append(now)
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request logging middleware."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        print(
            f"{request.method} {request.url.path} {response.status_code} {duration:.2f}ms"
        )
        return response
