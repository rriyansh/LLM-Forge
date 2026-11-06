"""Dataset loading from JSONL and Hugging Face datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSONL file into a list of dictionaries."""
    records: list[dict[str, Any]] = []
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                import json

                records.append(json.loads(line))
    return records


def load_hf_dataset(dataset_name: str, split: str = "train", **kwargs: Any) -> Any:
    """Load a dataset from the Hugging Face Hub."""
    from datasets import load_dataset

    return load_dataset(dataset_name, split=split, **kwargs)


def save_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    """Save a list of dictionaries to a JSONL file."""
    import json

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
