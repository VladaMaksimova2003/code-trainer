#!/usr/bin/env bash
# Import all 128 curriculum tasks (16 chapters × 8 tasks) into PostgreSQL.
# Run on the server after deploy, from repo root:
#   chmod +x deploy/scripts/import-full-course-128.sh
#   ./deploy/scripts/import-full-course-128.sh
#
# Chapters 1–5 only (40 tasks): ./deploy/scripts/import-chapters-1-5.sh
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

echo "==> Importing full 128-task course (16 chapters)"
echo "    ENV_FILE=$ENV_FILE"
if [[ "${#IMPORT_ARGS[@]}" -gt 0 ]]; then
  echo "    extra args: ${IMPORT_ARGS[*]}"
fi

run_import import_algo_basics_ch1.py "Chapter 1 — algo basics (tasks 1–8)"
run_import import_branches_ch2.py "Chapter 2 — branches (9–16)"
run_import import_loops_ch3.py "Chapter 3 — loops (17–24)"
run_import import_arrays_ch4.py "Chapter 4 — arrays (25–32)"
run_import import_strings_ch5.py "Chapter 5 — strings (33–40)"
run_import import_functions_ch6.py "Chapter 6 — functions (41–48)"
run_import import_recursion_ch7.py "Chapter 7 — recursion (49–56)"
run_import import_search_sort_ch8.py "Chapter 8 — search & sort (57–64)"
run_import import_aggregation_ch9.py "Chapter 9 — aggregation (65–72)"
run_import import_maps_ch10.py "Chapter 10 — maps (73–80)"
run_import import_files_modules_ch11.py "Chapter 11 — files & modules (81–88)"
run_import import_stack_queue_ch12.py "Chapter 12 — stack & queue (89–96)"
run_import import_linked_lists_ch13.py "Chapter 13 — linked lists (97–104)"
run_import import_trees_graphs_ch14.py "Chapter 14 — trees & graphs (105–112)"
run_import import_oop_ch15.py "Chapter 15 — OOP (113–120)"
run_import import_inheritance_ch16.py "Chapter 16 — inheritance (121–128)"

echo ""
echo "Done. Invalidate API task cache:"
echo "  ${COMPOSE[*]} restart api worker"
echo "Smoke: ./deploy/scripts/smoke-prod.sh"
