#!/usr/bin/env bash
# Первичная установка Code Trainer на чистый Ubuntu VDS.
# Запуск на сервере под root (после: ssh root@ВАШ_IP):
#   curl -fsSL https://raw.githubusercontent.com/VladaMaksimova2003/code-trainer/main/deploy/scripts/bootstrap-vds.sh | bash
# или после git clone:
#   chmod +x deploy/scripts/bootstrap-vds.sh && ./deploy/scripts/bootstrap-vds.sh
set -euo pipefail

DOMAIN="${DOMAIN:-92.63.102.50}"
REPO="${REPO:-https://github.com/VladaMaksimova2003/code-trainer.git}"
APP_DIR="${APP_DIR:-/opt/code_trainer}"
ENABLE_SSL="${ENABLE_SSL:-0}"
SEED_ADMIN="${SEED_ADMIN:-1}"
WORKER_SCALE="${WORKER_SCALE:-1}"

echo "==> Обновление системы и установка Docker..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl git openssl

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "==> Клонирование репозитория в ${APP_DIR}..."
if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO" "$APP_DIR"
fi
cd "$APP_DIR"

ENV_FILE="backend/deploy/.env.prod"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> Создание ${ENV_FILE}..."
  DB_PASS="$(openssl rand -hex 16)"
  AUTH_KEY="$(openssl rand -hex 32)"
  ADMIN_PASS="$(openssl rand -base64 18 | tr -d '/+=' | head -c 16)"

  if [[ "$ENABLE_SSL" == "1" ]]; then
    CORS_ORIGIN="https://${DOMAIN}"
  else
    CORS_ORIGIN="http://${DOMAIN}"
  fi

  cat > "$ENV_FILE" <<EOF
DOMAIN=${DOMAIN}
ACME_EMAIL=admin@localhost
ENABLE_SSL=${ENABLE_SSL}

VITE_API_BASE_URL=/api
CORS_ORIGINS=${CORS_ORIGIN}

DB_NAME=code_trainer
DB_USER=code_trainer
DB_PASSWORD=${DB_PASS}

AUTH__SECRET_KEY=${AUTH_KEY}

SMTP__HOST=localhost
SMTP__PORT=1025
SMTP__USER=
SMTP__PASSWORD=
SMTP__USE_TLS=false
SMTP__FROM_EMAIL=noreply@localhost

EXECUTION_GLOBAL_MAX_QUEUE=100
EXECUTION_USER_MAX_PER_MINUTE=20
EXECUTION_USER_MAX_CONCURRENT=2
WORKER_SCALE=${WORKER_SCALE}

SEED_ADMIN_EMAIL=admin@code-trainer.local
SEED_ADMIN_PASSWORD=${ADMIN_PASS}
SEED_ADMIN_NAME=Admin

ENABLE_OPENAPI_DOCS=false
BACKUP_INTERVAL_SECONDS=86400
BACKUP_RETENTION_DAYS=14
BACKUP_RETENTION_MAX_COUNT=14
EOF

  chmod 600 "$ENV_FILE"
  echo ""
  echo "Сохраните данные администратора (файл ${ENV_FILE}):"
  echo "  Email:    admin@code-trainer.local"
  echo "  Пароль:   ${ADMIN_PASS}"
  echo ""
fi

echo "==> Запуск production-установки (сборка может занять 20–40 мин на 2 CPU)..."
export SEED_ADMIN="$SEED_ADMIN"
export ENABLE_SSL="$ENABLE_SSL"
export WORKER_SCALE="$WORKER_SCALE"
chmod +x deploy/scripts/init-prod.sh deploy/scripts/smoke-prod.sh deploy/nginx/generate-config.sh
./deploy/scripts/init-prod.sh

echo ""
echo "Готово."
if [[ "$ENABLE_SSL" == "1" ]]; then
  echo "  Сайт:  https://${DOMAIN}/"
else
  echo "  Сайт:  http://${DOMAIN}/"
fi
echo "  API:   /api/health"
echo ""
echo "Проверка: docker compose --env-file ${ENV_FILE} -f docker-compose.prod.yml ps"
