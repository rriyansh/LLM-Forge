"""MinHash-based near-duplicate detection for training data."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable


def _shingles(text: str, k: int = 5) -> set[str]:
    words = re.findall(r"\w+", text.lower())
    if len(words) < k:
        return {" ".join(words)}
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def _minhash(shingles: set[str], num_hashes: int = 64) -> tuple[int, ...]:
    sig = [10**9] * num_hashes
    for sh in shingles:
        h = hashlib.blake2b(sh.encode(), digest_size=16).digest()
        for i in range(num_hashes):
            v = int.from_bytes(h[i % 8 : i % 8 + 4], "little") ^ (i * 0x9E3779B1)
            if v < sig[i]:
                sig[i] = v
    return tuple(sig)


def dedup(rows: Iterable[dict], *, threshold: float = 0.9, key: str = "instruction") -> list[dict]:
    """Returns de-duplicated rows (first occurrence wins). O(N^2) worst case.

    For very large datasets, plug in a proper MinHash LSH index.
    """
    result: list[dict] = []
    signatures: list[tuple[int, ...]] = []
    for row in rows:
        sig = _minhash(_shingles(row.get(key, "")))
        is_dup = False
        for prev in signatures:
            matches = sum(1 for a, b in zip(sig, prev) if a == b)
            if matches / len(sig) >= threshold:
                is_dup = True
                break
        if not is_dup:
            result.append(row)
            signatures.append(sig)
    return result
