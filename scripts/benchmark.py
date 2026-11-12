"""Quick benchmark: throughput + P50/P95 latency against a running server."""
from __future__ import annotations

import os
import statistics
import sys
import time

import httpx


def main(url: str = "http://localhost:8000", n: int = 50) -> None:
    api_key = os.getenv("API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    latencies: list[float] = []
    with httpx.Client(timeout=120.0) as c:
        for i in range(n):
            start = time.perf_counter()
            r = c.post(f"{url}/generate", headers=headers, json={"prompt": f"Q{i}: hello", "max_tokens": 32})
            elapsed = time.perf_counter() - start
            if r.status_code == 200:
                latencies.append(elapsed)
    if not latencies:
        print("No successful requests")
        sys.exit(1)
    latencies.sort()
    print(f"n={len(latencies)}")
    print(f"p50={statistics.median(latencies) * 1000:.1f}ms")
    print(f"p95={latencies[int(0.95 * len(latencies))] * 1000:.1f}ms")
    print(f"mean={statistics.mean(latencies) * 1000:.1f}ms")
    print(f"throughput={len(latencies) / sum(latencies):.2f} req/s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000")
