"""Model warmup to reduce first-request latency."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.utils.logger import get_logger

if TYPE_CHECKING:
    from src.serving.engine import LLMEngine

log = get_logger(__name__)

WARMUP_PROMPTS = [
    "Hello, how are you?",
    "What is 2 + 2?",
]


async def warmup(engine: LLMEngine, rounds: int = 2) -> None:
    for _ in range(rounds):
        for p in WARMUP_PROMPTS:
            try:
                await engine.generate(
                    p, temperature=0.0, top_p=1.0, max_tokens=8, stop=[]
                )
            except Exception as e:  # noqa: BLE001
                log.warning("warmup_failed", error=str(e))
        await asyncio.sleep(0.1)
    log.info("warmup_complete", rounds=rounds)
