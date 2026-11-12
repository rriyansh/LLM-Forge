"""Dataset loading with JSON-schema validation."""
from __future__ import annotations

from pathlib import Path

from datasets import Dataset, load_dataset
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from src.utils.exceptions import ValidationError


class AlpacaExample(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=8192)
    input: str = Field(default="", max_length=16384)
    output: str = Field(..., min_length=1, max_length=16384)


class PreferenceExample(BaseModel):
    """DPO format."""
    prompt: str = Field(..., min_length=1)
    chosen: str = Field(..., min_length=1)
    rejected: str = Field(..., min_length=1)


def _validate_rows(ds: Dataset, model: type[BaseModel], sample: int = 100) -> None:
    n = min(sample, len(ds))
    for i in range(n):
        row = {k: ds[i].get(k, "") for k in model.model_fields}
        try:
            model(**row)
        except PydanticValidationError as e:
            raise ValidationError(f"invalid_row at index {i}: {e}") from e


def load_sft_dataset(path: str | Path) -> Dataset:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Dataset not found: {p}")
    ds = load_dataset("json", data_files=str(p), split="train")
    if len(ds) == 0:
        raise ValidationError("empty_dataset")
    _validate_rows(ds, AlpacaExample)
    return ds


def load_preference_dataset(path: str | Path) -> Dataset:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Dataset not found: {p}")
    ds = load_dataset("json", data_files=str(p), split="train")
    if len(ds) == 0:
        raise ValidationError("empty_dataset")
    _validate_rows(ds, PreferenceExample)
    return ds
