#Requires -Version 5.1
<#
.SYNOPSIS
  Registers Windows Scheduled Task: PostgreSQL dump once per day (03:00).

  Use when Postgres runs outside Docker or as a host-side copy in addition to
  the db_backup container (see docker-compose *.yml).

.EXAMPLE
  .\deploy\scripts\install-db-backup-daily.ps1
  (Run PowerShell as Administrator if registration fails.)
#>
param(
    [string]$TaskName = "CodeTrainerDbBackupDaily",
    [string]$EnvFile = "",
    [string]$At = "03:00"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$backupScript = Join-Path $Root "deploy\scripts\db-backup.ps1"

if (-not (Test-Path $backupScript)) {
    Write-Error "Missing $backupScript"
}

if ($EnvFile) {
    $arguments = "-NoProfile -ExecutionPolicy Bypass -Command `"`$env:ENV_FILE='$EnvFile'; & '$backupScript'`""
} else {
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$backupScript`""
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Daily -At $At

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "Scheduled task registered: $TaskName (daily at $At)"
    Write-Host "Backups -> $Root\backups\db\"
    Write-Host "Retention: BACKUP_RETENTION_DAYS / BACKUP_RETENTION_MAX_COUNT in your .env"
    Write-Host "Test now: powershell -File $backupScript"
} catch {
    Write-Warning "Could not register task (Administrator required?): $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Run PowerShell as Administrator, then:"
    Write-Host "  cd $Root"
    Write-Host "  .\deploy\scripts\install-db-backup-daily.ps1"
    exit 1
}
