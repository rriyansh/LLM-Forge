"""Structured JSON logging with PII scrubbing, correlation IDs, and audit trail."""
from __future__ import annotations

import logging
import os
import re
import sys
from contextvars import ContextVar
from typing import Any

import structlog

# ---------- Correlation context ----------
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")

_SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization:\s*bearer\s+)[\w\-\.]+"), r"\1[REDACTED]"),
    (re.compile(r'(?i)("?(?:api[_-]?key|token|password|secret)"?\s*[:=]\s*)["\']?[\w\-\.]+["\']?'), r"\1[REDACTED]"),
    (re.compile(r"(?i)(hf_)[A-Za-z0-9]{20,}"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(sk-)[A-Za-z0-9]{20,}"), r"\1[REDACTED]"),
]


def _scrub(value: str) -> str:
    if not isinstance(value, str):
        return value
    for pat, repl in _SECRET_PATTERNS:
        value = pat.sub(repl, value)
    return value


def _add_context(logger: Any, method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    event_dict["request_id"] = request_id_var.get()
    event_dict["user_id"] = user_id_var.get()
    return event_dict


def _scrub_processor(logger: Any, method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    for k, v in list(event_dict.items()):
        if isinstance(v, str):
            event_dict[k] = _scrub(v)
    return event_dict


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)
    # Silence noisy libs
    for noisy in ("uvicorn.access", "httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_context,
            _scrub_processor,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


class AuditLogger:
    """Separate channel for audit events (auth, quota, admin actions).

    In production, ship to a WORM (write-once-read-many) backend.
    """

    def __init__(self) -> None:
        self._log = get_logger("audit")

    def auth_success(self, *, user_id: str, method: str, ip: str, path: str) -> None:
        self._log.info("auth_success", user_id=user_id, method=method, ip=ip, path=path)

    def auth_failure(self, *, reason: str, ip: str, path: str) -> None:
        self._log.warning("auth_failure", reason=reason, ip=ip, path=path)

    def quota_exceeded(self, *, user_id: str, tier: str, metric: str) -> None:
        self._log.warning("quota_exceeded", user_id=user_id, tier=tier, metric=metric)

    def safety_blocked(self, *, user_id: str, reason: str, category: str) -> None:
        self._log.warning("safety_blocked", user_id=user_id, reason=reason, category=category)

    def admin_action(self, *, user_id: str, action: str, target: str) -> None:
        self._log.info("admin_action", user_id=user_id, action=action, target=target)


audit = AuditLogger()
