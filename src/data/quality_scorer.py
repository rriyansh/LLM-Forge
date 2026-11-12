"""LLM-assisted and heuristic quality scoring for dataset curation."""
from __future__ import annotations

import re

from src.data.validator import score_example

HEDGING_RE = re.compile(r"(?i)\b(maybe|probably|i think|not sure|perhaps)\b")


def heuristic_score(instruction: str, output: str) -> float:
    """0..1 heuristic quality score (higher = better)."""
    score = 1.0
    q = score_example(instruction, output)
    if not q.passed:
        score -= 0.3 * len(q.reasons)
    # Prefer outputs with structure (lists, examples)
    if re.search(r"^\s*[-*0-9]+\.", output, re.M):
        score += 0.05
    # Penalize hedging
    if HEDGING_RE.search(output):
        score -= 0.05
    # Prefer length in sweet spot
    out_len = len(output)
    if out_len < 30:
        score -= 0.1
    elif 100 <= out_len <= 2000:
        score += 0.05
    return max(0.0, min(1.0, score))
