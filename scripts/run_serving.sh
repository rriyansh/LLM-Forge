#!/usr/bin/env bash
set -Eeuo pipefail

: "${API_KEY:?Set API_KEY (>=32 chars)}"
: "${JWT_SECRET_KEY:?Set JWT_SECRET_KEY (>=32 chars)}"

export PYTHONPATH="${PYTHONPATH:-$(pwd)}"

exec uvicorn src.serving.app:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --timeout-keep-alive 75 \
  --no-access-log \
  --loop uvloop \
  --http httptools
