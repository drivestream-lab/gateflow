#!/usr/bin/env bash
# Local stack: API + worker (ADR-001). Both load .env from cwd.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  echo "[ERROR] .venv missing — run make setup" >&2
  exit 1
fi

WORKER_PID=""

cleanup() {
  if [[ -n "${WORKER_PID}" ]] && kill -0 "${WORKER_PID}" 2>/dev/null; then
    echo "[INFO] Stopping worker pid=${WORKER_PID}"
    kill "${WORKER_PID}" 2>/dev/null || true
    wait "${WORKER_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "[INFO] Starting worker (src.worker_main) — claims Postgres jobs"
.venv/bin/python -m src.worker_main &
WORKER_PID=$!

echo "[INFO] Starting API (src.main) — Ctrl+C stops API and worker"
.venv/bin/python -m src.main
