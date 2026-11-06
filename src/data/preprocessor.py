"""Tokenization and prompt formatting for fine-tuning."""

from __future__ import annotations

from typing import Any

try:
    from transformers import PreTrainedTokenizerBase  # type: ignore
except Exception:  # pragma: no cover - transformers may not be installed
    PreTrainedTokenizerBase = Any  # type: ignore


def format_prompt(instruction: str, input_text: str | None = None) -> str:
    """Build an instruction-tuning prompt."""
    if input_text:
        return f"Instruction: {instruction}\nInput: {input_text}\nOutput:"
    return f"Instruction: {instruction}\nOutput:"


def tokenize(
    examples: dict[str, list[str]],
    tokenizer: PreTrainedTokenizerBase,
    max_length: int = 2048,
) -> dict[str, list[list[int]]]:
    """Tokenize a batch of examples for causal language modeling."""
    texts = [format_prompt(i, inp) for i, inp in zip(examples["instruction"], examples.get("input", [None] * len(examples["instruction"])))]
    return tokenizer(
        texts,
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors=None,
    )
