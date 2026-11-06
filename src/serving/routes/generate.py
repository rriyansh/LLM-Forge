"""Generate and chat/completions endpoints."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.serving.engine import vLLMEngine
from src.serving.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    GenerateRequest,
    GenerateResponse,
)

router = APIRouter()

engine = vLLMEngine(model="/models/llama-3-8b")


def get_engine() -> vLLMEngine:
    return engine


@router.on_event("startup")
async def startup() -> None:
    await engine.start()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest, eng: vLLMEngine = Depends(get_engine)
) -> GenerateResponse:
    sampling_params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
    }
    text = await eng.generate(request.prompt, sampling_params)
    return GenerateResponse(
        generated_text=text,
        model=eng.model,
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    )


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest, eng: vLLMEngine = Depends(get_engine)
) -> ChatCompletionResponse:
    prompt = "\n".join(f"{m.role}: {m.content}" for m in request.messages)
    sampling_params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
    }
    text = await eng.generate(prompt, sampling_params)
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        model=request.model,
        choices=[
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    )
