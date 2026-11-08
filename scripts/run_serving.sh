#!/usr/bin/env bash
set -euo pipefail
: "${API_KEY:?Set API_KEY (>=32 chars)}"
exec uvicorn src.serving.app:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --timeout-keep-alive 75 \
  --no-access-log
