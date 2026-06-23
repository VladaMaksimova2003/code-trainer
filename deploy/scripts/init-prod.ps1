#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

$EnvFile = if ($env:ENV_FILE) { $env:ENV_FILE } else { "backend/deploy/.env.prod" }
if (-not (Test-Path $EnvFile)) {
    Write-Error "Missing $EnvFile"
}

Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
    }
}

$Compose = @("compose", "--env-file", $EnvFile, "-f", "docker-compose.prod.yml")

Write-Host "==> Generating nginx config (HTTP)..."
$env:SSL = "0"
bash deploy/nginx/generate-config.sh

Write-Host "==> Building images..."
docker @Compose build api worker frontend
docker @Compose --profile runners build

Write-Host "==> Starting postgres & redis..."
docker @Compose up -d --wait postgres redis

Write-Host "==> Migrations..."
docker @Compose --profile init run --rm migrate

if ($env:SEED_ADMIN -eq "1") {
    docker @Compose --profile init run --rm seed
}

$WorkerScale = if ($env:WORKER_SCALE) { $env:WORKER_SCALE } else { "2" }
docker @Compose up -d --scale "worker=$WorkerScale"

if (($env:ENABLE_SSL -ne "0")) {
    Write-Host "==> Certbot..."
    docker @Compose --profile init run --rm certbot certonly `
        --webroot -w /var/www/certbot `
        --email $env:ACME_EMAIL `
        -d $env:DOMAIN `
        --agree-tos --no-eff-email --non-interactive
    $env:SSL = "1"
    bash deploy/nginx/generate-config.sh
    docker @Compose exec -T nginx nginx -s reload
}

Write-Host "Done."
Write-Host ""
Write-Host "DB backups: automatic (service db_backup, once per day)."
Write-Host "  Folder: $Root\backups\db\"
Write-Host "  Old dumps are removed by age and count (see BACKUP_* in $EnvFile)."
