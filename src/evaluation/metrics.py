"""Perplexity, ROUGE, and domain-specific accuracy metrics."""

from __future__ import annotations

import math
from typing import Any

try:
    from rouge_score import rouge_scorer  # type: ignore
except Exception:  # pragma: no cover
    rouge_scorer = None  # type: ignore


def perplexity(loss: float) -> float:
    """Compute perplexity from a loss value."""
    return math.exp(loss)


def rouge_scores(prediction: str, reference: str) -> dict[str, float]:
    """Compute ROUGE-1, ROUGE-2, and ROUGE-L F1 scores."""
    if rouge_scorer is None:
        raise RuntimeError("rouge-score is required for ROUGE metrics")
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rouge2": scores["rouge2"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure,
    }


def accuracy(predictions: list[Any], references: list[Any]) -> float:
    """Compute exact-match accuracy."""
    if len(predictions) != len(references):
        raise ValueError("predictions and references must have the same length")
    if not predictions:
        return 0.0
    matches = sum(1 for p, r in zip(predictions, references) if p == r)
    return matches / len(predictions)
