# Script de vérification du setup frontend

Write-Host "Vérification du setup frontend..." -ForegroundColor Cyan

# Vérifier les fichiers essentiels
$files = @(
    "frontend/lib/utils.ts",
    "frontend/components/ui/button.tsx",
    "frontend/components/ui/card.tsx",
    "frontend/components/accessibility/AccessibilityToolbar.tsx",
    "frontend/components/theme/ThemeSelector.tsx",
    "frontend/components/providers/Providers.tsx"
)

Write-Host "`nVérification des fichiers..." -ForegroundColor Yellow
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MANQUANT" -ForegroundColor Red
    }
}

# Vérifier les dépendances
Write-Host "`nVérification des dépendances..." -ForegroundColor Yellow
if (Test-Path "frontend/node_modules") {
    Write-Host "  ✓ node_modules présent" -ForegroundColor Green
} else {
    Write-Host "  ✗ node_modules manquant - Exécutez: cd frontend && npm install" -ForegroundColor Red
}

# Vérifier package.json
if (Test-Path "frontend/package.json") {
    Write-Host "  ✓ package.json présent" -ForegroundColor Green
} else {
    Write-Host "  ✗ package.json manquant" -ForegroundColor Red
}

Write-Host "`nPour démarrer le serveur:" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White

