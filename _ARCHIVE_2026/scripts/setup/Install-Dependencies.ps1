# Math Trainer - Installation des dépendances via PowerShell
Write-Host "===================================================" -ForegroundColor Green
Write-Host "   Math Trainer Backend - Installation des dépendances" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Se placer dans le dossier du script
Set-Location $PSScriptRoot
Write-Host "Répertoire actuel: $PWD"
Write-Host ""

# Afficher la version de Python
python --version
Write-Host ""

# Installation des dépendances
Write-Host "Installation des dépendances pour le serveur minimal..." -ForegroundColor Cyan
python -m pip install starlette==0.27.0 uvicorn==0.20.0
Write-Host ""

Write-Host "Installation des dépendances pour le serveur amélioré..." -ForegroundColor Cyan
python -m pip install jinja2==3.1.2 aiofiles==23.2.1
Write-Host ""

# Vérification de l'installation
Write-Host "Vérification de l'installation..." -ForegroundColor Cyan
try {
    python -c "import starlette; import uvicorn; import jinja2; import aiofiles; print('Toutes les dépendances sont correctement installées!')"
    Write-Host "Installation réussie!" -ForegroundColor Green
}
catch {
    Write-Host "Une erreur est survenue lors de la vérification. Certaines dépendances peuvent manquer." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Création du fichier .env s'il n'existe pas
if (-not (Test-Path .env)) {
    Write-Host "Création du fichier .env..." -ForegroundColor Cyan
    @"
DEBUG=True
DATABASE_URL=sqlite:///./math_trainer.db
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "Fichier .env créé avec succès!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation terminée. Vous pouvez maintenant exécuter :" -ForegroundColor Green
Write-Host "- ./Start-MathTrainer.ps1" -ForegroundColor Green
Write-Host "- python minimal_server.py" -ForegroundColor Green
Write-Host "- python enhanced_server.py" -ForegroundColor Green
Write-Host ""

# Pause à la fin
Write-Host "Appuyez sur une touche pour quitter..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 