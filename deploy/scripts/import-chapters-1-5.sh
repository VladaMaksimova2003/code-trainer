#!/usr/bin/env bash
# Import curriculum chapters 1–5 (40 tasks) into PostgreSQL.
# Full course (128 tasks): ./deploy/scripts/import-curriculum-128.sh
# Run on the server after deploy, from repo root:
#   chmod +x deploy/scripts/import-chapters-1-5.sh
#   ./deploy/scripts/import-chapters-1-5.sh
#
# Optional:
#   ENV_FILE=backend/deploy/.env.prod
#   NO_REPLACE=1          — pass --no-replace to each import (keep existing rows)
#   TEACHER_EMAIL=...     — owner email for imported tasks
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-backend/deploy/.env.prod}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

IMPORT_ARGS=()
if [[ "${NO_REPLACE:-0}" == "1" ]]; then
  IMPORT_ARGS+=(--no-replace)
fi
if [[ -n "${TEACHER_EMAIL:-}" ]]; then
  IMPORT_ARGS+=(--teacher-email "$TEACHER_EMAIL")
fi

run_import() {
  local script="$1"
  local label="$2"
  echo ""
  echo "==> $label ($script)"
  "${COMPOSE[@]}" run --rm --no-deps api python "scripts/$script" "${IMPORT_ARGS[@]}"
}

echo "==> Importing chapters 1–5 into production database"
echo "    ENV_FILE=$ENV_FILE"
if [[ "${#IMPORT_ARGS[@]}" -gt 0 ]]; then
  echo "    extra args: ${IMPORT_ARGS[*]}"
fi

run_import import_algo_basics_ch1.py "Chapter 1 — algo basics"
run_import import_branches_ch2.py "Chapter 2 — branches"
run_import import_loops_ch3.py "Chapter 3 — loops"
run_import import_arrays_ch4.py "Chapter 4 — arrays"
run_import import_strings_ch5.py "Chapter 5 — strings"

echo ""
echo "Done. Hints/MPLT banners are in the API image — restart if api was already running:"
echo "  ${COMPOSE[*]} restart api worker"
echo "Smoke: ./deploy/scripts/smoke-prod.sh"
