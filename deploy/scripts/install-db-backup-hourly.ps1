#Requires -Version 5.1
<#
.SYNOPSIS
  DEPRECATED — use install-db-backup-daily.ps1 (once per day).
#>
param(
    [string]$TaskName = "",
    [string]$EnvFile = ""
)

Write-Warning "Hourly backups are deprecated. Installing daily backup instead."
$daily = Join-Path $PSScriptRoot "install-db-backup-daily.ps1"
$params = @{}
if ($TaskName) { $params["TaskName"] = $TaskName }
if ($EnvFile) { $params["EnvFile"] = $EnvFile }
& $daily @params
