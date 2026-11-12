
<h1 align="center">
  <br>
  LLM-Forge V2
  <br>
</h1>

<h3 align="center">Production-grade, security-hardened pipeline for fine-tuning and serving open-source LLMs</h3>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/yourrealorg/llm-forge/ci.yml?branch=main&label=CI&logo=github-actions&logoColor=white&style=for-the-badge" alt="CI" />
  <img src="https://img.shields.io/github/actions/workflow/status/yourrealorg/llm-forge/security-scan.yml?branch=main&label=Security%20Scan&logo=github&logoColor=white&style=for-the-badge" alt="Security Scan" />
  <img src="https://img.shields.io/github/actions/workflow/status/yourrealorg/llm-forge/nightly-eval.yml?branch=main&label=Nightly%20Eval&logo=github&logoColor=white&style=for-the-badge" alt="Nightly Eval" />
  <img src="https://img.shields.io/github/license/yourrealorg/llm-forge?logo=opensourceinitiative&logoColor=white&style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white&style=for-the-badge" alt="Python 3.11+" />
</p>

<p align="center">
  An end-to-end, production-ready platform for domain-specific LLM fine-tuning (Llama-3, Mistral, Qwen)<br>
  using QLoRA + DPO, with a hardened high-throughput inference API built on vLLM + FastAPI.<br>
  Ships with RBAC, JWT auth, distributed rate limiting, semantic caching, circuit breakers,<br>
  OpenTelemetry tracing, Prometheus metrics, structured audit logs, PII redaction,<br>
  prompt-injection detection, and Helm charts.
</p>

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Security Highlights](#security-highlights)
- [Testing](#testing)
- [Deployment Options](#deployment-options)
- [Monitoring](#monitoring)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Tech Stack

### Language and Runtime

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="Ubuntu">
  <img src="https://img.shields.io/badge/GNU_Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white" alt="Bash">
</p>

### Machine Learning and Training

<p align="left">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace">
  <img src="https://img.shields.io/badge/Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Transformers">
  <img src="https://img.shields.io/badge/PEFT-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white" alt="PEFT">
  <img src="https://img.shields.io/badge/TRL-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white" alt="TRL">
  <img src="https://img.shields.io/badge/bitsandbytes-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="bitsandbytes">
  <img src="https://img.shields.io/badge/Datasets-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Datasets">
  <img src="https://img.shields.io/badge/Accelerate-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Accelerate">
  <img src="https://img.shields.io/badge/Safetensors-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white" alt="Safetensors">
</p>

### Inference Engine

<p align="left">
  <img src="https://img.shields.io/badge/vLLM-FF6B35?style=for-the-badge&logo=vllm&logoColor=white" alt="vLLM">
  <img src="https://img.shields.io/badge/CUDA-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA">
  <img src="https://img.shields.io/badge/NVIDIA-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="NVIDIA">
</p>

### Web Framework and API

<p align="left">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Uvicorn">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white" alt="OpenAPI">
  <img src="https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white" alt="JSON">
</p>

### Data and State

<p align="left">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Alembic-6BA539?style=for-the-badge&logo=python&logoColor=white" alt="Alembic">
  <img src="https://img.shields.io/badge/asyncpg-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="asyncpg">
</p>

### Security

<p align="left">
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/Presidio-0078D4?style=for-the-badge&logo=microsoft&logoColor=white" alt="Presidio">
  <img src="https://img.shields.io/badge/OpenSSL-721412?style=for-the-badge&logo=openssl&logoColor=white" alt="OpenSSL">
  <img src="https://img.shields.io/badge/HashiCorp_Vault-000000?style=for-the-badge&logo=vault&logoColor=white" alt="Vault">
  <img src="https://img.shields.io/badge/Passlib-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="Passlib">
  <img src="https://img.shields.io/badge/HMAC-000000?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="HMAC">
  <img src="https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white" alt="spaCy">
</p>

### Observability

<p align="left">
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus">
  <img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana">
  <img src="https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OpenTelemetry">
  <img src="https://img.shields.io/badge/Loki-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Loki">
  <img src="https://img.shields.io/badge/Tempo-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Tempo">
  <img src="https://img.shields.io/badge/structlog-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="structlog">
</p>

### Experiment Tracking

<p align="left">
  <img src="https://img.shields.io/badge/Weights_%26_Biases-FFBE00?style=for-the-badge&logo=weightsandbiases&logoColor=black" alt="Weights and Biases">
</p>

### Containers and Orchestration

<p align="left">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white" alt="Helm">
  <img src="https://img.shields.io/badge/NGINX_Ingress-009639?style=for-the-badge&logo=nginx&logoColor=white" alt="NGINX">
  <img src="https://img.shields.io/badge/cert--manager-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="cert-manager">
</p>

### CI/CD and DevOps

<p align="left">
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  <img src="https://img.shields.io/badge/Make-6D00CC?style=for-the-badge&logo=gnu&logoColor=white" alt="Make">
  <img src="https://img.shields.io/badge/Conventional_Commits-FE5196?style=for-the-badge&logo=conventionalcommits&logoColor=white" alt="Conventional Commits">
</p>

### Code Quality and Testing

<p align="left">
  <img src="https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black" alt="Ruff">
  <img src="https://img.shields.io/badge/Black-000000?style=for-the-badge&logo=python&logoColor=white" alt="Black">
  <img src="https://img.shields.io/badge/mypy-2A6DB2?style=for-the-badge&logo=python&logoColor=white" alt="mypy">
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Coverage-F4A261?style=for-the-badge&logo=python&logoColor=white" alt="Coverage">
  <img src="https://img.shields.io/badge/Pre--commit-FAB040?style=for-the-badge&logo=pre-commit&logoColor=black" alt="Pre-commit">
  <img src="https://img.shields.io/badge/Gitleaks-000000?style=for-the-badge&logo=git&logoColor=white" alt="Gitleaks">
  <img src="https://img.shields.io/badge/Bandit-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="Bandit">
  <img src="https://img.shields.io/badge/pip--audit-4B8BBE?style=for-the-badge&logo=pypi&logoColor=white" alt="pip-audit">
  <img src="https://img.shields.io/badge/Locust-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="Locust">
</p>

### Cloud Platforms (compatible)

<p align="left">
  <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS">
  <img src="https://img.shields.io/badge/EKS-FF9900?style=for-the-badge&logo=amazoneks&logoColor=white" alt="EKS">
  <img src="https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Google Cloud">
  <img src="https://img.shields.io/badge/GKE-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="GKE">
  <img src="https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Azure">
  <img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare">
  <img src="https://img.shields.io/badge/Let%27s_Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="Let's Encrypt">
</p>

### Formats and Protocols

<p align="left">
  <img src="https://img.shields.io/badge/YAML-CB171E?style=for-the-badge&logo=yaml&logoColor=white" alt="YAML">
  <img src="https://img.shields.io/badge/TOML-9C4121?style=for-the-badge&logo=toml&logoColor=white" alt="TOML">
  <img src="https://img.shields.io/badge/JSONL-000000?style=for-the-badge&logo=json&logoColor=white" alt="JSONL">
  <img src="https://img.shields.io/badge/HTTP%2F2-005C97?style=for-the-badge&logo=http&logoColor=white" alt="HTTP2">
  <img src="https://img.shields.io/badge/SSE-000000?style=for-the-badge&logo=serverless&logoColor=white" alt="SSE">
  <img src="https://img.shields.io/badge/OTLP-000000?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OTLP">
  <img src="https://img.shields.io/badge/gRPC-244C5A?style=for-the-badge&logo=grpc&logoColor=white" alt="gRPC">
</p>

---

## Features

### Training

- QLoRA 4-bit fine-tuning (PEFT + bitsandbytes + TRL)
- DPO preference optimization
- LoRA adapter merging for fast standalone serving
- W&B experiment tracking + file-based model registry
- Dataset quality scoring, MinHash deduplication, schema validation
- Config-driven (YAML), fully reproducible
- Model registry with version history and metric lineage
- Warmup pipeline to reduce first-request latency
- Smoke test support for smaller models before scaling to 8B

### Serving

- vLLM AsyncLLM engine (PagedAttention, continuous batching, prefix caching, chunked prefill)
- FastAPI with OpenAI-compatible `/v1/chat/completions`
- JWT + API key auth, RBAC scopes, multi-tenancy
- Redis-backed distributed rate limiting + per-tenant daily quotas
- Semantic response cache (Redis + local LRU fallback)
- Circuit breakers + retries with exponential backoff
- PII redaction (Presidio), prompt-injection filter, toxicity hooks
- SSE streaming for chat completions
- Admin endpoints for engine reload, status, circuit inspection
- Health probes (liveness, readiness with dependency checks)

### Operations

- Docker (separate train / serve images, multi-stage, non-root, read-only rootfs)
- Kubernetes manifests + Helm chart
- HPA (custom metrics), PDB, NetworkPolicy, ServiceMonitor
- OpenTelemetry traces to Tempo
- Prometheus metrics + Grafana dashboard
- Loki log aggregation
- Structured JSON logs with request-id + user-id correlation
- Audit log channel for security events (auth, quota, safety, admin actions)
- CI (lint, type, test, security scan) + CD (build, push, deploy)
- Pre-commit hooks (ruff, mypy, gitleaks, detect-secrets, black)
- Nightly evaluation workflow

---

## Project Structure

```text
llm-forge/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── Makefile
├── pyproject.toml
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── .pre-commit-config.yaml
│
├── .github/
│   ├── CODEOWNERS
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       ├── security-scan.yml
│       └── nightly-eval.yml
│
├── configs/
│   ├── training_config.yaml
│   ├── serving_config.yaml
│   ├── security_config.yaml
│   ├── eval_config.yaml
│   └── logging_config.yaml
│
├── data/
│   ├── schema.json
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       ├── train.jsonl
│       └── val.jsonl
│
├── src/
│   ├── __init__.py
│   ├── version.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── preprocessor.py
│   │   ├── validator.py
│   │   ├── deduplicator.py
│   │   └── quality_scorer.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── qlora_trainer.py
│   │   ├── dpo_trainer.py
│   │   ├── merge_adapter.py
│   │   ├── model_registry.py
│   │   └── warmup.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── llm_as_judge.py
│   │   ├── safety_eval.py
│   │   └── evaluate.py
│   │
│   ├── serving/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── engine.py
│   │   ├── schemas.py
│   │   ├── middleware.py
│   │   ├── cache.py
│   │   ├── quota.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── generate.py
│   │       ├── chat.py
│   │       ├── models.py
│   │       ├── health.py
│   │       ├── metrics.py
│   │       └── admin.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   │           └── .gitkeep
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config_parser.py
│       ├── logger.py
│       ├── security.py
│       ├── auth.py
│       ├── secrets.py
│       ├── rate_limiter.py
│       ├── circuit_breaker.py
│       ├── retry.py
│       ├── metrics.py
│       ├── tracing.py
│       └── exceptions.py
│
├── docker/
│   ├── Dockerfile.train
│   ├── Dockerfile.serve
│   ├── Dockerfile.dev
│   └── docker-compose.yml
│
├── deployment/
│   ├── k8s/
│   │   ├── namespace.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   ├── networkpolicy.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── ingress.yaml
│   │   └── servicemonitor.yaml
│   └── helm/
│       └── llm-forge/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│               ├── _helpers.tpl
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── hpa.yaml
│               ├── configmap.yaml
│               ├── secret.yaml
│               ├── ingress.yaml
│               ├── serviceaccount.yaml
│               └── servicemonitor.yaml
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alert_rules.yml
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/
│   │   │   │   └── prometheus.yml
│   │   │   └── dashboards/
│   │   │       └── dashboards.yml
│   │   └── dashboards/
│   │       └── llm_forge.json
│   ├── loki/
│   │   └── loki-config.yml
│   └── otel/
│       └── otel-collector.yml
│
├── scripts/
│   ├── run_training.sh
│   ├── run_serving.sh
│   ├── download_model.py
│   ├── rotate_api_keys.py
│   ├── benchmark.py
│   ├── seed_db.py
│   └── smoke_test.sh
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_security.py
│   ├── test_auth.py
│   ├── test_api.py
│   ├── test_data.py
│   ├── test_cache.py
│   ├── test_metrics.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_end_to_end.py
│   └── load/
│       ├── __init__.py
│       └── locustfile.py
│
├── checkpoints/
│   └── .gitkeep
│
├── models/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
└── docs/
    ├── ARCHITECTURE.md
    ├── SECURITY.md
    ├── API.md
    ├── RUNBOOK.md
    ├── THREAT_MODEL.md
    ├── DEPLOYMENT.md
    ├── DEVELOPMENT.md
    └── CHANGELOG_GUIDE.md
```

---

## Quick Start

### Prerequisites

- Python 3.11 or newer
- Docker 24+ (for local services)
- NVIDIA GPU with CUDA 12.x (for training and serving tests)
- Git
- Make

### 1. Clone and Configure

```bash
git clone https://github.com/yourorg/llm-forge.git
cd llm-forge
cp .env.example .env

# Generate secrets
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "API_KEY=$(openssl rand -hex 24)" >> .env
echo "REQUEST_SIGNING_KEY=$(openssl rand -hex 24)" >> .env

# Edit .env and set:
#   HF_TOKEN=<your huggingface token>
#   WANDB_API_KEY=<your w&b key>
#   MODEL_ID=meta-llama/Meta-Llama-3-8B  (or your base model)
#   MERGED_MODEL_PATH=/models/merged
```

### 2. Install

```bash
pip install -r requirements-dev.txt
pre-commit install
```

### 3. Verify

```bash
make lint typecheck test security-scan
```

### 4. Prepare Data

Place your instruction-tuning data in Alpaca format at `data/processed/train.jsonl`:

```json
{"instruction": "What is the capital of France?", "input": "", "output": "Paris is the capital of France."}
{"instruction": "Summarize the following text.", "input": "LLM-Forge is a pipeline for fine-tuning open-source models.", "output": "LLM-Forge fine-tunes open-source LLMs."}
```

Then create a validation split at `data/processed/val.jsonl`.

### 5. Train (needs 24 GB or more VRAM)

```bash
make train
make merge
```

Training writes to `./checkpoints/final` (LoRA adapter). Merging writes to `./models/merged`.

### 6. Evaluate

```bash
python -m src.evaluation.evaluate ./models/merged data/processed/val.jsonl
```

Reports are written to `./reports/eval.json`. The script exits non-zero if any configured gate fails.

### 7. Serve Locally

```bash
# Using Docker Compose (includes Redis + Postgres + API)
docker compose -f docker/docker-compose.yml up -d --build

# Verify
bash scripts/smoke_test.sh

# Or run directly
export MERGED_MODEL_PATH=./models/merged
bash scripts/run_serving.sh
```

### 8. Test the API

```bash
curl -X POST http://localhost:8000/generate \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is LLM-Forge?", "max_tokens": 100}'
```

### 9. Deploy to Kubernetes

```bash
kubectl create namespace llm-forge
kubectl create secret generic llm-forge-secrets -n llm-forge --from-env-file=.env
helm install llm-forge deployment/helm/llm-forge -n llm-forge \
  --set image.repository=ghcr.io/yourorg/llm-forge \
  --set image.tag=2.0.0 \
  --wait --timeout=15m
```

### 10. Verify Deployment

```bash
kubectl rollout status deploy/llm-forge -n llm-forge --timeout=15m
curl -sf https://api.yourdomain.com/health/ready
```

---

## Configuration

All runtime configuration is via environment variables (see `.env.example`) and YAML files under `configs/`.

### Environment Variables (summary)

| Variable | Purpose | Required |
|---|---|---|
| ENV | dev, test, prod (prod disables /docs) | Yes |
| MODEL_ID | HuggingFace base model ID | Yes |
| MERGED_MODEL_PATH | Path to merged model weights (serving) | Yes |
| HF_TOKEN | HuggingFace token (gated models) | Yes (for gated) |
| API_KEY | Static API key (32+ chars) for admin and service auth | Yes |
| JWT_SECRET_KEY | JWT signing key (32+ chars) | Yes |
| REQUEST_SIGNING_KEY | HMAC signing key (32+ chars) | Yes |
| WANDB_API_KEY | Weights and Biases API key | Training only |
| DATABASE_URL | PostgreSQL DSN (asyncpg) | Yes for auth |
| REDIS_URL | Redis DSN (rate limit, quota) | Optional |
| CACHE_REDIS_URL | Redis DSN for cache (defaults to REDIS_URL) | Optional |
| VLLM_MAX_MODEL_LEN | Max total tokens (prompt + completion) | Yes |
| VLLM_GPU_MEMORY_UTILIZATION | Fraction of GPU memory for KV cache | Yes |
| VLLM_TENSOR_PARALLEL_SIZE | Number of GPUs for tensor parallelism | Yes |
| VLLM_MAX_NUM_SEQS | Max concurrent sequences | Yes |
| RATE_LIMIT_PER_MINUTE | Per-IP rate limit | Yes |
| REQUEST_TIMEOUT_SECONDS | Per-request generation timeout | Yes |
| ENABLE_PII_REDACTION | Toggle Presidio redaction | Yes |
| ENABLE_PROMPT_INJECTION_FILTER | Toggle injection detection | Yes |
| ALLOWED_ORIGINS | CORS origins (comma-separated) | Optional |
| IP_ALLOWLIST | Comma-separated CIDRs | Optional |
| OTEL_ENABLED | Enable OpenTelemetry | Optional |
| OTEL_EXPORTER_OTLP_ENDPOINT | OTLP collector endpoint | Optional |
| VAULT_ENABLED | Enable HashiCorp Vault secrets | Optional |
| VAULT_ADDR | Vault address | Optional |
| VAULT_TOKEN | Vault token | Optional |

### Config Files

| File | Purpose |
|---|---|
| configs/training_config.yaml | QLoRA + DPO hyperparameters |
| configs/serving_config.yaml | vLLM engine + generation + cache + limits |
| configs/security_config.yaml | JWT, RBAC roles, quotas, filters |
| configs/eval_config.yaml | Metric gates, LLM-as-judge, safety probes |
| configs/logging_config.yaml | Logging format (JSON) |

---

## Security Highlights

- Constant-time API key comparison using `hmac.compare_digest` on SHA-256 hashes
- HMAC-SHA256 request signing for inter-service calls (with timestamp replay protection)
- JWT with aud / iss / exp / type validation, short TTL
- RBAC scopes per role (admin, developer, readonly, service)
- Per-IP and per-tenant rate limiting (Redis sliding window)
- Per-tenant daily quotas for requests and tokens
- PII redaction via Microsoft Presidio (configurable entities)
- Prompt-injection detection (configurable regex patterns)
- Secret scrubbing in structlog processor (authorization, api_key, token, password, hf_*, sk-*)
- NUL and control character stripping in sanitize_text
- Non-root container (UID 10001), read-only rootfs, dropped capabilities, seccomp RuntimeDefault
- NetworkPolicy default-deny
- SealedSecrets / External Secrets Operator compatible
- Audit log channel with request_id + user_id correlation
- HSTS, CSP, X-Frame-Options, X-Content-Type-Options headers
- Gitleaks + detect-secrets in pre-commit and CI

See [docs/SECURITY.md](docs/SECURITY.md) and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for full details.

---

## Testing

### Unit and Integration Tests

```bash
make test              # unit tests + coverage
make test-cov          # HTML coverage report
make lint              # ruff + mypy
make format            # black + ruff --fix
make security-scan     # pip-audit + bandit
```

### Integration Tests (against a running server)

```bash
BASE_URL=http://localhost:8000 pytest tests/integration -v
```

### Load Tests

```bash
# Requires running server
API_KEY=<your_key> locust -f tests/load/locustfile.py --host http://localhost:8000

# Headless mode
make benchmark
```

### GPU Tests

```bash
RUN_GPU_TESTS=1 pytest tests/test_engine.py -v
```

---

## Deployment Options

| Option | Use Case | Command |
|---|---|---|
| Docker Compose | Local dev with Redis + Postgres | `docker compose -f docker/docker-compose.yml up -d` |
| Single container | Quick test | `docker run --gpus all --env-file .env -p 8000:8000 llm-forge:latest` |
| K3s / k3d | Staging, single-node | `helm install llm-forge deployment/helm/llm-forge -n llm-forge` |
| EKS / GKE | Production | See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |

---

## Monitoring

### Prometheus Metrics

Key metrics exposed on `/metrics`:

| Metric | Type | Description |
|---|---|---|
| llmforge_http_requests_total | Counter | Requests by method, path, status |
| llmforge_http_request_duration_seconds | Histogram | Request latency by method, path |
| llmforge_tokens_in_total | Counter | Input tokens by tenant, model |
| llmforge_tokens_out_total | Counter | Output tokens by tenant, model |
| llmforge_generation_duration_seconds | Histogram | Time spent in vLLM engine |
| llmforge_inflight_requests | Gauge | In-flight generation requests |
| llmforge_safety_blocks_total | Counter | Safety-blocked requests |
| llmforge_rate_limited_total | Counter | Rate-limited requests |
| llmforge_quota_exceeded_total | Counter | Quota-exceeded requests |
| llmforge_cache_hits_total | Counter | Cache hits |
| llmforge_cache_misses_total | Counter | Cache misses |
| llmforge_circuit_state | Gauge | Circuit breaker state (0=closed, 1=half, 2=open) |

### Grafana Dashboard

Import `monitoring/grafana/dashboards/llm_forge.json` into Grafana.

Panels include:

- Request rate by path
- P50 / P95 / P99 latency
- Tokens per second
- Cache hit rate
- Safety blocks (5m)
- Circuit breaker state
- GPU utilization (via vLLM metrics)

### Alerts

Pre-built alerts in `monitoring/prometheus/alert_rules.yml`:

- HighP95Latency (p95 > 5s for 5m)
- HighErrorRate (5xx > 5% for 5m)
- ModelNotReady (up == 0 for 3m)
- CircuitOpen (circuit state == 2 for 2m)
- QuotaBurningFast (quota exceeded rate > 1/10m)
- HighSafetyBlockRate (safety blocks > 5/min for 5m)

### Tracing

OpenTelemetry traces are exported via OTLP/gRPC to `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://otel-collector:4317`). Spans auto-instrument FastAPI routes and SQLAlchemy queries.

### Logs

Structured JSON logs. Each line includes:

- timestamp (ISO 8601 UTC)
- level
- event (message)
- request_id
- user_id
- Additional contextual fields

Shipped to Loki via Promtail (or your log aggregator of choice).

---

## Documentation

| Document | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, data flow, scaling strategy, design decisions |
| [docs/SECURITY.md](docs/SECURITY.md) | Security posture, controls, incident response, compliance |
| [docs/API.md](docs/API.md) | Complete endpoint reference with request/response schemas |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | On-call playbook for common failure modes |
| [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) | STRIDE threat analysis and attack trees |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Local, K3s, EKS, GKE deployment guide |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Developer setup, workflows, debugging |
| [docs/CHANGELOG_GUIDE.md](docs/CHANGELOG_GUIDE.md) | Changelog format and release process |

---

## Roadmap

- [ ] vLLM multi-LoRA adapter hot-swap (serve multiple fine-tuned adapters on one base model)
- [ ] pgvector-based semantic cache (embedding similarity instead of exact hash)
- [ ] Guardrails AI integration (structured output validation)
- [ ] OpenAI function calling / tool use compatibility
- [ ] RAG pipeline with pluggable retriever interface
- [ ] Model distillation (small student from large teacher)
- [ ] Triton Inference Server backend option
- [ ] SGLang backend option
- [ ] Prompt template versioning and A/B testing
- [ ] Multi-region failover

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, commit conventions, and the review process.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines.

### Quick Contribution Checklist

1. Fork the repo and create a feature branch
2. Run `make install-dev` and `pre-commit install`
3. Make your changes with tests
4. Run `make lint typecheck test security-scan`
5. Commit using Conventional Commits
6. Open a pull request with a clear description

---

## License

MIT License. See [LICENSE](LICENSE).

Copyright (c) 2026 LLM-Forge Contributors.

---

## Acknowledgments

- [vLLM](https://github.com/vllm-project/vllm) for the high-throughput inference engine
- [HuggingFace](https://huggingface.co/) for Transformers, PEFT, TRL, Datasets, Accelerate, and Safetensors
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [Presidio](https://microsoft.github.io/presidio/) for PII redaction
- [Redis](https://redis.io/) and [PostgreSQL](https://www.postgresql.org/) for state
- [Prometheus](https://prometheus.io/), [Grafana](https://grafana.com/), [Loki](https://grafana.com/oss/loki/), [Tempo](https://grafana.com/oss/tempo/), and [OpenTelemetry](https://opentelemetry.io/) for observability
- [Weights and Biases](https://wandb.ai/) for experiment tracking
- [Cloudflare](https://www.cloudflare.com/) for edge and WAF
- [Let's Encrypt](https://letsencrypt.org/) for TLS certificates
```
```

