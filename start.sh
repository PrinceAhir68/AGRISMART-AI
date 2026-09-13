#!/usr/bin/env bash
set -e

PORT=${PORT:-8000}
HOST=${HOST:-"0.0.0.0"}
WORKERS=${WORKERS:-1}

echo "======================================================="
echo " Starting AgriSmart AI Production Server on ${HOST}:${PORT}"
echo "======================================================="

# Ensure isolated upload directory exists
mkdir -p app/isolated_uploads

# Launch FastAPI ASGI server with uvicorn
exec uvicorn app.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"
