import json
from pathlib import Path

import pytest

from src.data.deduplicator import dedup
from src.data.preprocessor import format_alpaca, format_chatml
from src.data.quality_scorer import heuristic_score


def test_format_alpaca():
    out = format_alpaca({"instruction": "Hi", "input": "", "output": "Hello"})
    assert "### Instruction:" in out["text"]
    assert "Hello" in out["text"]


def test_dedup():
    rows = [
        {"instruction": "What is the capital of France?"},
        {"instruction": "What is the capital of France?"},
        {"instruction": "Completely different question about quantum physics"},
    ]
    out = dedup(rows, threshold=0.8)
    assert len(out) == 2


def test_quality_score():
    s1 = heuristic_score("Explain photosynthesis in detail.", "Photosynthesis is the process by which plants convert light into energy. " * 5)
    assert s1 > 0.5
    s2 = heuristic_score("hi", "as an ai language model, I cannot help")
    assert s2 < 0.7
