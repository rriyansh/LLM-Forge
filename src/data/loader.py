"""Dataset loading with schema validation."""
from __future__ import annotations

from pathlib import Path

from datasets import Dataset, load_dataset
from pydantic import BaseModel, Field


class AlpacaExample(BaseModel):
    instruction: str = Field(..., min_length=1)
    input: str = ""
    output: str = Field(..., min_length=1)


def load_jsonl_dataset(path: str | Path) -> Dataset:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    ds = load_dataset("json", data_files=str(path), split="train")
    if len(ds) == 0:
        raise ValueError("Dataset is empty")
    # validate a sample of rows
    for i, row in enumerate(ds.select(range(min(50, len(ds))))):
        AlpacaExample(**{k: row.get(k, "") for k in ("instruction", "input", "output")})
    return ds
