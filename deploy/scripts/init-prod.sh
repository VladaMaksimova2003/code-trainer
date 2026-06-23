#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-backend/deploy/.env.prod}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy backend/deploy/.env.prod.example and edit secrets."
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "==> Generating nginx config (HTTP)..."
chmod +x deploy/nginx/generate-config.sh
SSL=0 DOMAIN="$DOMAIN" deploy/nginx/generate-config.sh

echo "==> Building application images..."
"${COMPOSE[@]}" build api worker frontend

echo "==> Building language runner images..."
if ! "${COMPOSE[@]}" --profile runners build; then
  echo ""
  echo "WARNING: runner image build failed (often Docker Hub DNS/network on the server)."
  echo "  The site/API can still start. Code execution will work only after runners are built:"
  echo "  ${COMPOSE[*]} --profile runners build"
  echo "  Quick check: docker pull python:3.12-slim"
  echo ""
fi

echo "==> Starting database & cache (wait until healthy)..."
"${COMPOSE[@]}" up -d --wait postgres redis

echo "==> Bootstrapping database schema (ORM + alembic stamp)..."
"${COMPOSE[@]}" run --rm --no-deps api python scripts/bootstrap_db.py

if [[ "${SEED_ADMIN:-0}" == "1" ]]; then
  echo "==> Seeding admin user..."
  "${COMPOSE[@]}" --profile init run --rm seed
fi

WORKER_SCALE="${WORKER_SCALE:-2}"
echo "==> Starting application stack (worker x${WORKER_SCALE})..."
"${COMPOSE[@]}" up -d --scale "worker=${WORKER_SCALE}"

echo "==> Reloading nginx (pick up recreated api/frontend IPs)..."
"${COMPOSE[@]}" exec -T nginx nginx -s reload 2>/dev/null || "${COMPOSE[@]}" restart nginx

echo "==> Waiting for API health..."
for _ in $(seq 1 30); do
  if "${COMPOSE[@]}" exec -T api curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if [[ "${ENABLE_SSL:-1}" == "1" ]]; then
  echo "==> Requesting Let's Encrypt certificate for ${DOMAIN}..."
  if "${COMPOSE[@]}" --profile init run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    --email "${ACME_EMAIL}" \
    -d "${DOMAIN}" \
    --agree-tos --no-eff-email --non-interactive; then
    echo "==> Enabling HTTPS in nginx..."
    SSL=1 DOMAIN="$DOMAIN" deploy/nginx/generate-config.sh
    "${COMPOSE[@]}" exec -T nginx nginx -s reload || "${COMPOSE[@]}" up -d nginx
  else
    echo "WARNING: certbot failed — site stays on HTTP only. Check DNS and port 80."
  fi
else
  echo "==> ENABLE_SSL=0 — skipping certbot (HTTP only)."
fi

echo ""
echo "Done. Check:"
echo "  https://${DOMAIN}/  (or http:// if SSL failed/disabled)"
echo "  https://${DOMAIN}/api/health"
echo "  ./deploy/scripts/smoke-prod.sh"
echo ""
echo "DB backups: automatic (db_backup service, once per day) -> backups/db/"
echo "  Retention: BACKUP_RETENTION_DAYS / BACKUP_RETENTION_MAX_COUNT in $ENV_FILE"
echo ""
echo "Logs: docker compose --env-file $ENV_FILE -f docker-compose.prod.yml logs -f nginx api worker lint_worker db_backup"
