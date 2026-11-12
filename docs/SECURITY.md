
# Security Posture

<p align="left">
  <img src="https://img.shields.io/badge/security-hardened-critical?style=flat-square&logo=shieldsdotio&logoColor=white" alt="Hardened" />
  <img src="https://img.shields.io/badge/version-2.0.0-2ea44f?style=flat-square" alt="Version 2.0.0" />
  <img src="https://img.shields.io/badge/review-quarterly-orange?style=flat-square&logo=calendar&logoColor=white" alt="Review Quarterly" />
  <img src="https://img.shields.io/badge/contact-security%40llmforge.dev-red?style=flat-square&logo=gmail&logoColor=white" alt="Contact" />
</p>

This document describes LLM-Forge's security architecture, controls, and
incident response procedures. It is intended for engineers, SREs, security
reviewers, and auditors who need to understand how the system protects data,
enforces access, and responds to incidents.

The document follows a defense-in-depth model: no single control is trusted
alone, and every control fails safe by default.

---

## Table of Contents

| | Section |
|---|---|
| ▸ | [Threat Model Summary](#threat-model-summary) |
| ▸ | [Authentication](#authentication) |
| ▸ | [Authorization (RBAC)](#authorization-rbac) |
| ▸ | [Input Validation and Sanitization](#input-validation-and-sanitization) |
| ▸ | [Rate Limiting and Quotas](#rate-limiting-and-quotas) |
| ▸ | [Secrets Management](#secrets-management) |
| ▸ | [Container and Runtime Security](#container-and-runtime-security) |
| ▸ | [Transport Security](#transport-security) |
| ▸ | [HTTP Security Headers](#http-security-headers) |
| ▸ | [Logging and Audit](#logging-and-audit) |
| ▸ | [Incident Response](#incident-response) |
| ▸ | [Compliance](#compliance) |
| ▸ | [Reporting Vulnerabilities](#reporting-vulnerabilities) |

---

## Threat Model Summary

<p align="left">
  <img src="https://img.shields.io/badge/stride-full%20analysis-red?style=flat-square&logo=owasp&logoColor=white" alt="STRIDE" />
  <img src="https://img.shields.io/badge/owasp-llm%20top%2010-purple?style=flat-square&logo=owasp&logoColor=white" alt="OWASP LLM Top 10" />
  <img src="https://img.shields.io/badge/mitre-atlas-blue?style=flat-square&logo=mitre&logoColor=white" alt="MITRE ATLAS" />
</p>

The full STRIDE threat model is documented in [THREAT_MODEL.md](THREAT_MODEL.md).
The highest-risk threats and their primary mitigations are:

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| Forged JWT | Spoofing | HS256 with 32+ byte secret, `aud`/`iss`/`exp` validation | Low |
| Prompt injection | Information disclosure | Regex filter + PII redaction + optional ML classifier | Medium |
| API key theft | Spoofing | Constant-time comparison, 32+ char minimum, rotation | Low |
| DDoS request flood | Denial of service | Per-IP rate limit, per-tenant quota, WAF | Low |
| Cross-tenant data leak | Information disclosure | Tenant-scoped cache keys (planned), scoped quotas | Medium |
| Model extraction | Information disclosure | Rate limits, quota cost | Medium |
| Supply chain attack | Tampering | `pip-audit`, `gitleaks`, pinned versions, signed images (planned) | Low |
| Container escape | Elevation | Non-root, read-only rootfs, dropped capabilities, seccomp | Low |

See [THREAT_MODEL.md](THREAT_MODEL.md) for the complete analysis including
attack trees and residual risk assessment.

---

## Authentication

<p align="left">
  <img src="https://img.shields.io/badge/jwt-HS256-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
  <img src="https://img.shields.io/badge/api%20key-sha256-blue?style=for-the-badge&logo=keycdn&logoColor=white" alt="API Key" />
  <img src="https://img.shields.io/badge/hmac-sha256-purple?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="HMAC" />
</p>

LLM-Forge supports three authentication mechanisms, each with a distinct use
case. All three fail closed: missing or malformed credentials are rejected
with HTTP 401.

### JWT (user sessions)

| Property | Value | Notes |
|---|---|---|
| Algorithm | HS256 (HMAC-SHA256) | Rotating the secret invalidates all tokens |
| Signing key | `JWT_SECRET_KEY` | Minimum 32 characters; app refuses to start otherwise |
| Access token TTL | 1 hour | Configurable via `JWT_ACCESS_TTL_SECONDS` |
| Refresh token TTL | 7 days | Configurable via `JWT_REFRESH_TTL_SECONDS` |
| Claims | `sub`, `role`, `tenant`, `iat`, `nbf`, `exp`, `iss`, `aud`, `type` | All validated on decode |
| Issuer | `llm-forge` | Validated |
| Audience | `llm-forge-api` | Validated |
| Type check | `access` vs `refresh` | Access rejected on refresh endpoints and vice versa |

Validation is performed by `decode_token()`:

```python
jwt.decode(
    token,
    secret,
    algorithms=["HS256"],
    issuer="llm-forge",
    audience="llm-forge-api",
    options={"require_exp": True},
)
```

If validation fails for any reason (expired, wrong issuer, wrong audience,
wrong type, bad signature), the request is rejected with a generic 401 and
an `auth_failure` audit event.

### API keys (service-to-service)

| Property | Value | Notes |
|---|---|---|
| Header | `Authorization: Bearer <key>` or `X-API-Key: <key>` | Either accepted |
| Storage | SHA-256 hash only | Never plaintext in DB |
| Comparison | `hmac.compare_digest(sha256(provided), sha256(expected))` | Constant-time |
| Minimum length | 32 characters | Startup fails otherwise |
| Rotation | `scripts/rotate_api_keys.py` | Manual or scheduled |

The comparison is deliberately constant-time on the SHA-256 of both values to
prevent timing side channels that could reveal the key one byte at a time.

### HMAC request signing (inter-service)

For high-trust service-to-service calls, the API key alone is insufficient.
Callers must also sign the request body with a shared secret:

```text
X-Timestamp: <unix_seconds>
X-Signature: hex(HMAC-SHA256(REQUEST_SIGNING_KEY, f"{ts}.{body}"))
```

| Property | Value | Notes |
|---|---|---|
| Secret | `REQUEST_SIGNING_KEY` | Minimum 32 characters |
| Skew tolerance | 300 seconds | Rejects replayed requests |
| Verification | `verify_request_signature(body, sig, ts)` | Constant-time compare |

Both the timestamp and the signature must be present, and the timestamp must
be within 300 seconds of the server's clock. Clock skew beyond this window is
rejected as a potential replay.

---

## Authorization (RBAC)

<p align="left">
  <img src="https://img.shields.io/badge/rbac-scopes-blue?style=for-the-badge&logo=auth0&logoColor=white" alt="RBAC" />
  <img src="https://img.shields.io/badge/roles-4%20levels-green?style=for-the-badge&logo=keycdn&logoColor=white" alt="Roles" />
</p>

Authorization is enforced at the route level via the `require_scopes()`
dependency. Roles are defined in `configs/security_config.yaml` and are
immutable at runtime.

| Role | Scopes | Typical Use |
|---|---|---|
| `admin` | `*` (all) | Internal operators |
| `developer` | `generate`, `chat`, `models:list`, `metrics:read` | Application developers |
| `readonly` | `models:list`, `health` | Monitoring, dashboards |
| `service` | `generate`, `chat`, `metrics:write` | Internal microservices |

Enforcement example:

```python
@router.post("/generate")
async def generate(
    body: GenerateRequest,
    principal: Principal = Depends(require_scopes("generate")),
) -> GenerateResponse:
    ...
```

If the principal's role does not include the required scope, the request is
rejected with HTTP 403 and the missing scopes are logged (in the audit
channel only, not in the response body).

### Admin endpoints

Paths under `/admin/*` are gated by `AdminAPIKeyMiddleware`. These endpoints
accept **only** the static `API_KEY`, never a JWT. This prevents privilege
escalation via a stolen user token.

| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/status` | GET | Engine status and environment |
| `/admin/reload` | POST | Reload the vLLM engine |
| `/admin/circuit/{name}` | GET | Inspect a circuit breaker's state |

---

## Input Validation and Sanitization

<p align="left">
  <img src="https://img.shields.io/badge/pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
  <img src="https://img.shields.io/badge/presidio-pii%20redaction-0078D4?style=for-the-badge&logo=microsoft&logoColor=white" alt="Presidio" />
  <img src="https://img.shields.io/badge/regex-injection%20filter-orange?style=for-the-badge&logo=regex&logoColor=white" alt="Regex" />
</p>

Every request body is validated against a Pydantic model before any
processing. Fields have explicit `min_length`, `max_length`, `ge`, `le`, and
`pattern` constraints.

### Body size limit

| Control | Value | Enforcement |
|---|---|---|
| HTTP body cap | 1 MB | `BodySizeLimitMiddleware` |
| Prompt length | 32,000 chars | `GenerateRequest.prompt` |
| Message count | 64 | `ChatRequest.messages` |
| Message length | 32,000 chars | `ChatMessage.content` |
| Stop sequences | 8 | `GenerateRequest.stop` |
| Max completion | 4,096 tokens | `GenerateRequest.max_tokens` |
| Model context | `VLLM_MAX_MODEL_LEN` | Engine-level |

Requests exceeding any of these limits are rejected with HTTP 422 and a
generic `validation_error` response.

### Control character stripping

```python
def sanitize_text(text: str, *, max_len: int = 32_000) -> str:
    if not text:
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:max_len]
```

This removes NUL bytes, escape sequences, and other control characters that
could cause log injection, terminal escape sequence attacks, or tokenizer
truncation. Newlines and tabs are preserved.

### Prompt injection detection

Heuristic regex filter configured in `configs/security_config.yaml`:

```yaml
filters:
  injection:
    enabled: true
    patterns:
      - "(?i)ignore\\s+(all\\s+)?(previous|above)\\s+instructions"
      - "(?i)disregard\\s+the\\s+(system|previous)\\s+prompt"
      - "(?i)reveal\\s+(your\\s+)?(system\\s+prompt|instructions|hidden\\s+prompt)"
      - "(?i)you\\s+are\\s+now\\s+(a|an|the)\\s+"
      - "(?i)</?system>"
      - "(?i)\\[\\[?\\s*system\\s*\\]\\]?"
      - "(?i)repeat\\s+the\\s+above"
      - "(?i)print\\s+(all\\s+)?(your\\s+)?(initial|system)\\s+(prompt|message)"
```

When a prompt matches any pattern:

1. The request is rejected with HTTP 400 `safety_violation`
2. An `audit.safety_blocked` event is emitted with the user ID and pattern ID
3. `llmforge_safety_blocks_total{reason="injection"}` is incremented

**Limitation**: regex filters are bypassable with obfuscation, encoding, or
translation. This is a defense-in-depth layer, not a complete solution. A
trained ML classifier is planned (see Roadmap).

### PII redaction (Presidio)

Microsoft Presidio's `AnalyzerEngine` and `AnonymizerEngine` detect and redact
PII before the prompt reaches the model:

| Entity | Detection | Replacement |
|---|---|---|
| `EMAIL_ADDRESS` | Regex + NER | `<EMAIL_ADDRESS>` |
| `PHONE_NUMBER` | Regex + NER | `<PHONE_NUMBER>` |
| `CREDIT_CARD` | Luhn + regex | `<CREDIT_CARD>` |
| `PERSON` | NER (spaCy) | `<PERSON>` |
| `US_SSN` | Regex | `<US_SSN>` |
| `IBAN_CODE` | Regex | `<IBAN_CODE>` |

| Property | Value | Notes |
|---|---|---|
| Toggle | `ENABLE_PII_REDACTION=true` | On by default in prod |
| Failure mode | Fail-open | Presidio error logs a warning and passes the text through |
| Performance | ~20-50ms per request | Offloaded to a thread pool if needed |

PII redaction **fails open** deliberately: a Presidio failure should not
break availability. The trade-off is documented, and the failure is logged.

---

## Rate Limiting and Quotas

<p align="left">
  <img src="https://img.shields.io/badge/redis-sliding%20window-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/quota-per%20tenant-orange?style=for-the-badge&logo=speedtest&logoColor=white" alt="Quota" />
  <img src="https://img.shields.io/badge/concurrency-semaphore-blue?style=for-the-badge&logo=python&logoColor=white" alt="Semaphore" />
</p>

Three independent mechanisms protect the GPU from abuse:

### Per-IP rate limit

| Property | Value | Notes |
|---|---|---|
| Backend | Redis sorted-set sliding window | O(log N) per request |
| Fallback | In-memory deque | Single replica only, fail-open |
| Default | 60 requests per minute | Configurable via `RATE_LIMIT_PER_MINUTE` |
| Key | Client IP | Respects `X-Forwarded-For` from trusted ingress |
| Response | HTTP 429 with `Retry-After` header | Also increments `llmforge_rate_limited_total` |

The Redis implementation uses `ZADD` with millisecond timestamps and
`ZREMRANGEBYSCORE` to evict old entries:

```text
1. ZREMRANGEBYSCORE rl:<key> 0 <now - window>
2. ZADD rl:<key> <now> <unique_id>
3. ZCARD rl:<key>
4. EXPIRE rl:<key> <window + 1>
```

If `ZCARD > limit`, the request is rejected and the retry delay is computed
from the oldest entry in the sorted set.

### Per-tenant daily quota

| Property | Value | Notes |
|---|---|---|
| Backend | Redis `INCRBY` with `EXPIRE` | Daily reset at 00:00 UTC |
| Metric | `requests_per_day` and `tokens_per_day` | Both enforced |
| Tiers | `default` and `premium` | See `configs/security_config.yaml` |
| Response | HTTP 402 with error code `quota_exceeded` | Also increments `llmforge_quota_exceeded_total` |

The quota is consumed twice per request: once for the request count, and again
after generation for the token count. If Redis is unreachable, the check
**fails open**: availability is prioritized over strict quota enforcement.

### Per-replica concurrency cap

| Property | Value | Notes |
|---|---|---|
| Mechanism | `asyncio.Semaphore(max_concurrent_requests)` | Default 128 |
| Behavior | Queue grows; requests time out after `REQUEST_TIMEOUT_SECONDS` | Backpressure |
| Purpose | Prevents GPU queue overflow and memory exhaustion | Complements rate limits |

The semaphore is the last line of defense: even if rate limits and quotas are
misconfigured, the engine will not accept more than `max_concurrent_requests`
in-flight generations.

---

## Secrets Management

<p align="left">
  <img src="https://img.shields.io/badge/vault-hashicorp-000000?style=for-the-badge&logo=vault&logoColor=white" alt="Vault" />
  <img src="https://img.shields.io/badge/sealed%20secrets-kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="SealedSecrets" />
  <img src="https://img.shields.io/badge/external%20secrets-operator-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="External Secrets" />
</p>

Secrets are resolved from environment variables first, then from HashiCorp
Vault if enabled. Critical secrets have no defaults; the application refuses
to start if they are missing.

### Required secrets

| Secret | Minimum Length | Purpose | Default |
|---|---|---|---|
| `API_KEY` | 32 | Static API key for admin and service auth | None (fail) |
| `JWT_SECRET_KEY` | 32 | JWT signing | None (fail) |
| `REQUEST_SIGNING_KEY` | 32 | HMAC request signing | None (fail) |
| `HF_TOKEN` | 10 | HuggingFace access (gated models) | None (warn) |
| `WANDB_API_KEY` | 10 | Weights & Biases tracking | None (warn) |

### Rules

| ▸ | No defaults for critical secrets. App fails to start if missing. |
|---|---|
| ▸ | Minimum lengths enforced at startup (`JWT_SECRET_KEY >= 32`, `API_KEY >= 32`). |
| ▸ | Secrets are never logged. The structlog processor scrubs `authorization`, `api_key`, `token`, `password`, `secret`, `hf_*`, `sk-*`. |
| ▸ | `.env`, `*.pem`, `*.key`, `secrets/` are gitignored. |
| ▸ | `gitleaks` and `detect-secrets` run in pre-commit and CI. |

### Kubernetes secret sources

| Approach | Best For | Notes |
|---|---|---|
| `kubectl create secret` | Development, quick tests | Not recommended for production |
| SealedSecrets | GitOps workflows | Encrypted with a cluster key, safe to commit |
| External Secrets Operator | Vault/AWS/GCP integration | Reads from external store, refreshes periodically |

Secrets are mounted as `envFrom: secretRef`, not as files. This avoids leaking
secret content via `/proc`, container dumps, or accidental `ls` in logs.

---

## Container and Runtime Security

<p align="left">
  <img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/seccomp-runtime%20default-red?style=for-the-badge&logo=linux&logoColor=white" alt="Seccomp" />
</p>

Every container runs with the minimum privileges required to serve traffic.

### Image hardening

| Control | Implementation |
|---|---|
| Multi-stage build | Only runtime deps in final image |
| Non-root user | `USER 10001` |
| No build tools | `apt-get remove` after install |
| No `.git` directory | `.dockerignore` excludes it |
| Pinned base image | Specific SHA, not `latest` |
| Vulnerability scan | `trivy` in CI (planned) |
| Image signing | `cosign` in CI (planned) |

### Pod security context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
```

### Container security context

```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```

| Control | Effect |
|---|---|
| `readOnlyRootFilesystem` | Writes only to `/tmp` (tmpfs) and `/app/.cache` (emptyDir) |
| `allowPrivilegeEscalation: false` | Prevents `setuid` escalation |
| `capabilities: drop ALL` | No Linux capabilities available |
| `seccompProfile: RuntimeDefault` | Restricts syscalls to a safe subset |
| `automountServiceAccountToken: false` | No K8s API access from the pod |

### Network policy

Default-deny ingress and egress:

| Direction | Allowed From/To | Ports |
|---|---|---|
| Ingress | `ingress-nginx` namespace | 8000 |
| Ingress | `monitoring` namespace | 8000 |
| Egress | Any namespace (DNS) | 53 (TCP/UDP) |
| Egress | `llm-forge` namespace | 5432 (Postgres), 6379 (Redis) |

All other traffic is blocked. This limits lateral movement if the pod is
compromised.

---

## Transport Security

<p align="left">
  <img src="https://img.shields.io/badge/tls-1.2%2B-2ea44f?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="TLS" />
  <img src="https://img.shields.io/badge/hsts-preload-blue?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="HSTS" />
  <img src="https://img.shields.io/badge/cert--manager-auto%20renew-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="cert-manager" />
</p>

| Control | Value |
|---|---|
| Minimum TLS version | 1.2 |
| Certificate authority | Let's Encrypt (via cert-manager) |
| Certificate renewal | Automatic at 2/3 of validity |
| HSTS | `max-age=31536000; includeSubDomains; preload` |
| HTTP to HTTPS | 301 redirect enforced at ingress |
| Internal service calls | Plaintext within cluster (mTLS via service mesh if deployed) |

Internal traffic is plaintext because the network policy restricts egress to
same-namespace services. For stricter isolation, deploy Istio or Linkerd to
add automatic mTLS between pods.

---

## HTTP Security Headers

<p align="left">
  <img src="https://img.shields.io/badge/owasp-secure%20headers-purple?style=for-the-badge&logo=owasp&logoColor=white" alt="OWASP" />
</p>

Every response includes the following headers, applied by
`SecurityHeadersMiddleware`:

| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS for 1 year |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Referrer-Policy` | `no-referrer` | Do not leak referer |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | Disable unused browser APIs |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'` | Deny all resource loading |
| `Cache-Control` | `no-store` | Prevent caching of sensitive responses |

These headers are non-negotiable in production. Any deviation requires an
explicit `# nosemgrep` comment and a security review.

---

## Logging and Audit

<p align="left">
  <img src="https://img.shields.io/badge/structlog-json-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="structlog" />
  <img src="https://img.shields.io/badge/loki-log%20aggregation-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Loki" />
  <img src="https://img.shields.io/badge/audit-worm%20ready-orange?style=for-the-badge&logo=s3&logoColor=white" alt="Audit" />
</p>

### Application logs

| Property | Value |
|---|---|
| Format | JSON (structlog) |
| Correlation | `request_id` and `user_id` on every line |
| Secret scrubbing | Automatic via processor |
| PII | User-provided text is not logged; only token counts, latencies, statuses |
| Destination | stdout, shipped to Loki via Promtail |

Each log line is a single JSON object with keys such as `timestamp`, `level`,
`event`, `request_id`, `user_id`, and additional contextual fields. This makes
the logs machine-parseable by any aggregator.

### Audit log

A separate channel for security-relevant events. These are emitted with the
`audit` logger and include a consistent schema.

| Event | Fields | Purpose |
|---|---|---|
| `auth_success` | `user_id`, `method`, `ip`, `path` | Track successful authentications |
| `auth_failure` | `reason`, `ip`, `path` | Detect brute force |
| `quota_exceeded` | `user_id`, `tier`, `metric` | Detect abuse |
| `safety_blocked` | `user_id`, `reason`, `category` | Track filter hits |
| `admin_action` | `user_id`, `action`, `target` | Audit admin operations |

In production, ship audit logs to a write-once-read-many (WORM) backend such
as S3 Object Lock or QLDB. This ensures that even if an attacker gains
control of the cluster, they cannot tamper with audit history.

### Retention

| Log type | Retention | Storage |
|---|---|---|
| Application logs | 30 days | Loki |
| Audit logs | 1 year | WORM (S3 Object Lock) |
| Metrics | 90 days | Prometheus |
| Traces | 7 days | Tempo |

Retention periods are minimums. Increase them for regulated environments
(healthcare, finance).

---

## Incident Response

<p align="left">
  <img src="https://img.shields.io/badge/on--call-pagerduty-06AC38?style=for-the-badge&logo=pagerduty&logoColor=white" alt="PagerDuty" />
  <img src="https://img.shields.io/badge/runbook-available-blue?style=for-the-badge&logo=readthedocs&logoColor=white" alt="Runbook" />
</p>

Detailed procedures are in [RUNBOOK.md](RUNBOOK.md). The following are the
highest-priority scenarios.

### Suspected API key compromise

```bash
# 1. Rotate master API key
python scripts/rotate_api_keys.py

# 2. Update the K8s secret
kubectl create secret generic llm-forge-secrets -n llm-forge \
  --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

# 3. Restart pods
kubectl rollout restart deploy/llm-forge -n llm-forge

# 4. Audit recent auth events
kubectl logs -l app=llm-forge -n llm-forge | grep auth_failure | tail -100
```

### Suspected JWT secret compromise

Rotate `JWT_SECRET_KEY`. **All existing tokens are invalidated immediately**.
Every user must re-authenticate.

```bash
# Update .env with a new secret
openssl rand -hex 32 >> .env  # paste into JWT_SECRET_KEY
kubectl rollout restart deploy/llm-forge -n llm-forge
```

### Abusive tenant

```sql
-- 1. Deactivate tenant
UPDATE tenants SET active = false WHERE id = 'tenant-id';

-- 2. Revoke all users
UPDATE users SET active = false WHERE tenant_id = 'tenant-id';

-- 3. Revoke all API keys
UPDATE api_keys SET active = false WHERE tenant_id = 'tenant-id';
```

### Active attack (DDoS, injection flood)

| Step | Action |
|---|---|
| 1 | Enable strict IP allowlist: `IP_ALLOWLIST=<trusted CIDRs>` |
| 2 | Scale up: `kubectl scale deploy/llm-forge --replicas=4` |
| 3 | Tighten rate limit: `RATE_LIMIT_PER_MINUTE=10` |
| 4 | Check WAF logs at Cloudflare |
| 5 | Post-mortem within 72 hours |

### Data breach

| Step | Action |
|---|---|
| 1 | Preserve all logs. Do not delete pods. |
| 2 | Isolate the node: `kubectl cordon <node>` |
| 3 | Stop deployment: `kubectl scale deploy/llm-forge --replicas=0` |
| 4 | Notify DPO/legal within 72 hours (GDPR) |
| 5 | Forensics: pull container filesystem, memory dump, network logs |
| 6 | Remediate: rotate all secrets, force password reset |

---

## Compliance

<p align="left">
  <img src="https://img.shields.io/badge/gdpr-ready-blue?style=for-the-badge&logo=europeanunion&logoColor=white" alt="GDPR" />
  <img src="https://img.shields.io/badge/soc%202-ready%2C%20not%20certified-orange?style=for-the-badge&logo=aicpa&logoColor=white" alt="SOC 2" />
  <img src="https://img.shields.io/badge/hipaa-not%20compliant-red?style=for-the-badge&logo=healthcare&logoColor=white" alt="HIPAA" />
</p>

### GDPR

| Control | Implementation |
|---|---|
| Data minimization | Only `user_id`, `tenant`, `tokens`, `latency` logged |
| Right to erasure | `DELETE FROM users WHERE id=...` cascades |
| Data residency | Deploy per-region; no cross-region data flows |
| DPA | Available on request |

### SOC 2

| Control | Implementation |
|---|---|
| Access control | RBAC + audit log |
| Change management | PR review + CI |
| Monitoring | Prometheus + alerts |
| Incident response | Documented in [RUNBOOK.md](RUNBOOK.md) |

The system is **ready** for SOC 2 audit but is **not certified**. The audit
must be performed by an independent CPA firm.

### HIPAA and PCI-DSS

**Not compliant by default.** For PHI or card data workloads:

| Requirement | Action |
|---|---|
| Encryption at rest | Enable full-disk encryption on PVCs |
| Isolation | Dedicated cluster, dedicated namespace |
| BAAs | Sign with all sub-processors (cloud, CDN, LLM provider) |
| Audit retention | 7 years (extend from 1 year) |
| `X-Forwarded-For` trust | Disable if behind untrusted proxies |
| PII redaction | Mandatory (`ENABLE_PII_REDACTION=true`) |

Do not deploy PHI or card data into a default LLM-Forge instance without
completing these steps and consulting a compliance officer.

---

## Reporting Vulnerabilities

<p align="left">
  <img src="https://img.shields.io/badge/security%20email-security%40llmforge.dev-red?style=for-the-badge&logo=gmail&logoColor=white" alt="Security Email" />
  <img src="https://img.shields.io/badge/pgp-available-blue?style=for-the-badge&logo=gnuprivacyguard&logoColor=white" alt="PGP" />
  <img src="https://img.shields.io/badge/response-within%2048h-green?style=for-the-badge&logo=clockify&logoColor=white" alt="48h Response" />
</p>

**Do not open a public issue for security vulnerabilities.**

Email `security@llmforge.dev` with:

| ▸ | A clear description of the vulnerability |
|---|---|
| ▸ | Steps to reproduce |
| ▸ | The affected version(s) |
| ▸ | Potential impact assessment |
| ▸ | Any suggested mitigations |

A PGP key for encrypted reports is available at
`https://llmforge.dev/security.asc`
(fingerprint: `ABCD EFGH IJKL MNOP QRST UVWX YZ01 2345`).

| Commitment | Value |
|---|---|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix timeline | Depends on severity; critical fixes prioritized |
| Credit | Given in changelog unless anonymity requested |

---

## Related Documents

| Document | Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and data flow |
| [THREAT_MODEL.md](THREAT_MODEL.md) | STRIDE threat analysis and attack trees |
| [API.md](API.md) | Endpoint reference |
| [RUNBOOK.md](RUNBOOK.md) | On-call playbook |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Developer setup |
| [CHANGELOG_GUIDE.md](CHANGELOG_GUIDE.md) | Changelog format |
