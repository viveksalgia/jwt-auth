#!/usr/bin/env sh
# Entrypoint for Cloud Run: run migrations then start the app.
set -euo pipefail

echo "[entrypoint] starting uvicorn"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}" --log-level info