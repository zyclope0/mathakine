# Script PowerShell de vérification TypeScript avant déploiement
# Usage: .\scripts\check_types_before_deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔍 Vérification TypeScript complète avant déploiement..." -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
npm install --silent

Write-Host ""
Write-Host "🔨 Build TypeScript..." -ForegroundColor Yellow

try {
    npm run build
    Write-Host ""
    Write-Host "✅ Build réussi ! Aucune erreur TypeScript détectée." -ForegroundColor Green
    Set-Location ..
    exit 0
} catch {
    Write-Host ""
    Write-Host "❌ Build échoué ! Des erreurs TypeScript ont été détectées." -ForegroundColor Red
    Write-Host "Corrigez les erreurs avant de déployer." -ForegroundColor Red
    Set-Location ..
    exit 1
}

