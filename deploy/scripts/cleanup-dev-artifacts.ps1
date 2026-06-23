#Requires -Version 5.1
<#
.SYNOPSIS
  Removes local dev debug dumps under backend/_* (not production DB backups).

.EXAMPLE
  .\deploy\scripts\cleanup-dev-artifacts.ps1
  .\deploy\scripts\cleanup-dev-artifacts.ps1 -WhatIf
#>
param(
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$backend = Join-Path $Root "backend"

$patterns = @("_*.txt", "_*.json", "_diag*", "_dump*")
$removed = 0

foreach ($pattern in $patterns) {
    Get-ChildItem -Path $backend -Filter $pattern -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            if ($WhatIf) {
                Write-Host "Would remove: $($_.FullName)"
            } else {
                Remove-Item -Force $_.FullName
                Write-Host "Removed: $($_.Name)"
            }
            $removed++
        }
}

if ($removed -eq 0) {
    Write-Host "Nothing to clean in backend/"
} elseif ($WhatIf) {
    Write-Host "$removed file(s) would be removed."
} else {
    Write-Host "Done. Removed $removed file(s)."
}
