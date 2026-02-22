# Script de backup BDD Mathakine (PowerShell)
# Usage: .\scripts\backup_db.ps1
# Charge .env pour DATABASE_URL. Si BDD via Docker (pg-test), utilise docker exec.

$ErrorActionPreference = "Stop"

$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# Charger URL depuis .env (DATABASE_URL ou TEST_DATABASE_URL pour local)
$url = $env:DATABASE_URL
$testUrl = $env:TEST_DATABASE_URL
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^DATABASE_URL=(.+)$" -and $_ -notmatch "^\s*#") {
            $url = ($_ -split "=", 2)[1].Trim().Trim('"').Trim("'")
        }
        if ($_ -match "^TEST_DATABASE_URL=(.+)$" -and $_ -notmatch "^\s*#") {
            $testUrl = ($_ -split "=", 2)[1].Trim().Trim('"').Trim("'")
        }
    }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$dumpFile = "$backupDir\mathakine_backup_$timestamp.dump"

# BDD locale via Docker : pg-test avec test_mathakine
$dockerContainer = "pg-test"
$dockerDb = "test_mathakine"

# Prefer TEST_DATABASE_URL si localhost (base de dev locale)
$urlToUse = if ($testUrl -and ($testUrl -match "localhost|127\.0\.0\.1")) { $testUrl } else { $url }
# Détecter si URL pointe vers localhost (Docker local)
$useDocker = $urlToUse -and ($urlToUse -match "localhost|127\.0\.0\.1")

if ($useDocker) {
    Write-Host "Backup BDD locale (Docker $dockerContainer / $dockerDb) vers $dumpFile ..." -ForegroundColor Cyan
    try {
        cmd /c "docker exec $dockerContainer pg_dump -U postgres -d $dockerDb -F c > $dumpFile"
        if (Test-Path $dumpFile) {
            $size = (Get-Item $dumpFile).Length
            Write-Host "Backup termine: $dumpFile ($size octets)" -ForegroundColor Green
        } else {
            Write-Host "Erreur: fichier non cree" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
        exit 1
    }
} elseif ($url) {
    Write-Host "Backup vers $dumpFile ..." -ForegroundColor Cyan
    try {
        pg_dump $url -F c -f $dumpFile
        Write-Host "Backup termine: $dumpFile" -ForegroundColor Green
    } catch {
        Write-Host "Erreur: $_" -ForegroundColor Red
        Write-Host "Si BDD locale Docker: l'URL localhost declenche le mode docker exec automatiquement." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "ERREUR: DATABASE_URL non definie. Definir la var ou ajouter DATABASE_URL dans .env" -ForegroundColor Red
    exit 1
}
