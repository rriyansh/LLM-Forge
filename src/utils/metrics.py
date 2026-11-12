"""Prometheus metrics registry."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# HTTP
HTTP_REQUESTS = Counter(
    "llmforge_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "llmforge_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

# Generation
TOKENS_IN = Counter("llmforge_tokens_in_total", "Input tokens", ["tenant", "model"])
TOKENS_OUT = Counter("llmforge_tokens_out_total", "Output tokens", ["tenant", "model"])
GEN_LATENCY = Histogram(
    "llmforge_generation_duration_seconds",
    "Time spent in vLLM engine",
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)
INFLIGHT = Gauge("llmforge_inflight_requests", "In-flight generation requests", ["tenant"])

# Safety
SAFETY_BLOCKS = Counter(
    "llmforge_safety_blocks_total", "Requests blocked by safety filters",
    ["reason", "category"],
)
RATE_LIMITED = Counter("llmforge_rate_limited_total", "Requests hit by rate limit")
QUOTA_HIT = Counter("llmforge_quota_exceeded_total", "Requests over quota", ["tier", "metric"])

# Cache
CACHE_HITS = Counter("llmforge_cache_hits_total", "Semantic cache hits")
CACHE_MISSES = Counter("llmforge_cache_misses_total", "Semantic cache misses")

# Circuit breakers
CIRCUIT_STATE = Gauge("llmforge_circuit_state", "Circuit breaker state (0=closed,1=half,2=open)", ["name"])
