
# Architecture

<p align="left">
  <img src="https://img.shields.io/badge/system-architecture-blue?style=flat-square&logo=diagramsdotnet&logoColor=white" alt="Architecture" />
  <img src="https://img.shields.io/badge/version-2.0.0-2ea44f?style=flat-square" alt="Version 2.0.0" />
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=flat-square" alt="Status Stable" />
  <img src="https://img.shields.io/badge/review-quarterly-orange?style=flat-square&logo=calendar&logoColor=white" alt="Review Quarterly" />
</p>

This document describes the system architecture of LLM-Forge v2.0. It covers
the high-level topology, layer responsibilities, data flows, scaling strategy,
failure modes, and the design decisions behind each component.

---

## Table of Contents

| | Section |
|---|---|
| ▸ | [High-Level Topology](#high-level-topology) |
| ▸ | [Layers](#layers) |
| ▸ | [Data Flow: Generate](#data-flow-generate) |
| ▸ | [Training Data Flow](#training-data-flow) |
| ▸ | [Scaling Strategy](#scaling-strategy) |
| ▸ | [Failure Modes and Recovery](#failure-modes-and-recovery) |
| ▸ | [Design Decisions](#design-decisions) |
| ▸ | [Future Work](#future-work) |

---

## High-Level Topology

<p align="left">
  <img src="https://img.shields.io/badge/edge-cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white" alt="Cloudflare" />
  <img src="https://img.shields.io/badge/ingress-nginx-009639?style=flat-square&logo=nginx&logoColor=white" alt="NGINX" />
  <img src="https://img.shields.io/badge/app-fastapi-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/inference-vllm-FF6B35?style=flat-square&logo=vllm&logoColor=white" alt="vLLM" />
  <img src="https://img.shields.io/badge/state-redis%20%2B%20postgres-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis + Postgres" />
  <img src="https://img.shields.io/badge/observability-prometheus%20%2B%20grafana-E6522C?style=flat-square&logo=prometheus&logoColor=white" alt="Prometheus + Grafana" />
</p>

```text
                              +------------------+
                              |  DNS + TLS       |
                              |  (Cloudflare)    |
                              +--------+---------+
                                       |
                                       v
                              +------------------+
                              |  Ingress (NGINX) |
                              |  WAF + TLS term  |
                              |  IP rate limit   |
                              +--------+---------+
                                       |
                                       v
                       +------------------------------+
                       |  FastAPI Middleware Stack    |
                       |  1. Correlation ID           |
                       |  2. IP allowlist             |
                       |  3. Body size limit          |
                       |  4. Rate limit (Redis)       |
                       |  5. Security headers         |
                       |  6. Admin API-key (opt)      |
                       |  7. Metrics collection       |
                       +--------------+---------------+
                                      |
                                      v
                       +------------------------------+
                       |  Route Handler               |
                       |  - Auth (JWT / API key)      |
                       |  - RBAC scope check          |
                       |  - Quota check (Redis)       |
                       |  - PII redaction (Presidio)  |
                       |  - Injection detection       |
                       |  - Semantic cache lookup     |
                       +--------------+---------------+
                                      |
                                      v
                       +------------------------------+
                       |  vLLM AsyncLLM Engine        |
                       |  - Concurrency semaphore     |
                       |  - PagedAttention            |
                       |  - Continuous batching       |
                       |  - Prefix caching            |
                       +--------------+---------------+
                                      |
                                      v
                              +---------------+
                              |  GPU + Model  |
                              |  Weights (PV) |
                              +---------------+

Sidecars / Services:
  +---------+   +------------+   +------------+   +----------+
  |  Redis  |   |  Postgres  |   | Prometheus |   |   Tempo  |
  | cache+  |   | users +    |   | metrics    |   |  traces  |
  | quota+  |   | usage      |   | scraping   |   |          |
  | ratelmt |   |            |   |            |   |          |
  +---------+   +------------+   +------------+   +----------+
                                                       ^
                                                       | OTLP
                                                   +---+----+
                                                   |  Loki  |
                                                   |  logs  |
                                                   +--------+
```

---

## Layers

### 1. Edge Layer

<p align="left">
  <img src="https://img.shields.io/badge/cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare" />
  <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white" alt="NGINX" />
  <img src="https://img.shields.io/badge/letsencrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="Let's Encrypt" />
</p>

The edge layer terminates TLS, applies WAF rules, and enforces coarse
IP-level rate limits before traffic reaches the application.

| Component | Responsibility | Technology |
|---|---|---|
| DNS | Resolve `api.llmforge.dev` | Cloudflare (DNSSEC, CAA) |
| TLS termination | HTTPS handshake, certificate management | Cloudflare + cert-manager + Let's Encrypt |
| WAF | Block common attacks (SQLi, XSS, bot signatures) | Cloudflare managed rules |
| IP rate limit | Coarse per-IP throttle (50 rps) | NGINX Ingress `limit-rps` |
| Body size cap | Reject oversized payloads | NGINX `proxy-body-size: 2m` |

### 2. Middleware Layer

<p align="left">
  <img src="https://img.shields.io/badge/middleware-7%20layers-blue?style=for-the-badge&logo=fastapi&logoColor=white" alt="Middleware" />
</p>

Middlewares execute outside-in. Order matters: authentication and rate
limiting come before route handlers, and response headers are attached last.

| # | Middleware | Purpose | Failure Mode |
|---|---|---|---|
| 1 | `CorrelationMiddleware` | Assign or forward `X-Request-ID` | Pass-through if header malformed |
| 2 | `IPAllowlistMiddleware` | Reject non-allowlisted IPs (opt-in) | Deny by default if enabled |
| 3 | `BodySizeLimitMiddleware` | Reject >1 MB bodies | Return 413 |
| 4 | `RateLimitMiddleware` | Redis sliding-window per IP | Fail-open to in-memory limiter if Redis unreachable |
| 5 | `SecurityHeadersMiddleware` | HSTS, CSP, X-Frame-Options, etc. | Attach on every response |
| 6 | `AdminAPIKeyMiddleware` | Static API key for `/admin/*` | Return 401 on mismatch |
| 7 | `MetricsMiddleware` | Prometheus counters and histograms | Continue on metrics failure |

### 3. Route Layer

<p align="left">
  <img src="https://img.shields.io/badge/routes-6%20endpoints-green?style=for-the-badge&logo=fastapi&logoColor=white" alt="Routes" />
</p>

Route handlers enforce authentication, authorization, quotas, safety, and cache
lookups before invoking the engine.

| Concern | Enforced By | Module |
|---|---|---|
| Authentication | `get_principal()` resolves JWT or API key | `src/utils/auth.py` |
| Authorization | `require_scopes(...)` checks role scopes | `src/utils/auth.py` |
| Quota | `check_and_consume()` increments Redis counters | `src/serving/quota.py` |
| Safety | `detect_prompt_injection()`, `redact_pii()`, `sanitize_text()` | `src/utils/security.py` |
| Cache | `SemanticCache.get()` and `.set()` | `src/serving/cache.py` |

Available routes:

| Method | Path | Purpose | Scope |
|---|---|---|---|
| `POST` | `/generate` | Text completion | `generate` |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat | `chat` |
| `GET` | `/v1/models` | List models | `models:list` |
| `POST` | `/auth/token` | Issue JWT | public |
| `GET` | `/health/live` | Liveness probe | public |
| `GET` | `/health/ready` | Readiness probe | public |
| `GET` | `/metrics` | Prometheus scrape | public (cluster) |
| `GET` | `/admin/status` | Admin status | API key only |
| `POST` | `/admin/reload` | Reload engine | API key only |

### 4. Inference Layer

<p align="left">
  <img src="https://img.shields.io/badge/vllm-FF6B35?style=for-the-badge&logo=vllm&logoColor=white" alt="vLLM" />
  <img src="https://img.shields.io/badge/cuda-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA" />
  <img src="https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
</p>

The inference layer wraps vLLM's `AsyncLLM` engine in a controlled interface.

| Feature | Implementation | Benefit |
|---|---|---|
| Concurrency cap | `asyncio.Semaphore(max_concurrent_requests)` | Prevents GPU queue overflow |
| Request timeout | `asyncio.wait_for(timeout=REQUEST_TIMEOUT_SECONDS)` | Bounded latency |
| PagedAttention | vLLM native | 2-3x throughput vs HF `generate` |
| Continuous batching | vLLM native | No head-of-line blocking |
| Prefix caching | vLLM `enable_prefix_caching` | Free win for system-prompt-heavy workloads |
| Chunked prefill | vLLM `enable_chunked_prefill` | Better GPU utilization under load |
| Streaming | SSE via `StreamingResponse` | Real-time token delivery |

### 5. State Layer

<p align="left">
  <img src="https://img.shields.io/badge/redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/postgresql-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/sqlalchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
</p>

State is split between Redis (ephemeral, fast) and Postgres (durable, ACID).

| Store | Purpose | TTL | Backend |
|---|---|---|---|
| Redis DB 0 | Rate limits, quotas | 60s to 24h | `REDIS_URL` |
| Redis DB 1 | Response cache | `SEMANTIC_CACHE_TTL_SECONDS` | `CACHE_REDIS_URL` |
| Postgres | Users, tenants, API keys, usage | Permanent | `DATABASE_URL` |

### 6. Observability Layer

<p align="left">
  <img src="https://img.shields.io/badge/prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus" />
  <img src="https://img.shields.io/badge/grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana" />
  <img src="https://img.shields.io/badge/opentelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OpenTelemetry" />
  <img src="https://img.shields.io/badge/loki-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Loki" />
  <img src="https://img.shields.io/badge/tempo-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Tempo" />
</p>

The observability layer captures metrics, traces, and logs from every
component.

| Signal | Backend | Purpose |
|---|---|---|
| Metrics | Prometheus | Counters, histograms, gauges at `/metrics` |
| Traces | OpenTelemetry to Tempo | Request flow across FastAPI, asyncpg, vLLM |
| Logs | structlog JSON to Loki | Structured events with `request_id`, `user_id` |
| Dashboards | Grafana | Visualize metrics and logs |
| Alerts | Alertmanager | Page on-call on SLO breach |

---

## Data Flow: Generate

<p align="left">
  <img src="https://img.shields.io/badge/path-POST%20%2Fgenerate-2ea44f?style=for-the-badge&logo=http&logoColor=white" alt="POST /generate" />
</p>

The end-to-end request lifecycle for `POST /generate`:

```text
 1. Client sends POST /generate with Bearer JWT
 2. Ingress terminates TLS and applies WAF
 3. CorrelationMiddleware sets or forwards X-Request-ID
 4. IPAllowlistMiddleware checks (opt-in via IP_ALLOWLIST)
 5. BodySizeLimitMiddleware rejects if >1 MB
 6. RateLimitMiddleware calls RedisRateLimiter.allow(ip, limit=60/min)
 7. SecurityHeadersMiddleware adds response headers
 8. MetricsMiddleware starts a timer
 9. Route handler: require_scopes("generate") validates JWT
10. sanitize_text(prompt) strips control chars and caps length
11. detect_prompt_injection(prompt) returns 400 on heuristic match
12. redact_pii(prompt) via Presidio
13. check_and_consume(tenant) increments Redis quota
14. SemanticCache.get(prompt, params) returns early on hit
15. engine.generate(...) wrapped in asyncio.wait_for(timeout):
    a. Acquire semaphore
    b. Build vLLM SamplingParams
    c. Async iteration over output tokens
    d. Release semaphore
16. SemanticCache.set(prompt, params, text)
17. Prometheus counters updated: tokens_in, tokens_out, latency
18. Return GenerateResponse
```

Response time targets:

| Metric | Target | Current | Alert |
|---|---|---|---|
| P50 latency | <500ms | ~300ms | — |
| P95 latency | <2s | ~1.5s | >5s for 5m |
| P99 latency | <5s | ~3s | — |
| Throughput | >20 req/s per replica | ~30 req/s | — |
| Cache hit rate | >30% | ~40% | — |

---

## Training Data Flow

<p align="left">
  <img src="https://img.shields.io/badge/pipeline-data%20to%20model-FE5196?style=for-the-badge&logo=huggingface&logoColor=white" alt="Training Pipeline" />
  <img src="https://img.shields.io/badge/tracker-wandb-FFBE00?style=for-the-badge&logo=weightsandbiases&logoColor=black" alt="W&B" />
</p>

The training pipeline moves data from raw sources to a deployed model.

```text
+--------------+   +--------------+   +--------------+
| data/raw/*   |-->| data_prep.py |-->|data/processed|
| (PDF, JSON,  |   | - schema     |   |  train.jsonl |
|  CSV, HTML)  |   | - dedup      |   |  val.jsonl   |
|              |   | - quality    |   |              |
+--------------+   +--------------+   +------+-------+
                                             |
                                             v
                                    +----------------+
                                    | qlora_trainer  |
                                    | - 4-bit load   |
                                    | - LoRA attach  |
                                    | - SFTTrainer   |
                                    | - W&B log      |
                                    +--------+-------+
                                             |
                                             v
                                    +----------------+
                                    | checkpoints/   |
                                    |   final/       |
                                    | (LoRA adapter) |
                                    +--------+-------+
                                             |
                                             v
                                    +----------------+
                                    | merge_adapter  |
                                    | to merged model|
                                    +--------+-------+
                                             |
                                             v
                                    +----------------+
                                    | model_registry |
                                    | + evaluation   |
                                    +----------------+
```

Training stages:

| Stage | Input | Output | Notes |
|---|---|---|---|
| Data curation | Raw documents | `data/processed/train.jsonl` | Alpaca format, validated |
| Deduplication | Train JSONL | Deduplicated JSONL | MinHash, 0.9 similarity threshold |
| Quality scoring | Deduplicated JSONL | Scored JSONL | Heuristic + optional LLM |
| QLoRA training | Scored JSONL | `checkpoints/final` | 4-bit NF4, LoRA r=16 |
| Adapter merge | `checkpoints/final` | `models/merged` | `merge_and_unload` |
| Evaluation | `models/merged` | `reports/eval.json` | Perplexity, ROUGE-L, LLM judge |
| Registration | `models/merged` | `models/registry.json` | Versioned metadata |

---

## Scaling Strategy

<p align="left">
  <img src="https://img.shields.io/badge/horizontal-HPA-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Horizontal" />
  <img src="https://img.shields.io/badge/vertical-GPU-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="Vertical" />
  <img src="https://img.shields.io/badge/cache-3%20tiers-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Cache" />
</p>

### Horizontal scaling

| Component | Mechanism | Metric | Constraint |
|---|---|---|---|
| vLLM replicas | HPA | `vllm_num_requests_waiting` | 1 GPU per replica |
| Postgres | Read replicas | Connection count | Manual or Patroni |
| Redis | Cluster mode | Throughput >100k RPM | Requires cluster client |

### Vertical scaling

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `VLLM_GPU_MEMORY_UTILIZATION` | 0.85 | 0.5 to 0.95 | Higher = more KV cache |
| `VLLM_MAX_NUM_SEQS` | 64 | 32 to 256 | Higher = more concurrency |
| `MAX_CONCURRENT_REQUESTS` | 128 | 64 to 512 | Higher = more in-flight |
| `VLLM_MAX_MODEL_LEN` | 4096 | 2048 to 32768 | Higher = longer context |

### Caching tiers

| Tier | Backend | Hit Rate | TTL | Purpose |
|---|---|---|---|---|
| Response cache | Redis DB 1 | 30-60% | `SEMANTIC_CACHE_TTL_SECONDS` | Exact-match (prompt, params) |
| vLLM prefix cache | GPU KV cache | 20-40% | Session | Shared prefix (system prompts) |
| CDN | Cloudflare | 80%+ | Configurable | Static assets only |

---

## Failure Modes and Recovery

<p align="left">
  <img src="https://img.shields.io/badge/resilience-circuit%20breaker-orange?style=for-the-badge&logo=istio&logoColor=white" alt="Resilience" />
</p>

| Failure | Detection | Immediate Response | Recovery |
|---|---|---|---|
| vLLM OOM | `llmforge_http_requests_total{status="500"}` spike | Reduce `VLLM_MAX_MODEL_LEN` | Restart pod |
| Redis down | `/health/ready` reports `redis: down` | Fail-open to in-memory limiter | Restart Redis |
| Postgres down | Startup fails | Retry with backoff | Restore from backup |
| GPU preempted | Startup probe fails | K8s reschedules | Automatic |
| Model file corrupt | Startup fails | Rollback via `kubectl set image` | Redeploy |
| Traffic spike | HPA scales | Auto | Automatic |
| Prompt injection | `safety_blocks_total` spike | Reject with 400 | Review patterns |
| Circuit breaker open | `llmforge_circuit_state == 2` | Reject with 503 | Auto half-open after 30s |

See [RUNBOOK.md](RUNBOOK.md) for detailed recovery procedures.

---

## Design Decisions

<p align="left">
  <img src="https://img.shields.io/badge/rationale-documented-purple?style=for-the-badge&logo=readthedocs&logoColor=white" alt="Rationale" />
</p>

### Why vLLM?

| Aspect | vLLM | HF `generate` | Triton |
|---|---|---|---|
| Throughput | 2-3x | Baseline | 2-4x |
| PagedAttention | Native | No | No |
| Continuous batching | Yes | No | Yes |
| Prefix caching | Yes | No | No |
| Complexity | Low | Lowest | Highest |

vLLM offers the best balance of throughput, features, and simplicity for a
first-party deployment.

### Why Redis for cache, quota, and rate limit?

| Feature | Redis | Alternatives |
|---|---|---|
| Sub-millisecond latency | Yes | SQLite, files |
| Atomic operations | INCR, ZADD, EXPIRE | Files, Memcached |
| Distributed | Cluster mode | Single-node only |
| Battle-tested | Yes | N/A |

Redis's atomic primitives make it ideal for sliding-window rate limiting and
quota counters that must be consistent across replicas.

### Why PostgreSQL instead of SQLite?

| Feature | Postgres | SQLite |
|---|---|---|
| Concurrent writes | Yes | Single-writer |
| ACID | Yes | Yes |
| Row-level security | Yes | No |
| Migrations | Alembic | Manual |

Postgres handles concurrent writes from many API replicas safely.

### Why structlog with JSON output?

| Feature | structlog | Standard logging |
|---|---|---|
| Machine-parseable | JSON | Text |
| Secret scrubbing | Custom processor | Manual |
| Correlation IDs | ContextVars | Manual |
| Loki/ELK compatible | Direct | Parsing required |

Structlog provides first-class support for structured events and automatic
secret redaction.

### Why not LangChain?

| Aspect | Direct vLLM + FastAPI | LangChain |
|---|---|---|
| Latency overhead | ~5ms | ~50-200ms |
| Transparency | Full | Partial |
| Auditability | Every function is explicit | Chain abstractions hide logic |
| Dependencies | Minimal | Heavy |

LangChain adds abstraction overhead we do not need for a single-purpose API.

---

## Future Work

<p align="left">
  <img src="https://img.shields.io/badge/roadmap-planned-blue?style=for-the-badge&logo=gitbook&logoColor=white" alt="Roadmap" />
</p>

| Priority | Item | Description |
|---|---|---|
| High | pgvector semantic cache | Embedding-based similarity instead of exact hash |
| High | Multi-LoRA hot-swap | Serve multiple fine-tuned adapters on one base model |
| Medium | Guardrails AI integration | Structured output validation |
| Medium | Tool calling | OpenAI function calling compatibility |
| Medium | RAG pipeline | Pluggable retriever interface |
| Low | Model distillation | Small student from large teacher |
| Low | Triton backend | Alternative inference engine |
| Low | SGLang backend | Alternative inference engine |

---

## Related Documents

| Document | Description |
|---|---|
| [SECURITY.md](SECURITY.md) | Security posture and incident response |
| [API.md](API.md) | Endpoint reference |
| [RUNBOOK.md](RUNBOOK.md) | On-call playbook |
| [THREAT_MODEL.md](THREAT_MODEL.md) | STRIDE threat analysis |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Developer setup |
| [CHANGELOG_GUIDE.md](CHANGELOG_GUIDE.md) | Changelog format |
