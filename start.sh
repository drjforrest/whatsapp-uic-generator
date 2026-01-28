#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"

uvicorn app.main:app --host "$HOST" --port "$PORT"
