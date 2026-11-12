"""Async retry with exponential backoff + jitter."""
from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 5.0,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    last_exc: BaseException | None = None
    for i in range(attempts):
        try:
            return await fn()
        except retry_on as e:
            last_exc = e
            if i == attempts - 1:
                break
            delay = min(max_delay, base_delay * (2**i))
            delay *= 0.5 + random.random()  # jitter
            await asyncio.sleep(delay)
    assert last_exc is not None
    raise last_exc
