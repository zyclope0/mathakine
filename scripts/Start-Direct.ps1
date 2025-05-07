<#
.SYNOPSIS
    Script de démarrage direct du serveur Mathakine en PowerShell
.DESCRIPTION
    Ce script définit directement les variables d'environnement nécessaires 
    pour le serveur et lance enhanced_server.py sans passer par le mécanisme 
    complexe de chargement d'environnement
#>

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Mathakine - Démarrage direct du serveur" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

Write-Host "Démarrage du serveur amélioré sur le port 8081..." -ForegroundColor Yellow
Write-Host

# Définir les variables d'environnement directement
$env:MATH_TRAINER_DEBUG = "true"
$env:MATH_TRAINER_PORT = "8081"
$env:MATH_TRAINER_LOG_LEVEL = "DEBUG" 
$env:MATH_TRAINER_TEST_MODE = "true"
$env:MATH_TRAINER_PROFILE = "dev"

# Afficher la configuration
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Profil : $env:MATH_TRAINER_PROFILE"
Write-Host "  Port   : $env:MATH_TRAINER_PORT"
Write-Host "  Debug  : $env:MATH_TRAINER_DEBUG"
Write-Host "  Log    : $env:MATH_TRAINER_LOG_LEVEL"
Write-Host

# Lancer le serveur amélioré
try {
    python enhanced_server.py
}
catch {
    Write-Host "Erreur lors du démarrage du serveur:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host 
    Write-Host "Vérifiez que Python est installé et que le module 'requests' est disponible." -ForegroundColor Yellow
    Write-Host "Vous pouvez installer les dépendances avec: 'pip install requests'" -ForegroundColor Yellow
}

Write-Host
Write-Host "Appuyez sur une touche pour quitter..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 