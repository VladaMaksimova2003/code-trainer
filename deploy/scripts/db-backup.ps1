#Requires -Version 5.1

<#

.SYNOPSIS

  PostgreSQL dump for Code Trainer (daily via Task Scheduler or manual run).



.EXAMPLE

  .\deploy\scripts\db-backup.ps1

  $env:ENV_FILE = "backend/deploy/.env.prod"; .\deploy\scripts\db-backup.ps1

#>

param(

    [string]$EnvFile = "",

    [int]$RetentionDays = 0,

    [int]$RetentionMaxCount = 0

)



$ErrorActionPreference = "Stop"



$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

Set-Location $Root



if (-not $EnvFile) {

    $EnvFile = if ($env:ENV_FILE) { $env:ENV_FILE } else { "backend/deploy/.env.dev" }

}

if (-not (Test-Path $EnvFile)) {

    Write-Error "Env file not found: $EnvFile"

}



$vars = @{}

Get-Content $EnvFile | ForEach-Object {

    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {

        $vars[$matches[1].Trim()] = $matches[2].Trim()

    }

}



$dbName = if ($vars["DB_NAME"]) { $vars["DB_NAME"] } else { "code_trainer" }

$dbUser = if ($vars["DB_USER"]) { $vars["DB_USER"] } else { "code_trainer" }

$dbPassword = $vars["DB_PASSWORD"]

$postgresPort = if ($vars["POSTGRES_PORT"]) { $vars["POSTGRES_PORT"] } else { "5433" }



if ($RetentionDays -le 0) {

    $RetentionDays = if ($vars["BACKUP_RETENTION_DAYS"]) { [int]$vars["BACKUP_RETENTION_DAYS"] } else { 21 }

}

if ($RetentionMaxCount -le 0) {

    $RetentionMaxCount = if ($vars["BACKUP_RETENTION_MAX_COUNT"]) { [int]$vars["BACKUP_RETENTION_MAX_COUNT"] } else { 30 }

}



if (-not $dbPassword) {

    Write-Error "DB_PASSWORD is missing in $EnvFile"

}



$backupDir = Join-Path $Root "backups\db"

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null



$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$outFile = Join-Path $backupDir "${dbName}_${timestamp}.dump"



function Invoke-DockerBackup {

    param([string]$ComposeFile)



    $composeArgs = @("compose", "--env-file", $EnvFile, "-f", $ComposeFile, "exec", "-T", "postgres")

    $dumpArgs = @("pg_dump", "-U", $dbUser, "-Fc", $dbName)



    $proc = Start-Process -FilePath "docker" `

        -ArgumentList ($composeArgs + $dumpArgs) `

        -RedirectStandardOutput $outFile `

        -NoNewWindow -Wait -PassThru



    if ($proc.ExitCode -ne 0) {

        Remove-Item -Force -ErrorAction SilentlyContinue $outFile

        throw "docker compose pg_dump failed (exit $($proc.ExitCode))"

    }

}



function Invoke-LocalBackup {

    $pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue

    if (-not $pgDump) {

        throw "pg_dump not found in PATH and postgres container is not running"

    }



    $env:PGPASSWORD = $dbPassword

    try {

        & $pgDump.Source -h 127.0.0.1 -p $postgresPort -U $dbUser -Fc -f $outFile $dbName

        if ($LASTEXITCODE -ne 0) {

            Remove-Item -Force -ErrorAction SilentlyContinue $outFile

            throw "pg_dump failed (exit $LASTEXITCODE)"

        }

    } finally {

        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue

    }

}



function Remove-OldBackups {

    param([string]$Dir)



    if ($RetentionDays -gt 0) {

        $cutoff = (Get-Date).AddDays(-$RetentionDays)

        Get-ChildItem $Dir -Filter "*.dump" -File |

            Where-Object { $_.LastWriteTime -lt $cutoff } |

            ForEach-Object {

                Write-Host "Removing old backup (age): $($_.Name)"

                Remove-Item -Force $_.FullName

            }

    }



    if ($RetentionMaxCount -gt 0) {

        $files = @(Get-ChildItem $Dir -Filter "*.dump" -File | Sort-Object LastWriteTime -Descending)

        if ($files.Count -gt $RetentionMaxCount) {

            $files | Select-Object -Skip $RetentionMaxCount | ForEach-Object {

                Write-Host "Removing old backup (cap): $($_.Name)"

                Remove-Item -Force $_.FullName

            }

        }

    }



    $remaining = @(Get-ChildItem $Dir -Filter "*.dump" -File)

    $totalMb = [math]::Round(($remaining | Measure-Object -Property Length -Sum).Sum / 1MB, 2)

    Write-Host "Archive: $($remaining.Count) file(s), total ~$totalMb MB"

}



$usedDocker = $false

foreach ($composeFile in @("docker-compose.prod.yml", "docker-compose.yml", "backend/deploy/docker-compose.dev.yml")) {

    if (-not (Test-Path $composeFile)) { continue }

    try {

        $ps = docker compose --env-file $EnvFile -f $composeFile ps postgres --status running -q 2>$null

        if ($ps) {

            Invoke-DockerBackup -ComposeFile $composeFile

            $usedDocker = $true

            break

        }

    } catch {

        # try next compose file

    }

}



if (-not $usedDocker) {

    Invoke-LocalBackup

}



$sizeMb = [math]::Round((Get-Item $outFile).Length / 1MB, 2)

Write-Host "Backup saved: $outFile ($sizeMb MB)"



Remove-OldBackups -Dir $backupDir

