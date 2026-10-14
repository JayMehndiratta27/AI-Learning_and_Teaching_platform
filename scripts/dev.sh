#!/usr/bin/env bash
# Start Mongo (if Docker is available), restart API on :8000, and Angular on :4200.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Project root: $ROOT"

if command -v docker >/dev/null 2>&1; then
  echo "==> Starting MongoDB (docker compose)…"
  docker compose up -d 2>/dev/null || echo "    (docker compose skipped or failed — ensure Mongo is on localhost:27017)"
else
  echo "==> Docker not found — start MongoDB yourself (e.g. mongod or Atlas URI in backend/.env)"
fi

echo "==> Freeing port 8000 (old backend)…"
if command -v lsof >/dev/null 2>&1; then
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  echo "ERROR: backend/.venv missing. Run: cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

cleanup() {
  echo ""
  echo "==> Shutting down backend…"
  if [[ -n "${UVICORN_PID:-}" ]] && kill -0 "$UVICORN_PID" 2>/dev/null; then
    kill "$UVICORN_PID" 2>/dev/null || true
    wait "$UVICORN_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "==> Starting backend (http://localhost:8000)…"
cd "$ROOT/backend"
# shellcheck disable=SC1091
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
cd "$ROOT"

sleep 1
if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
  echo "ERROR: Backend did not start. Check backend/.venv and dependencies."
  exit 1
fi

echo "==> Starting frontend (http://localhost:4200)…"
cd "$ROOT/frontend"
npx ng serve --open
