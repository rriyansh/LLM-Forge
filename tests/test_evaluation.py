"""Unit tests for evaluation metrics."""

from src.evaluation.metrics import accuracy, perplexity, rouge_scores


def test_perplexity() -> None:
    assert perplexity(0.0) == 1.0
    assert perplexity(1.0) > 1.0


def test_accuracy() -> None:
    assert accuracy([1, 2, 3], [1, 2, 3]) == 1.0
    assert accuracy([1, 2, 3], [1, 5, 3]) == 2 / 3
    assert accuracy([], []) == 0.0


def test_rouge_scores() -> None:
    scores = rouge_scores("the cat is on the mat", "the cat is on the mat")
    assert abs(scores["rouge1"] - 1.0) < 1e-6
    assert abs(scores["rougeL"] - 1.0) < 1e-6
