# =======================================================
# Script pour vérifier la validité des variables d'environnement
# Ce script détecte les problèmes potentiels dans la configuration
# =======================================================

[CmdletBinding()]
param (
    [Parameter()]
    [string]$EnvFile,
    
    [Parameter()]
    [switch]$Verbose,
    
    [Parameter()]
    [switch]$Help
)

# Si l'aide est demandée, afficher les informations et sortir
if ($Help) {
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "   Vérification des variables d'environnement" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Options:"
    Write-Host "  -EnvFile <fichier>    Spécifier un fichier .env à valider"
    Write-Host "  -Verbose              Afficher plus de détails"
    Write-Host "  -Help                 Afficher cette aide"
    Write-Host
    return
}

# Déterminer le chemin du script et du répertoire du projet
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Définir le chemin par défaut du fichier .env si non spécifié
if (-not $EnvFile) {
    $EnvFile = Join-Path -Path $ProjectRoot -ChildPath ".env"
}

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   Vérification des variables d'environnement" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host

# Vérifier si Python est disponible
try {
    $pythonVersion = python --version
    Write-Host "Python trouvé: $pythonVersion"
} catch {
    Write-Host "[ERREUR] Python n'est pas disponible. Veuillez l'installer." -ForegroundColor Red
    exit 1
}

# Définir les arguments Python
$pythonArgs = @()
if ($Verbose) {
    $pythonArgs += "--verbose"
}

# Vérifier si le fichier .env existe
if (-not (Test-Path $EnvFile)) {
    Write-Host "[ATTENTION] Le fichier $EnvFile n'existe pas." -ForegroundColor Yellow
    Write-Host "Utilisation des variables d'environnement système."
    
    # Valider les variables d'environnement système
    $validateScript = Join-Path -Path $ScriptDir -ChildPath "validate_env.py"
    python $validateScript $pythonArgs
    $returnCode = $LASTEXITCODE
} else {
    Write-Host "Validation du fichier $EnvFile..." -ForegroundColor Yellow
    
    # Valider le fichier .env
    $validateScript = Join-Path -Path $ScriptDir -ChildPath "validate_env.py"
    python $validateScript --env-file $EnvFile $pythonArgs
    $returnCode = $LASTEXITCODE
    
    if ($returnCode -ne 0) {
        Write-Host
        Write-Host "[ATTENTION] Des problèmes ont été détectés dans votre configuration." -ForegroundColor Yellow
        Write-Host "Vous pouvez corriger manuellement le fichier $EnvFile"
        Write-Host "ou utiliser les scripts de configuration:"
        Write-Host
        Write-Host ".\scripts\Config-Menu.ps1          # Menu interactif de configuration" -ForegroundColor Cyan
        Write-Host ".\scripts\utils\env_manager.ps1    # Gestion en ligne de commande" -ForegroundColor Cyan
    } else {
        Write-Host
        Write-Host "[OK] La configuration est valide." -ForegroundColor Green
    }
}

exit $returnCode 