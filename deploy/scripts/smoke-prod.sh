#!/usr/bin/env bash
# Post-deploy smoke checks for production (run on the server from repo root).
#
# Usage:
#   chmod +x deploy/scripts/smoke-prod.sh
#   ./deploy/scripts/smoke-prod.sh
#
# Optional env:
#   BASE_URL=http://127.0.0.1          — nginx entrypoint (default)
#   BASE_URL=https://your.domain       — external HTTPS check
#   ENV_FILE=backend/deploy/.env.prod
#   SKIP_COMPOSE=1                     — only HTTP checks (no docker compose ps)
#   SKIP_RUNNERS=1                     — skip runner image inspect
#   CURL_EXTRA_ARGS="-k"               — e.g. self-signed TLS
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-backend/deploy/.env.prod}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)
BASE_URL="${BASE_URL:-http://127.0.0.1}"
BASE_URL="${BASE_URL%/}"
CURL_EXTRA_ARGS="${CURL_EXTRA_ARGS:-}"

FAILED=0

pass() {
  echo "  OK   $*"
}

fail() {
  echo "  FAIL $*"
  FAILED=$((FAILED + 1))
}

curl_http_code() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local tmp
  tmp="$(mktemp)"
  local code
  if [[ "$method" == "GET" ]]; then
    # shellcheck disable=SC2086
    code="$(curl -sS $CURL_EXTRA_ARGS -o "$tmp" -w "%{http_code}" "$url")"
  else
    # shellcheck disable=SC2086
    code="$(curl -sS $CURL_EXTRA_ARGS -o "$tmp" -w "%{http_code}" -X "$method" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$url")"
  fi
  # Body and status code must be on separate lines (JSON often has no trailing newline).
  printf '%s\n%s' "$(cat "$tmp")" "$code"
  rm -f "$tmp"
}

expect_http() {
  local name="$1"
  local method="$2"
  local url="$3"
  local expected_re="$4"
  local data="${5:-}"
  local body code

  if [[ "$method" == "GET" ]]; then
    body="$(curl_http_code GET "$url")"
  else
    body="$(curl_http_code "$method" "$url" "$data")"
  fi
  code="$(echo "$body" | tail -n1)"
  body="$(echo "$body" | sed '$d')"

  if [[ ! "$code" =~ ^($expected_re)$ ]]; then
    fail "$name — HTTP $code (expected $expected_re)"
    if [[ -n "$body" ]]; then
      echo "       $(echo "$body" | tr '\n' ' ' | head -c 240)"
    fi
    return 1
  fi
  pass "$name — HTTP $code"
  REPLY="$body"
  return 0
}

json_assert() {
  local name="$1"
  local body="$2"
  local py="$3"
  if ! echo "$body" | python3 -c "$py" >/dev/null 2>&1; then
    fail "$name — unexpected response body"
    echo "       $(echo "$body" | tr '\n' ' ' | head -c 240)"
    return 1
  fi
  pass "$name — response shape"
  return 0
}

echo "==> Code Trainer production smoke"
echo "    BASE_URL=$BASE_URL"
echo ""

if [[ "${SKIP_COMPOSE:-0}" != "1" ]]; then
  echo "==> Docker Compose services"
  if [[ ! -f "$ENV_FILE" ]]; then
    fail "missing env file: $ENV_FILE"
  else
    for svc in nginx api frontend worker lint_worker postgres redis; do
      state="$("${COMPOSE[@]}" ps "$svc" --format '{{.State}}' 2>/dev/null | head -n1 || true)"
      if [[ -z "$state" || "$state" == "exited" || "$state" == "dead" ]]; then
        fail "service $svc — state: ${state:-not found}"
      else
        pass "service $svc — $state"
      fi
    done

    api_health="$("${COMPOSE[@]}" ps api --format '{{.Health}}' 2>/dev/null | head -n1 || true)"
    if [[ "$api_health" == "healthy" ]]; then
      pass "api container healthcheck"
    else
      fail "api container healthcheck — ${api_health:-unknown}"
    fi
  fi
  echo ""
fi

echo "==> HTTP via nginx ($BASE_URL)"

if expect_http "GET /api/health" GET "$BASE_URL/api/health" "200"; then
  json_assert "GET /api/health" "$REPLY" \
    'import json,sys; d=json.load(sys.stdin); assert d.get("status")=="ok"'
fi

if expect_http "GET /api/languages/" GET "$BASE_URL/api/languages/" "200"; then
  json_assert "GET /api/languages/" "$REPLY" \
    'import json,sys; d=json.load(sys.stdin); assert isinstance(d,list) and len(d)>=1'
fi

tasks_body=""
tasks_ok=0
overview_result="$(curl_http_code GET "$BASE_URL/api/tasks/overview")"
overview_code="$(echo "$overview_result" | tail -n1)"
overview_body="$(echo "$overview_result" | sed '$d')"
if [[ "$overview_code" == "200" ]]; then
  pass "GET /api/tasks/overview — HTTP 200"
  tasks_body="$overview_body"
  tasks_ok=1
elif [[ "$overview_code" =~ ^(404|422)$ ]]; then
  echo "  WARN GET /api/tasks/overview — HTTP $overview_code (trying /api/tasks/?light=true)"
  if expect_http "GET /api/tasks/?light=true (fallback)" GET "$BASE_URL/api/tasks/?light=true" "200"; then
    tasks_body="$REPLY"
    tasks_ok=1
  fi
else
  fail "GET /api/tasks/overview — HTTP $overview_code"
  if expect_http "GET /api/tasks/?light=true (fallback)" GET "$BASE_URL/api/tasks/?light=true" "200"; then
    tasks_body="$REPLY"
    tasks_ok=1
  fi
fi
if [[ "$tasks_ok" == "1" ]]; then
  json_assert "task overview payload" "$tasks_body" \
    'import json,sys; d=json.load(sys.stdin); assert "tasks" in d and isinstance(d["tasks"], list)'
else
  fail "task overview — no working endpoint"
fi

# Route must exist: unauthenticated POST → 401/403/422, not 404/405/502.
submission_payload='{"task_id":1,"language":"python","source_code":"print(1)"}'
for path in "/api/submissions/" "/api/submissions"; do
  expect_http "POST $path" POST "$BASE_URL$path" "307|401|403|422" "$submission_payload" || true
done

if expect_http "GET / (frontend)" GET "$BASE_URL/" "200"; then
  if ! echo "$REPLY" | grep -qi '<html'; then
    fail "GET / — response does not look like HTML"
  else
    pass "GET / — HTML shell"
  fi
fi

echo ""

if [[ "${SKIP_RUNNERS:-0}" != "1" ]]; then
  echo "==> Language runner images (worker docker run)"
  for image in python_runner cpp_runner java_runner csharp_runner pascal_runner; do
    if docker image inspect "$image" >/dev/null 2>&1; then
      pass "image $image"
    else
      fail "image $image — not found (run: docker compose --profile runners build)"
    fi
  done
  echo ""
fi

if [[ "$FAILED" -eq 0 ]]; then
  echo "All smoke checks passed."
  exit 0
fi

echo "$FAILED check(s) failed."
exit 1
