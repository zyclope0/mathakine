# Script PowerShell pour exécuter les tests de charge k6
# Usage: .\scripts\load\run_load_tests.ps1 [--level quick|standard|full]

param(
    [string]$BackendUrl = $env:BACKEND_URL,
    [ValidateSet("quick", "standard", "full")]
    [string]$Level = "standard",
    [string]$Username = $env:TEST_USERNAME,
    [string]$Password = $env:TEST_PASSWORD
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📈 TESTS DE CHARGE MATHAKINE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier k6
Write-Host "🔍 Vérification de k6..." -ForegroundColor Yellow
try {
    $k6Version = k6 version 2>&1
    Write-Host "  ✅ k6 installé: $($k6Version -split "`n" | Select-Object -First 1)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ k6 n'est pas installé" -ForegroundColor Red
    Write-Host "     Installation: winget install k6" -ForegroundColor Yellow
    exit 1
}

# Configuration par défaut
if (-not $BackendUrl) {
    $BackendUrl = "http://localhost:10000"
}
if (-not $Username) {
    $Username = "ObiWan"
}
if (-not $Password) {
    $Password = "HelloThere123!"
}

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  Backend URL: $BackendUrl" -ForegroundColor White
Write-Host "  Niveau: $Level" -ForegroundColor White
Write-Host "  Username: $Username" -ForegroundColor White
Write-Host ""

# Vérifier que le backend est accessible
Write-Host "🔍 Vérification du backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✅ Backend accessible" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Backend non accessible à $BackendUrl" -ForegroundColor Yellow
    $continue = Read-Host "  Continuer quand même ? (o/N)"
    if ($continue -ne "o") {
        exit 1
    }
}

# Définir les variables d'environnement
$env:BACKEND_URL = $BackendUrl
$env:TEST_USERNAME = $Username
$env:TEST_PASSWORD = $Password

# Aller dans le répertoire k6
$k6Dir = Join-Path $PSScriptRoot "k6"
Set-Location $k6Dir

# Définir les scénarios selon le niveau
$scenarios = @()

if ($Level -eq "quick") {
    $scenarios = @(
        @{ Name = "Auth Burst"; File = "auth_burst.js"; VUs = 5; Duration = "30s" }
    )
} elseif ($Level -eq "standard") {
    $scenarios = @(
        @{ Name = "Auth Burst"; File = "auth_burst.js"; VUs = 5; Duration = "60s" },
        @{ Name = "Refresh Storm"; File = "refresh_storm.js"; VUs = 3; Duration = "60s" }
    )
} else {  # full
    $scenarios = @(
        @{ Name = "Auth Burst"; File = "auth_burst.js"; VUs = 5; Duration = "60s" },
        @{ Name = "Refresh Storm"; File = "refresh_storm.js"; VUs = 3; Duration = "60s" },
        @{ Name = "SSE IA Challenges"; File = "sse_ia_challenges.js"; VUs = 200; Duration = "60s" },
        @{ Name = "Mix Auth+SSE"; File = "mix_auth_sse.js"; VUs = 100; Duration = "120s" }
    )
}

Write-Host "📊 Exécution de $($scenarios.Count) scénario(s)..." -ForegroundColor Yellow
Write-Host ""

$results = @()
$allPassed = $true

foreach ($scenario in $scenarios) {
    Write-Host "[$($scenarios.IndexOf($scenario) + 1)/$($scenarios.Count)] $($scenario.Name)" -ForegroundColor Cyan
    Write-Host "  VUs: $($scenario.VUs), Durée: $($scenario.Duration)" -ForegroundColor Gray
    
    try {
        $result = k6 run --vus $scenario.VUs --duration $scenario.Duration $scenario.File
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $($scenario.Name): Succès" -ForegroundColor Green
            $results += @{ Name = $scenario.Name; Success = $true }
        } else {
            Write-Host "  ❌ $($scenario.Name): Échec" -ForegroundColor Red
            $results += @{ Name = $scenario.Name; Success = $false }
            $allPassed = $false
        }
    } catch {
        Write-Host "  ❌ $($scenario.Name): Erreur - $_" -ForegroundColor Red
        $results += @{ Name = $scenario.Name; Success = $false }
        $allPassed = $false
    }
    
    Write-Host ""
}

# Résumé
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.Success }).Count
$failed = ($results | Where-Object { -not $_.Success }).Count

Write-Host "✅ Succès: $passed/$($results.Count)" -ForegroundColor Green
Write-Host "❌ Échecs: $failed/$($results.Count)" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($allPassed) {
    Write-Host "✅ Tous les tests de charge sont passés" -ForegroundColor Green
    Set-Location $PSScriptRoot\..
    exit 0
} else {
    Write-Host "❌ Certains tests de charge ont échoué" -ForegroundColor Red
    Set-Location $PSScriptRoot\..
    exit 1
}

