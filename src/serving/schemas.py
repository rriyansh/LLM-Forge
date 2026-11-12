"""Pydantic request/response models with strict validation."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=32_000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.95, gt=0.0, le=1.0)
    max_tokens: int = Field(256, ge=1, le=4096)
    stop: list[str] = Field(default_factory=list, max_length=8)
    use_cache: bool = True

    @field_validator("stop")
    @classmethod
    def _limit_stop(cls, v: list[str]) -> list[str]:
        return [s[:64] for s in v]


class GenerateResponse(BaseModel):
    text: str
    tokens_in: int
    tokens_out: int
    finish_reason: str
    request_id: str
    cached: bool = False
    model: str = ""


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=32_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=64)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.95, gt=0.0, le=1.0)
    max_tokens: int = Field(256, ge=1, le=4096)
    stop: list[str] = Field(default_factory=list, max_length=8)
    stream: bool = False
    use_cache: bool = True


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: dict[str, int]


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "llm-forge"
    created: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
    dependencies: dict[str, str] = Field(default_factory=dict)


class TokenRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
