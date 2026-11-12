"""Dataset quality gates: length, repetition, refusal detection."""
from __future__ import annotations

import re
from dataclasses import dataclass

REFUSAL_PATTERNS = [
    re.compile(r"(?i)as an ai language model", re.I),
    re.compile(r"(?i)i cannot (assist|help|comply)", re.I),
    re.compile(r"(?i)i'?m sorry, but i (can't|cannot)", re.I),
]


@dataclass
class QualityResult:
    passed: bool
    reasons: list[str]


def score_example(instruction: str, output: str, *, min_out_len: int = 10, max_rep: float = 0.3) -> QualityResult:
    reasons: list[str] = []
    if len(instruction.strip()) < 5:
        reasons.append("instruction_too_short")
    if len(output.strip()) < min_out_len:
        reasons.append("output_too_short")
    for pat in REFUSAL_PATTERNS:
        if pat.search(output):
            reasons.append("refusal_response")
            break
    # Repetition score (unique word ratio)
    words = output.lower().split()
    if len(words) >= 20:
        ratio = len(set(words)) / len(words)
        if ratio < (1 - max_rep):
            reasons.append("high_repetition")
    return QualityResult(passed=not reasons, reasons=reasons)
