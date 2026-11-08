"""Generation routes with sanitization + injection detection."""
from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter, HTTPException, Request

from src.serving.engine import LLMEngine
from src.serving.schemas import GenerateRequest, GenerateResponse
from src.utils.logger import get_logger
from src.utils.security import detect_prompt_injection, redact_pii, sanitize_text

log = get_logger(__name__)
router = APIRouter()


def _engine(request: Request) -> LLMEngine:
    eng = getattr(request.app.state, "engine", None)
    if eng is None or not eng.ready:
        raise HTTPException(status_code=503, detail="model not ready")
    return eng


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, request: Request) -> GenerateResponse:
    eng = _engine(request)

    prompt = sanitize_text(req.prompt)
    if detect_prompt_injection(prompt):
        log.warning("prompt_injection_blocked", ip=request.client.host if request.client else "unknown")
        raise HTTPException(status_code=400, detail="prompt rejected by safety filter")

    if os.getenv("ENABLE_PII_REDACTION", "true").lower() == "true":
        prompt = redact_pii(prompt)

    timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    try:
        text, tin, tout, finish, rid = await asyncio.wait_for(
            eng.generate(
                prompt,
                temperature=req.temperature,
                top_p=req.top_p,
                max_tokens=req.max_tokens,
                stop=req.stop,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="generation timeout") from None
    except Exception as e:  # noqa: BLE001
        log.error("generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="generation failed") from e

    return GenerateResponse(
        text=text, tokens_in=tin, tokens_out=tout, finish_reason=finish, request_id=rid
    )
