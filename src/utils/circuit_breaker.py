"""Async circuit breaker with half-open probe."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TypeVar

from src.utils.exceptions import CircuitOpenError
from src.utils.logger import get_logger

T = TypeVar("T")
log = get_logger(__name__)


class State(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = State.CLOSED
        self._failures = 0
        self._opened_at = 0.0
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> State:
        return self._state

    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        async with self._lock:
            if self._state is State.OPEN:
                if time.monotonic() - self._opened_at >= self.recovery_timeout:
                    self._state = State.HALF_OPEN
                    self._half_open_calls = 0
                    log.info("circuit_half_open", name=self.name)
                else:
                    raise CircuitOpenError(f"circuit_open:{self.name}")
            if self._state is State.HALF_OPEN and self._half_open_calls >= self.half_open_max_calls:
                raise CircuitOpenError(f"circuit_open:{self.name}")
            if self._state is State.HALF_OPEN:
                self._half_open_calls += 1

        try:
            result = await fn()
        except Exception:
            await self._record_failure()
            raise
        await self._record_success()
        return result

    async def _record_success(self) -> None:
        async with self._lock:
            self._failures = 0
            if self._state is not State.CLOSED:
                log.info("circuit_closed", name=self.name)
            self._state = State.CLOSED

    async def _record_failure(self) -> None:
        async with self._lock:
            self._failures += 1
            if self._state is State.HALF_OPEN or self._failures >= self.failure_threshold:
                self._state = State.OPEN
                self._opened_at = time.monotonic()
                log.warning("circuit_opened", name=self.name, failures=self._failures)
