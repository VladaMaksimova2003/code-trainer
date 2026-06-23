#!/usr/bin/env bash
# Generate nginx conf from templates. Usage:
#   DOMAIN=trainer.example.com SSL=0 ./deploy/nginx/generate-config.sh
#   DOMAIN=trainer.example.com SSL=1 ./deploy/nginx/generate-config.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/deploy/nginx/generated"
TEMPLATE="$ROOT/deploy/nginx/templates/app.conf.template"
SSL_TEMPLATE="$ROOT/deploy/nginx/templates/ssl-server.conf.template"

DOMAIN="${DOMAIN:?DOMAIN is required}"
SSL="${SSL:-0}"
export DOMAIN

mkdir -p "$OUT_DIR"

if [[ "$SSL" == "1" ]]; then
  export SSL_SERVER_BLOCK
  SSL_SERVER_BLOCK="$(envsubst '$DOMAIN' < "$SSL_TEMPLATE")"
  export SSL_SERVER_BLOCK
else
  export SSL_SERVER_BLOCK=""
fi

envsubst '$DOMAIN $SSL_SERVER_BLOCK' < "$TEMPLATE" > "$OUT_DIR/app.conf"
echo "Wrote $OUT_DIR/app.conf (SSL=$SSL)"
