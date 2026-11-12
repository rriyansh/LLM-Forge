"""Core metrics: perplexity, ROUGE-L, exact match."""
from __future__ import annotations

import math
import re
from collections.abc import Iterable

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


def compute_perplexity(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer, texts: Iterable[str], max_len: int = 1024
) -> float:
    total_loss, total_tokens = 0.0, 0
    model.eval()
    with torch.no_grad():
        for text in texts:
            enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_len)
            enc = {k: v.to(model.device) for k, v in enc.items()}
            out = model(**enc, labels=enc["input_ids"])
            n = enc["input_ids"].shape[1]
            total_loss += out.loss.item() * n
            total_tokens += n
    return math.exp(total_loss / max(1, total_tokens))


def _tokens(s: str) -> list[str]:
    return re.findall(r"\w+", s.lower())


def rouge_l(pred: str, ref: str) -> float:
    p, r = _tokens(pred), _tokens(ref)
    if not p or not r:
        return 0.0
    dp = [[0] * (len(r) + 1) for _ in range(len(p) + 1)]
    for i in range(1, len(p) + 1):
        for j in range(1, len(r) + 1):
            if p[i - 1] == r[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[-1][-1]
    prec, rec = lcs / len(p), lcs / len(r)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if pred.strip().lower() == ref.strip().lower() else 0.0
