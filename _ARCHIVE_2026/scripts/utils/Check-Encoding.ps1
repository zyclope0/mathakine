# Script pour vérifier l'encodage des fichiers du projet
# Ce script identifie les fichiers avec des problèmes d'encodage des caractères accentués

# Déterminer le chemin du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Se placer dans le répertoire du script
Set-Location -Path $ScriptDir

# Vérifier si Python est disponible
try {
    $pythonVersion = python --version
    Write-Host "Python trouvé: $pythonVersion"
} catch {
    Write-Host "Erreur: Python n'est pas disponible dans le PATH." -ForegroundColor Red
    exit 1
}

# Installer colorama si nécessaire (pour les couleurs dans la console)
try {
    $coloramaInstalled = python -c "import colorama" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation du module colorama pour l'affichage en couleur..." -ForegroundColor Yellow
        python -m pip install colorama
    }
} catch {
    Write-Host "Erreur lors de la vérification/installation de colorama: $_" -ForegroundColor Red
}

# Installer chardet si nécessaire (pour la détection d'encodage)
try {
    $chardetInstalled = python -c "import chardet" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation du module chardet pour la détection d'encodage..." -ForegroundColor Yellow
        python -m pip install chardet
    }
} catch {
    Write-Host "Erreur lors de la vérification/installation de chardet: $_" -ForegroundColor Red
}

# Exécuter le script de vérification d'encodage
Write-Host "Exécution de la vérification d'encodage..." -ForegroundColor Cyan
python check_encoding.py

# Récupérer le code de retour
$exitCode = $LASTEXITCODE

# Retourner le code de sortie
exit $exitCode 