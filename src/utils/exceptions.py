"""Domain-specific exception hierarchy. All app errors derive from LLMForgeError."""
from __future__ import annotations


class LLMForgeError(Exception):
    """Base exception."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str = "", *, detail: dict | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        self.message = message
        self.detail = detail or {}


class ValidationError(LLMForgeError):
    status_code = 422
    error_code = "validation_error"


class AuthError(LLMForgeError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(LLMForgeError):
    status_code = 403
    error_code = "forbidden"


class NotFoundError(LLMForgeError):
    status_code = 404
    error_code = "not_found"


class RateLimitError(LLMForgeError):
    status_code = 429
    error_code = "rate_limited"


class QuotaExceededError(LLMForgeError):
    status_code = 402
    error_code = "quota_exceeded"


class SafetyError(LLMForgeError):
    status_code = 400
    error_code = "safety_violation"


class EngineNotReadyError(LLMForgeError):
    status_code = 503
    error_code = "engine_not_ready"


class UpstreamTimeoutError(LLMForgeError):
    status_code = 504
    error_code = "upstream_timeout"


class CircuitOpenError(LLMForgeError):
    status_code = 503
    error_code = "circuit_open"
