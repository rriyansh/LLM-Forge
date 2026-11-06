"""Unit tests for the data loader."""

import json
import tempfile
from pathlib import Path

from src.data.loader import load_jsonl, save_jsonl


def test_save_and_load_jsonl(tmp_path: Path) -> None:
    records = [{"text": "hello"}, {"text": "world"}]
    path = tmp_path / "data.jsonl"
    save_jsonl(records, path)

    loaded = load_jsonl(path)
    assert loaded == records


def test_load_jsonl_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "blank.jsonl"
    path.write_text('{"text": "a"}\n\n{"text": "b"}\n', encoding="utf-8")
    loaded = load_jsonl(path)
    assert len(loaded) == 2
