#Requires -Version 5.1
# Снять дамп локальной dev-БД (Docker postgres) для переноса на сервер.
# Запуск из корня репозитория:
#   .\deploy\scripts\export-local-db.ps1
$ErrorActionPreference = "Stop"

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

$EnvFile = Join-Path $Root "backend\deploy\.env.dev"
if (-not (Test-Path $EnvFile)) {
    $EnvFile = Join-Path $Root "backend\deploy\.env.dev.example"
}

$dbName = "code_trainer"
$dbUser = "code_trainer"
$dbPassword = "change_me"
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*DB_NAME=(.+)$') { $dbName = $matches[1].Trim() }
    if ($_ -match '^\s*DB_USER=(.+)$') { $dbUser = $matches[1].Trim() }
    if ($_ -match '^\s*DB_PASSWORD=(.+)$') { $dbPassword = $matches[1].Trim() }
}

$container = docker ps --format "{{.Names}}" | Where-Object { $_ -match "dev-postgres-1$" } | Select-Object -First 1
if (-not $container) {
    Write-Error "Контейнер dev-postgres не найден. Запустите: docker compose -f backend/deploy/docker-compose.dev.yml --env-file backend/deploy/.env.dev up -d postgres"
}

$outDir = Join-Path $Root "backups\db"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$hostFile = Join-Path $outDir "code_trainer_local_$stamp.dump"

Write-Host "==> Dump from container: $container"
docker exec -e "PGPASSWORD=$dbPassword" $container pg_dump -U $dbUser -Fc -f /tmp/ct_export.dump $dbName
docker cp "${container}:/tmp/ct_export.dump" $hostFile
docker exec $container rm -f /tmp/ct_export.dump

$size = (Get-Item $hostFile).Length
Write-Host "OK: $hostFile ($size bytes)"
Write-Host ""
Write-Host "На сервер:"
Write-Host "  scp `"$hostFile`" root@92.63.102.50:/opt/code_trainer/backups/db/"
Write-Host "  ssh root@92.63.102.50"
Write-Host "  cd /opt/code_trainer && ./deploy/scripts/restore-db-on-server.sh backups/db/$(Split-Path $hostFile -Leaf)"
