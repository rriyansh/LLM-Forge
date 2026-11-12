"""Typed YAML config loader with validation + env override support."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


# ---------- Training ----------
class ModelSection(BaseModel):
    id: str
    torch_dtype: str = "bfloat16"
    trust_remote_code: bool = False


class QuantizationSection(BaseModel):
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_use_double_quant: bool = True


class LoraSection(BaseModel):
    r: int = Field(16, ge=4, le=256)
    alpha: int = Field(32, ge=8, le=512)
    dropout: float = Field(0.05, ge=0.0, le=0.5)
    target_modules: list[str]


class TrainingSection(BaseModel):
    output_dir: str = "./checkpoints"
    num_train_epochs: int = Field(2, ge=1)
    per_device_train_batch_size: int = Field(2, ge=1)
    gradient_accumulation_steps: int = Field(8, ge=1)
    learning_rate: float = Field(2e-4, gt=0)
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = Field(0.05, ge=0.0, le=0.5)
    weight_decay: float = Field(0.01, ge=0.0)
    max_grad_norm: float = Field(1.0, gt=0)
    bf16: bool = True
    logging_steps: int = 10
    save_strategy: str = "epoch"
    save_total_limit: int = 2
    max_seq_length: int = Field(2048, ge=128)
    packing: bool = True
    gradient_checkpointing: bool = True
    optim: str = "paged_adamw_8bit"
    group_by_length: bool = True


class DPOSection(BaseModel):
    beta: float = Field(0.1, gt=0)
    loss_type: str = "sigmoid"
    max_prompt_length: int = 1024
    max_length: int = 2048


class WandbSection(BaseModel):
    project: str = "llm-forge"
    run_name: str = "run"
    tags: list[str] = Field(default_factory=list)


class FullTrainingConfig(BaseModel):
    model: ModelSection
    quantization: QuantizationSection
    lora: LoraSection
    training: TrainingSection
    dpo: DPOSection
    wandb: WandbSection


# ---------- Serving ----------
class EngineSection(BaseModel):
    max_model_len: int = Field(4096, ge=512)
    gpu_memory_utilization: float = Field(0.85, ge=0.1, le=0.99)
    tensor_parallel_size: int = Field(1, ge=1)
    max_num_seqs: int = Field(64, ge=1)
    dtype: str = "bfloat16"
    trust_remote_code: bool = False
    enable_prefix_caching: bool = True
    enable_chunked_prefill: bool = True
    disable_log_requests: bool = True


class GenerationSection(BaseModel):
    default_temperature: float = Field(0.7, ge=0.0, le=2.0)
    default_top_p: float = Field(0.95, gt=0.0, le=1.0)
    default_max_tokens: int = Field(512, ge=1)
    max_max_tokens: int = Field(4096, ge=1)
    stop_sequences: list[str] = Field(default_factory=list)


class SecuritySection(BaseModel):
    rate_limit_per_minute: int = Field(60, ge=1)
    max_request_bytes: int = Field(1_048_576, ge=1024)
    request_timeout_seconds: int = Field(60, ge=1)
    enable_pii_redaction: bool = True
    enable_toxicity_filter: bool = True
    enable_injection_filter: bool = True


class CacheSection(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 3600
    similarity_threshold: float = Field(0.95, ge=0.5, le=1.0)
    max_entries: int = 10000


class LimitsSection(BaseModel):
    max_concurrent_requests: int = 128
    max_input_tokens: int = 32000
    max_output_tokens: int = 4096


class FullServingConfig(BaseModel):
    engine: EngineSection
    generation: GenerationSection
    security: SecuritySection
    cache: CacheSection
    limits: LimitsSection


# ---------- Security config ----------
class JWTConfig(BaseModel):
    jwt_algorithm: str = "HS256"
    access_ttl_seconds: int = 3600
    refresh_ttl_seconds: int = 604800
    issuer: str = "llm-forge"
    audience: str = "llm-forge-api"


class RBACRole(BaseModel):
    scopes: list[str]


class RBACConfig(BaseModel):
    roles: dict[str, RBACRole]

    def scopes_for(self, role: str) -> list[str]:
        r = self.roles.get(role)
        return r.scopes if r else []


class QuotaTier(BaseModel):
    requests_per_day: int
    tokens_per_day: int


class QuotasConfig(BaseModel):
    default: QuotaTier
    premium: QuotaTier


class FilterConfig(BaseModel):
    enabled: bool
    entities: list[str] = Field(default_factory=list)
    threshold: float = 0.8
    patterns: list[str] = Field(default_factory=list)


class FiltersConfig(BaseModel):
    pii: FilterConfig
    toxicity: FilterConfig
    injection: FilterConfig


class FullSecurityConfig(BaseModel):
    auth: JWTConfig
    rbac: RBACConfig
    quotas: QuotasConfig
    filters: FiltersConfig


# ---------- Eval ----------
class MetricGate(BaseModel):
    enabled: bool = True
    gate: float | None = None
    model: str | None = None
    criteria: list[str] = Field(default_factory=list)
    probes: list[str] = Field(default_factory=list)


class MetricsEvalConfig(BaseModel):
    perplexity: MetricGate
    rouge_l: MetricGate
    exact_match: MetricGate
    llm_as_judge: MetricGate
    safety: MetricGate


class ReportConfig(BaseModel):
    output_dir: str = "reports"
    format: str = "json"


class FullEvalConfig(BaseModel):
    metrics: MetricsEvalConfig
    report: ReportConfig


# ---------- Loaders ----------
def _load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {p}")
    return data


@lru_cache(maxsize=4)
def load_training_config(path: str = "configs/training_config.yaml") -> FullTrainingConfig:
    return FullTrainingConfig(**_load_yaml(path))


@lru_cache(maxsize=4)
def load_serving_config(path: str = "configs/serving_config.yaml") -> FullServingConfig:
    return FullServingConfig(**_load_yaml(path))


@lru_cache(maxsize=4)
def load_security_config(path: str = "configs/security_config.yaml") -> FullSecurityConfig:
    return FullSecurityConfig(**_load_yaml(path))


@lru_cache(maxsize=4)
def load_eval_config(path: str = "configs/eval_config.yaml") -> FullEvalConfig:
    return FullEvalConfig(**_load_yaml(path))


def get_env(key: str, default: str | None = None, *, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Required env var missing: {key}")
    return val  # type: ignore[return-value]


def get_env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


def get_env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default
