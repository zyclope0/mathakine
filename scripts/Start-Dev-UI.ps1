# =======================================================
# Script de démarrage rapide du serveur Mathakine avec UI
# Mode développement par défaut
# =======================================================

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Mathakine - Démarrage interface utilisateur" -ForegroundColor Cyan
Write-Host "   (Mode développement)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
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

# Obtenir le chemin du script et du projet
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Se placer dans le dossier racine du projet
Set-Location -Path $projectRoot
Write-Host "Répertoire de projet: $projectRoot"
Write-Host

# Lancer le serveur amélioré
try {
    Write-Host "Démarrage du serveur avec interface utilisateur..." -ForegroundColor Green
    Write-Host "L'interface sera disponible à l'adresse: http://localhost:$env:MATH_TRAINER_PORT" -ForegroundColor Yellow
    Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
    Write-Host
    
    # Exécuter le serveur amélioré
    python $projectRoot\enhanced_server.py
}
catch {
    Write-Host "Erreur lors du démarrage du serveur:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host 
    Write-Host "Vérifiez que Python est installé et que les dépendances sont disponibles." -ForegroundColor Yellow
} 