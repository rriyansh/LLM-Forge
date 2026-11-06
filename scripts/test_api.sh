#!/usr/bin/env bash
set -euo pipefail

# curl-based smoke test for the serving API.

HOST="${HOST:-http://localhost:8000}"
API_KEY="${API_KEY:-changeme}"

echo "=== Health check ==="
curl -s "$HOST/health" | python -m json.tool

echo "=== /generate endpoint ==="
curl -s -X POST "$HOST/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"prompt":"Instruction: What is the capital of France?\nOutput:","max_tokens":64}' | python -m json.tool

echo "=== /chat/completions endpoint ==="
curl -s -X POST "$HOST/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"llama-3-8b","messages":[{"role":"user","content":"Hello!"}],"max_tokens":64}' | python -m json.tool

echo "Smoke test complete."
