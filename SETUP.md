# Установка и запуск проекта

## Что нужно установить

| Инструмент | Ссылка | Зачем |
|---|---|---|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ | Запускает все сервисы в контейнерах |
| **Git** | https://git-scm.com/ | Скачать репозиторий |

> После установки Docker Desktop убедитесь, что он **запущен** (иконка в трее).

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <ссылка-на-репозиторий> code_trainer
cd code_trainer
```

### 2. Создать файл окружения

**Windows (PowerShell):**
```powershell
Copy-Item backend\deploy\.env.dev.example backend\deploy\.env.dev
```

**Linux / macOS:**
```bash
cp backend/deploy/.env.dev.example backend/deploy/.env.dev
```

Файл `.env.dev` содержит настройки по умолчанию — для локального запуска менять ничего не нужно.

### 3. Собрать и запустить контейнеры

```bash
docker compose --env-file backend/deploy/.env.dev up -d --build
```

Первый запуск занимает **5–15 минут** — Docker скачивает базовые образы и собирает приложение.

Проверить что всё запустилось:
```bash
docker compose --env-file backend/deploy/.env.dev ps
```

Все сервисы должны быть в статусе `running` или `healthy`.

### 4. Применить миграции базы данных

Подождите ~15 секунд после шага 3, затем:

```bash
docker exec code_trainer_dev-api-1 alembic upgrade head
```

### 5. Загрузить курс Pascal в базу данных

```bash
docker exec code_trainer_dev-api-1 python scripts/seed_pascal_course_v311.py --force-catalog-sync
```

Скрипт создаст 200 учебных задач. Если запустить повторно — ничего не сломается (идемпотентный).

> Флаг `--force-catalog-sync` нужен, потому что по умолчанию синхронизация каталога из файлов отключена.

### 6. Создать аккаунт администратора

Добавьте в `backend/deploy/.env.dev` (или скопируйте из `.env.dev.example`):

```
SEED_ADMIN_EMAIL=admin@test.com
SEED_ADMIN_PASSWORD=dev_admin_pass_12
SEED_ADMIN_NAME=Admin
```

Перезапустите API, если меняли `.env.dev`:

```bash
docker compose --env-file backend/deploy/.env.dev up -d api
```

Затем:

```bash
docker exec code_trainer_dev-api-1 python scripts/seed_admin.py
```

Логин и пароль будут выведены в консоль.

### 7. Открыть приложение

| Сервис | Адрес |
|---|---|
| **Фронтенд** | http://localhost:5173 |
| **API (документация)** | http://localhost:9000/docs |
| **Почта (Mailpit)** | http://localhost:9025 |

---

## Остановка и перезапуск

```bash
# Остановить (данные сохранятся)
docker compose --env-file backend/deploy/.env.dev down

# Запустить снова
docker compose --env-file backend/deploy/.env.dev up -d
```

---

## Сброс базы данных (если нужно начать с нуля)

```bash
# Удалить контейнеры и том с данными
docker compose --env-file backend/deploy/.env.dev down -v

# Поднять заново и повторить шаги 3–6
docker compose --env-file backend/deploy/.env.dev up -d --build
docker exec code_trainer_dev-api-1 alembic upgrade head
docker exec code_trainer_dev-api-1 python scripts/seed_pascal_course_v311.py --force-catalog-sync
docker exec code_trainer_dev-api-1 python scripts/seed_admin.py
```

---

## Часто встречающиеся проблемы

### Порт уже занят

На Windows Hyper-V блокирует диапазон портов 7961–8060. Если `API_PORT=8001` не работает — откройте `backend/deploy/.env.dev` и смените:

```
API_PORT=9000
```

### Контейнер `api` не запускается

Посмотреть логи:
```bash
docker logs code_trainer_dev-api-1
```

### Фронтенд долго загружается первый раз

Это нормально — при первом старте `npm install` скачивает зависимости внутри контейнера (~2 минуты).

### `TLS handshake timeout` / `failed to resolve source metadata` (Windows + Docker Desktop)

Docker не может скачать `python:3.12-slim` с Docker Hub. Это **сеть**, не баг проекта. Падают `api`, `worker` и runner'ы — все на базе этого образа.

**1. Перезапустите Docker Desktop** (полностью Quit → снова запустить). Ошибка `pipe/dockerDesktopLinuxEngine: file has already been closed` часто лечится так.

**2. Проверьте pull отдельно (несколько раз):**

```powershell
docker pull python:3.12-slim
```

**3. DNS в Docker Desktop:** Settings → Docker Engine → добавьте (или дополните) и Apply:

```json
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```

**4. VPN** — если Docker Hub режется провайдером, включите VPN и повторите `docker pull`.

**5. Зеркало базового образа** — если образ уже есть под другим registry, в `backend/deploy/.env.dev`:

```env
PYTHON_BASE_IMAGE=your-mirror.example.com/library/python:3.12-slim
```

**6. Локально без сборки API** (если образы уже были когда-то скачаны):

```powershell
docker images python
docker compose --env-file backend/deploy/.env.dev up -d postgres redis mailpit
cd frontend
npm install --legacy-peer-deps
npm run dev
```

API на хосте (нужны Python 3.12 + Poetry):

```powershell
cd backend
poetry install
$env:DB__HOST="127.0.0.1"; $env:DB__PORT="5433"
poetry run uvicorn main:app --reload --port 9000
```

Фронт: http://localhost:5173, API: http://127.0.0.1:9000/docs

---

### `failed to resolve source metadata` при сборке runner'ов (Linux VDS)

Docker не может скачать базовые образы (`python:3.12-slim`, `ubuntu:22.04` и т.д.) с Docker Hub — обычно DNS или сеть на сервере.

**Поднять приложение без runner'ов** (сайт и API работают, проверка кода — нет):

```bash
docker compose --env-file backend/deploy/.env.dev up -d --build api worker lint_worker frontend postgres redis mailpit
```

**Проверка сети:**

```bash
curl -I https://registry-1.docker.io/v2/
docker pull python:3.12-slim
```

**Частый фикс DNS для Docker (на VDS под root):**

```bash
mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
EOF
systemctl restart docker
docker pull python:3.12-slim
```

**Собрать runner'ы отдельно** (когда `docker pull` заработал):

```bash
docker compose --env-file backend/deploy/.env.dev --profile runners build
# опционально — «тёплые» контейнеры для ускорения:
docker compose --env-file backend/deploy/.env.dev --profile runners up -d
```

На проде то же самое:

```bash
export COMPOSE='docker compose --env-file backend/deploy/.env.prod -f docker-compose.prod.yml'
$COMPOSE build api worker frontend
$COMPOSE --profile runners build
```
