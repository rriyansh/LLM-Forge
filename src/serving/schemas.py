"""Pydantic request/response models with strict validation."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=32_000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.95, gt=0.0, le=1.0)
    max_tokens: int = Field(256, ge=1, le=4096)
    stop: list[str] = Field(default_factory=list, max_length=8)


class GenerateResponse(BaseModel):
    text: str
    tokens_in: int
    tokens_out: int
    finish_reason: str
    request_id: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
