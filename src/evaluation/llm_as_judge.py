"""LLM-as-judge evaluation with retries, validation, and structured output.

Uses OpenAI-compatible endpoint; pluggable for local judge models too.
"""
from __future__ import annotations

import json
import os
from typing import Any

from src.utils.logger import get_logger
from src.utils.retry import retry_async

log = get_logger(__name__)

JUDGE_SYSTEM = (
    "You are a strict, fair evaluator. Given a prompt and a response, "
    "rate the response from 1 (very poor) to 5 (excellent) on each criterion. "
    "Return ONLY valid JSON with keys equal to the criteria and integer values."
)


async def _call_judge(prompt: str, response: str, criteria: list[str], model: str) -> dict[str, int]:
    """Call OpenAI-compatible API. Wire your client here."""
    import httpx

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("JUDGE_API_KEY")
    base = os.getenv("JUDGE_API_BASE", "https://api.openai.com/v1")
    if not api_key:
        log.warning("judge_no_api_key")
        return {c: 0 for c in criteria}

    user_msg = (
        f"Prompt:\n{prompt}\n\nResponse:\n{response}\n\n"
        f"Criteria: {criteria}. Return JSON."
    )
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            },
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content)


async def judge_one(prompt: str, response: str, criteria: list[str], model: str) -> dict[str, int]:
    return await retry_async(
        lambda: _call_judge(prompt, response, criteria, model), attempts=3, base_delay=0.5
    )


async def judge_batch(
    examples: list[dict[str, Any]], criteria: list[str], model: str, concurrency: int = 4
) -> dict[str, float]:
    import asyncio

    sem = asyncio.Semaphore(concurrency)
    scores: list[dict[str, int]] = []

    async def _one(ex: dict) -> None:
        async with sem:
            try:
                s = await judge_one(ex["prompt"], ex["response"], criteria, model)
                scores.append(s)
            except Exception as e:  # noqa: BLE001
                log.warning("judge_failed", error=str(e))

    await asyncio.gather(*(_one(ex) for ex in examples))
    if not scores:
        return {c: 0.0 for c in criteria}
    return {c: sum(s.get(c, 0) for s in scores) / len(scores) for c in criteria}
