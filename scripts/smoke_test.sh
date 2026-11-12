#!/usr/bin/env bash
set -Eeuo pipefail
BASE="${BASE:-http://localhost:8000}"
: "${API_KEY:?Set API_KEY}"

echo ">>> liveness"
curl -sf "${BASE}/health/live" | head -c 200; echo
echo ">>> readiness"
curl -sf "${BASE}/health/ready" | head -c 200; echo
echo ">>> generate (authenticated)"
curl -sf -X POST "${BASE}/generate" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is LLM-Forge?","max_tokens":64}' | head -c 400; echo
echo ">>> SMOKE OK"
