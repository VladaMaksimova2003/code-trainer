#!/usr/bin/env bash
# Switch production to DOMAIN + HTTPS (Let's Encrypt) without full rebuild.
#
# Prerequisites:
#   - DNS A record for $DOMAIN → this server's public IP
#   - Ports 80 and 443 open
#   - backend/deploy/.env.prod updated (DOMAIN, ENABLE_SSL=1, OAuth/CORS https URLs)
#
# Usage (on the server, from repo root):
#   chmod +x deploy/scripts/enable-domain-ssl.sh
#   ./deploy/scripts/enable-domain-ssl.sh
#
# Optional:
#   EXPECT_IP=92.63.102.50   — fail if DNS does not resolve to this IP
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

DOMAIN="${DOMAIN:?DOMAIN is required in $ENV_FILE}"
ENABLE_SSL="${ENABLE_SSL:-1}"
ACME_EMAIL="${ACME_EMAIL:?ACME_EMAIL is required for Let's Encrypt}"

if [[ "$ENABLE_SSL" != "1" ]]; then
  echo "ENABLE_SSL must be 1 in $ENV_FILE"
  exit 1
fi

if [[ -n "${EXPECT_IP:-}" ]]; then
  RESOLVED="$(getent ahosts "$DOMAIN" 2>/dev/null | awk '/STREAM/ {print $1; exit}')"
  if [[ -z "$RESOLVED" ]]; then
    RESOLVED="$(dig +short "$DOMAIN" A 2>/dev/null | head -n1 || true)"
  fi
  if [[ "$RESOLVED" != "$EXPECT_IP" ]]; then
    echo "DNS check failed: $DOMAIN → ${RESOLVED:-<none>} (expected $EXPECT_IP)"
    echo "Configure A record at your registrar, wait for propagation, then retry."
    exit 1
  fi
  echo "DNS OK: $DOMAIN → $RESOLVED"
fi

chmod +x deploy/nginx/generate-config.sh

echo "==> Nginx config (HTTP + ACME challenge)..."
SSL=0 DOMAIN="$DOMAIN" deploy/nginx/generate-config.sh
"${COMPOSE[@]}" up -d nginx

echo "==> Requesting Let's Encrypt certificate for ${DOMAIN}..."
if ! "${COMPOSE[@]}" --profile init run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "${ACME_EMAIL}" \
  -d "${DOMAIN}" \
  --agree-tos --no-eff-email --non-interactive; then
  echo ""
  echo "certbot failed. Common causes:"
  echo "  - DNS A record not pointing to this server yet"
  echo "  - port 80 blocked by firewall"
  echo "  - wrong DOMAIN in $ENV_FILE"
  exit 1
fi

echo "==> Enabling HTTPS in nginx..."
SSL=1 DOMAIN="$DOMAIN" deploy/nginx/generate-config.sh
"${COMPOSE[@]}" exec -T nginx nginx -s reload 2>/dev/null || "${COMPOSE[@]}" restart nginx

echo "==> Applying OAuth/CORS env (restart API)..."
"${COMPOSE[@]}" up -d api

echo ""
echo "Done."
echo "  Site:  https://${DOMAIN}/"
echo "  API:   https://${DOMAIN}/api/health"
echo "  OAuth: https://${DOMAIN}/api/auth/oauth/yandex/callback"
echo ""
echo "Update Yandex OAuth redirect URI to the URL above, then run:"
echo "  BASE_URL=https://${DOMAIN} ./deploy/scripts/smoke-prod.sh"
