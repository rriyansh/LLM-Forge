"""POST /generate — safe, cached, metered."""
from __future__ import annotations

import asyncio
import time

from fastapi import APIRouter, Depends, Request

from src.serving.cache import SemanticCache
from src.serving.dependencies import get_cache, get_engine
from src.serving.engine import LLMEngine
from src.serving.quota import check_and_consume
from src.serving.schemas import GenerateRequest, GenerateResponse
from src.utils.auth import Principal, require_scopes
from src.utils.config_parser import get_env_bool
from src.utils.exceptions import SafetyError, UpstreamTimeoutError
from src.utils.logger import audit, get_logger
from src.utils.metrics import CACHE_HITS, CACHE_MISSES, GEN_LATENCY, TOKENS_IN, TOKENS_OUT
from src.utils.security import detect_prompt_injection, redact_pii, sanitize_text

log = get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    body: GenerateRequest,
    request: Request,
    principal: Principal = Depends(require_scopes("generate")),
    engine: LLMEngine = Depends(get_engine),
    cache: SemanticCache = Depends(get_cache),
) -> GenerateResponse:
    prompt = sanitize_text(body.prompt)

    if get_env_bool("ENABLE_PROMPT_INJECTION_FILTER", True) and detect_prompt_injection(prompt):
        audit.safety_blocked(user_id=principal.user_id, reason="injection", category="prompt")
        raise SafetyError("prompt_injection_detected")

    if get_env_bool("ENABLE_PII_REDACTION", True):
        prompt = redact_pii(prompt)

    await check_and_consume(principal.tenant, "default")

    params = {"temperature": body.temperature, "top_p": body.top_p, "max_tokens": body.max_tokens}
    if body.use_cache:
        cached = await cache.get(prompt, params)
        if cached is not None:
            CACHE_HITS.inc()
            return GenerateResponse(
                text=cached,
                tokens_in=0,
                tokens_out=0,
                finish_reason="cache_hit",
                request_id="cache",
                cached=True,
                model=engine.model_name,
            )
        CACHE_MISSES.inc()

    timeout = float(request.app.state.request_timeout)
    start = time.perf_counter()
    try:
        text, tin, tout, finish, rid = await asyncio.wait_for(
            engine.generate(
                prompt,
                temperature=body.temperature,
                top_p=body.top_p,
                max_tokens=body.max_tokens,
                stop=body.stop,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError as e:
        raise UpstreamTimeoutError("generation_timeout") from e

    GEN_LATENCY.observe(time.perf_counter() - start)
    TOKENS_IN.labels(tenant=principal.tenant, model=engine.model_name).inc(tin)
    TOKENS_OUT.labels(tenant=principal.tenant, model=engine.model_name).inc(tout)

    if body.use_cache and text:
        await cache.set(prompt, params, text)

    log.info("generate_ok", tin=tin, tout=tout, finish=finish)
    return GenerateResponse(
        text=text,
        tokens_in=tin,
        tokens_out=tout,
        finish_reason=finish,
        request_id=rid,
        cached=False,
        model=engine.model_name,
    )
