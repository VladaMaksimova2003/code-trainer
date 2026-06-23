#!/usr/bin/env bash
# Восстановить PostgreSQL на production из pg_dump (-Fc).
# Запуск на сервере из корня репозитория:
#   chmod +x deploy/scripts/restore-db-on-server.sh
#   ./deploy/scripts/restore-db-on-server.sh backups/db/code_trainer_local_YYYYMMDD_HHMMSS.dump
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-backend/deploy/.env.prod}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

DUMP="${1:-}"
if [[ -z "$DUMP" || ! -f "$DUMP" ]]; then
  echo "Usage: $0 path/to/backup.dump"
  exit 1
fi

echo "==> Stopping api/worker/lint_worker (postgres stays up)"
"${COMPOSE[@]}" stop api worker lint_worker nginx frontend 2>/dev/null || true

PG_CONTAINER="$("${COMPOSE[@]}" ps -q postgres | head -n1)"
if [[ -z "$PG_CONTAINER" ]]; then
  echo "Starting postgres..."
  "${COMPOSE[@]}" up -d --wait postgres
  PG_CONTAINER="$("${COMPOSE[@]}" ps -q postgres | head -n1)"
fi

echo "==> Copy dump into postgres container"
docker cp "$DUMP" "${PG_CONTAINER}:/tmp/restore.dump"

echo "==> Restore into ${DB_NAME} (user ${DB_USER})"
docker exec -e PGPASSWORD="$DB_PASSWORD" "$PG_CONTAINER" \
  pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists --no-owner --no-privileges /tmp/restore.dump

docker exec "$PG_CONTAINER" rm -f /tmp/restore.dump

echo "==> Starting stack"
"${COMPOSE[@]}" up -d --scale worker=2

echo "Done. Check: curl -s https://${DOMAIN:-localhost}/api/health"
