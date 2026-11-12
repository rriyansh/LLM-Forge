"""OpenAI-compatible /v1/chat/completions endpoint (non-streaming + SSE)."""
from __future__ import annotations

import asyncio
import json
import time
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from src.serving.dependencies import get_engine
from src.serving.engine import LLMEngine
from src.serving.quota import check_and_consume
from src.serving.schemas import ChatChoice, ChatMessage, ChatRequest, ChatResponse
from src.utils.auth import Principal, require_scopes
from src.utils.config_parser import get_env_bool
from src.utils.exceptions import SafetyError, UpstreamTimeoutError
from src.utils.logger import audit, get_logger
from src.utils.metrics import GEN_LATENCY, TOKENS_IN, TOKENS_OUT
from src.utils.security import detect_prompt_injection, redact_pii, sanitize_text

log = get_logger(__name__)
router = APIRouter()


def _flatten(messages: list[ChatMessage]) -> str:
    parts = []
    for m in messages:
        parts.append(f"<|{m.role}|>\n{m.content}\n")
    parts.append("<|assistant|>\n")
    return "".join(parts)


@router.post("/v1/chat/completions")
async def chat(
    body: ChatRequest,
    request: Request,
    principal: Principal = Depends(require_scopes("chat")),
    engine: LLMEngine = Depends(get_engine),
):
    # Sanitize + safety
    safe_msgs: list[ChatMessage] = []
    for m in body.messages:
        content = sanitize_text(m.content)
        if get_env_bool("ENABLE_PROMPT_INJECTION_FILTER", True) and detect_prompt_injection(content):
            audit.safety_blocked(user_id=principal.user_id, reason="injection", category="chat")
            raise SafetyError("prompt_injection_detected")
        if get_env_bool("ENABLE_PII_REDACTION", True):
            content = redact_pii(content)
        safe_msgs.append(ChatMessage(role=m.role, content=content))

    await check_and_consume(principal.tenant, "default")
    prompt = _flatten(safe_msgs)
    req_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    if not body.stream:
        start = time.perf_counter()
        try:
            text, tin, tout, finish, _ = await asyncio.wait_for(
                engine.generate(
                    prompt,
                    temperature=body.temperature,
                    top_p=body.top_p,
                    max_tokens=body.max_tokens,
                    stop=body.stop,
                ),
                timeout=float(request.app.state.request_timeout),
            )
        except asyncio.TimeoutError as e:
            raise UpstreamTimeoutError("chat_timeout") from e

        GEN_LATENCY.observe(time.perf_counter() - start)
        TOKENS_IN.labels(tenant=principal.tenant, model=engine.model_name).inc(tin)
        TOKENS_OUT.labels(tenant=principal.tenant, model=engine.model_name).inc(tout)

        return ChatResponse(
            id=req_id,
            created=created,
            model=engine.model_name,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=text),
                    finish_reason=finish,
                )
            ],
            usage={"prompt_tokens": tin, "completion_tokens": tout, "total_tokens": tin + tout},
        )

    # Streaming (single-shot pseudo stream: yield full response, then [DONE])
    async def event_gen():
        try:
            text, _, _, finish, _ = await asyncio.wait_for(
                engine.generate(
                    prompt,
                    temperature=body.temperature,
                    top_p=body.top_p,
                    max_tokens=body.max_tokens,
                    stop=body.stop,
                ),
                timeout=float(request.app.state.request_timeout),
            )
            chunk = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": engine.model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": text},
                        "finish_reason": finish,
                    }
                ],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:  # noqa: BLE001
            err = {"error": {"message": str(e), "type": "server_error"}}
            yield f"data: {json.dumps(err)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
