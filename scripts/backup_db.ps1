# Script de backup BDD Mathakine (PowerShell)
# Usage: .\scripts\backup_db.ps1
# Ou avec DATABASE_URL: $env:DATABASE_URL="postgresql://..."; .\scripts\backup_db.ps1

$ErrorActionPreference = "Stop"

$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

$url = $env:DATABASE_URL
if (-not $url) {
    Write-Host "ERREUR: DATABASE_URL non definie. Ex: `$env:DATABASE_URL='postgresql://user:pass@host/db'" -ForegroundColor Red
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$dumpFile = "$backupDir/mathakine_backup_$timestamp.dump"

Write-Host "Backup vers $dumpFile ..." -ForegroundColor Cyan
try {
    pg_dump $url -F c -f $dumpFile
    Write-Host "Backup termine: $dumpFile" -ForegroundColor Green
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
    exit 1
}
