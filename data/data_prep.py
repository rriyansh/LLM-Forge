"""Data cleaning, formatting, and splitting for LLM-Forge."""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_config(path: str | Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configs")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def format_instruction(instruction: str, input_text: str | None, output: str) -> dict[str, Any]:
    if input_text:
        text = f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output}"
    else:
        text = f"Instruction: {instruction}\nOutput: {output}"
    return {"text": text}


def prepare(
    raw_path: str | Path,
    train_out: str | Path,
    val_out: str | Path,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> None:
    raw_path = Path(raw_path)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")

    records = load_jsonl(raw_path)
    formatted = [
        format_instruction(r.get("instruction", ""), r.get("input"), r.get("output", ""))
        for r in records
    ]

    rng = random.Random(seed)
    rng.shuffle(formatted)

    n_val = max(1, int(len(formatted) * val_ratio))
    val_records = formatted[:n_val]
    train_records = formatted[n_val:]

    write_jsonl(train_records, train_out)
    write_jsonl(val_records, val_out)

    print(f"Total records: {len(formatted)}")
    print(f"Train records: {len(train_records)} -> {train_out}")
    print(f"Val records:   {len(val_records)} -> {val_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare instruction data for fine-tuning")
    parser.add_argument("--raw", required=True, help="Path to raw JSONL data")
    parser.add_argument("--train-out", default="data/processed/train.jsonl")
    parser.add_argument("--val-out", default="data/processed/val.jsonl")
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    prepare(args.raw, args.train_out, args.val_out, args.val_ratio, args.seed)


if __name__ == "__main__":
    main()
