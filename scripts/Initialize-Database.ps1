# Initialisation de la base de données Mathakine

Write-Host "Initialisation de la base de données Mathakine" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Vérifier si Python est installé et la version
try {
    $pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
    Write-Host "Python détecté: $pythonVersion" -ForegroundColor Green
    
    # Vérifier la compatibilité de la version
    $versionParts = $pythonVersion.Split('.')
    $majorVersion = [int]$versionParts[0]
    $minorVersion = [int]$versionParts[1]
    
    if ($majorVersion -eq 3 -and $minorVersion -ge 8 -and $minorVersion -le 13) {
        Write-Host "Version de Python compatible" -ForegroundColor Green
        
        if ($minorVersion -eq 13) {
            Write-Host "Note: Python 3.13 est supporté avec les versions appropriées des dépendances:" -ForegroundColor Yellow
            Write-Host "- SQLAlchemy 2.0.27+" -ForegroundColor Yellow
            Write-Host "- pydantic 2.0.0+ avec pydantic-settings" -ForegroundColor Yellow
            Write-Host "- FastAPI 0.100.0+" -ForegroundColor Yellow
            Write-Host
        }
    } else {
        Write-Host "Version de Python non supportée. Veuillez utiliser Python 3.8 à 3.13" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python 3.8 à 3.13" -ForegroundColor Red
    exit 1
}

# Vérifier si l'environnement virtuel existe
if (-not (Test-Path -Path "venv")) {
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Installer les dépendances
Write-Host "Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt

# Exécuter le script d'initialisation de la base de données
Write-Host "Initialisation de la base de données..." -ForegroundColor Yellow
python scripts/create_database.py

# Désactiver l'environnement virtuel
Write-Host "Désactivation de l'environnement virtuel..." -ForegroundColor Yellow
deactivate

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Base de données initialisée avec succès!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant lancer le serveur avec run_server.bat ou Scripts-Menu.ps1" -ForegroundColor Green

Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 