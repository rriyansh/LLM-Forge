"""Typed YAML config loader with validation."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    id: str
    torch_dtype: str = "bfloat16"
    trust_remote_code: bool = False


class QuantizationConfig(BaseModel):
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_use_double_quant: bool = True


class LoRAConfig(BaseModel):
    r: int = Field(16, ge=4, le=128)
    alpha: int = Field(32, ge=8, le=256)
    dropout: float = Field(0.05, ge=0.0, le=0.5)
    target_modules: list[str]


class TrainingConfig(BaseModel):
    output_dir: str = "./checkpoints"
    num_train_epochs: int = Field(2, ge=1)
    per_device_train_batch_size: int = Field(2, ge=1)
    gradient_accumulation_steps: int = Field(8, ge=1)
    learning_rate: float = Field(2e-4, gt=0)
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = Field(0.05, ge=0.0, le=0.5)
    bf16: bool = True
    logging_steps: int = 10
    save_strategy: str = "epoch"
    save_total_limit: int = 2
    max_seq_length: int = Field(2048, ge=128)
    packing: bool = True
    gradient_checkpointing: bool = True
    optim: str = "paged_adamw_8bit"


class WandbConfig(BaseModel):
    project: str = "llm-forge"
    run_name: str = "llama3-8b-qlora"


class FullTrainingConfig(BaseModel):
    model: ModelConfig
    quantization: QuantizationConfig
    lora: LoRAConfig
    training: TrainingConfig
    wandb: WandbConfig


class EngineConfig(BaseModel):
    max_model_len: int = Field(4096, ge=512)
    gpu_memory_utilization: float = Field(0.85, ge=0.1, le=0.99)
    tensor_parallel_size: int = Field(1, ge=1)
    max_num_seqs: int = Field(64, ge=1)
    dtype: str = "bfloat16"
    trust_remote_code: bool = False
    enable_prefix_caching: bool = True
    enable_chunked_prefill: bool = True


class GenerationConfig(BaseModel):
    default_temperature: float = Field(0.7, ge=0.0, le=2.0)
    default_top_p: float = Field(0.95, gt=0.0, le=1.0)
    default_max_tokens: int = Field(512, ge=1)
    max_max_tokens: int = Field(4096, ge=1)
    stop_sequences: list[str] = Field(default_factory=list)


class SecurityConfig(BaseModel):
    rate_limit_per_minute: int = Field(60, ge=1)
    max_request_bytes: int = Field(1_048_576, ge=1024)
    request_timeout_seconds: int = Field(60, ge=1)
    enable_pii_redaction: bool = True


class FullServingConfig(BaseModel):
    engine: EngineConfig
    generation: GenerationConfig
    security: SecurityConfig


def _load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=4)
def load_training_config(path: str = "configs/training_config.yaml") -> FullTrainingConfig:
    return FullTrainingConfig(**_load_yaml(path))


@lru_cache(maxsize=4)
def load_serving_config(path: str = "configs/serving_config.yaml") -> FullServingConfig:
    return FullServingConfig(**_load_yaml(path))


def get_env(key: str, default: str | None = None, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Required env var missing: {key}")
    return val  # type: ignore[return-value]
