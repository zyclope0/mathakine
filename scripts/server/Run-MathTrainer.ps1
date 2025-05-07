# =======================================================
# Script launcher pour Math Trainer
# Ce script sert de wrapper pour exécuter le serveur Math Trainer
# directement en PowerShell (plus besoin du script batch)
# =======================================================

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   Math Trainer Backend - Launcher PowerShell" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host

# Obtenir le chemin du script et du projet
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)

# Se placer dans le dossier racine du projet
Set-Location -Path $projectRoot
Write-Host "Répertoire actuel: $PWD"
Write-Host

# Importer les variables d'environnement (optionnel, si disponible)
$envFile = Join-Path -Path $projectRoot -ChildPath ".env"
if (Test-Path $envFile) {
    Write-Host "Chargement des variables d'environnement..."
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value)
            # Pour le debugging: Write-Host "Variable définie: $key=$value"
        }
    }
    Write-Host
}

# Afficher la version de Python
python --version
Write-Host

# Récupérer les variables d'environnement pour l'affichage
$profile = [Environment]::GetEnvironmentVariable("MATH_TRAINER_PROFILE") -or "dev"
$port = [Environment]::GetEnvironmentVariable("MATH_TRAINER_PORT") -or "8080"
$debug = [Environment]::GetEnvironmentVariable("MATH_TRAINER_DEBUG") -or "false"

Write-Host "Configuration actuelle:" -ForegroundColor Yellow
Write-Host "- Profil: $profile"
Write-Host "- Port: $port"
Write-Host "- Mode debug: $debug"
Write-Host

Write-Host "Veuillez choisir l'option de serveur à démarrer:" -ForegroundColor Yellow
Write-Host
Write-Host "1 - Serveur minimal (simple API, sans interface graphique)"
Write-Host "2 - Serveur amélioré (avec interface graphique complète)"
Write-Host "3 - Configurer l'environnement avant démarrage"
Write-Host

$choix = Read-Host "Entrez votre choix (1, 2 ou 3)"

if ($choix -eq "1") {
    Write-Host
    Write-Host "Démarrage du serveur minimal sur le port $port..." -ForegroundColor Cyan
    Write-Host
    python (Join-Path -Path $projectRoot -ChildPath "minimal_server.py")
}
elseif ($choix -eq "2") {
    Write-Host
    Write-Host "Démarrage du serveur amélioré sur le port $port..." -ForegroundColor Cyan
    Write-Host
    python (Join-Path -Path $projectRoot -ChildPath "enhanced_server.py")
}
elseif ($choix -eq "3") {
    Write-Host
    Write-Host "Configuration de l'environnement..." -ForegroundColor Cyan
    Write-Host
    
    # Appeler le script de configuration
    $configScript = Join-Path -Path $projectRoot -ChildPath "scripts\Config-Menu.ps1"
    if (Test-Path $configScript) {
        & $configScript
    } else {
        Write-Host "Script de configuration introuvable: $configScript" -ForegroundColor Red
    }
    
    # Demander si l'utilisateur souhaite démarrer un serveur
    Write-Host
    $restart = Read-Host "Souhaitez-vous démarrer un serveur maintenant? (O/N)"
    
    if ($restart -eq "O" -or $restart -eq "o") {
        Clear-Host
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host "   Math Trainer Backend - Choix du serveur" -ForegroundColor Cyan
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host
        
        # Recharger les variables d'environnement
        if (Test-Path $envFile) {
            Get-Content $envFile | ForEach-Object {
                if ($_ -match "^([^#=]+)=(.*)$") {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    [Environment]::SetEnvironmentVariable($key, $value)
                }
            }
        }
        
        # Récupérer les nouvelles valeurs
        $profile = [Environment]::GetEnvironmentVariable("MATH_TRAINER_PROFILE") -or "dev"
        $port = [Environment]::GetEnvironmentVariable("MATH_TRAINER_PORT") -or "8080"
        $debug = [Environment]::GetEnvironmentVariable("MATH_TRAINER_DEBUG") -or "false"
        
        Write-Host "Configuration actuelle:" -ForegroundColor Yellow
        Write-Host "- Profil: $profile"
        Write-Host "- Port: $port"
        Write-Host "- Mode debug: $debug"
        Write-Host
        
        Write-Host "1 - Serveur minimal (simple API)"
        Write-Host "2 - Serveur amélioré (interface graphique)"
        Write-Host
        
        $serverChoice = Read-Host "Entrez votre choix (1 ou 2)"
        
        if ($serverChoice -eq "1") {
            python (Join-Path -Path $projectRoot -ChildPath "minimal_server.py")
        } else {
            python (Join-Path -Path $projectRoot -ChildPath "enhanced_server.py")
        }
    }
}
else {
    Write-Host
    Write-Host "Choix invalide! Utilisation du serveur amélioré par défaut..." -ForegroundColor Yellow
    Write-Host
    python (Join-Path -Path $projectRoot -ChildPath "enhanced_server.py")
}

# Pause à la fin pour permettre à l'utilisateur de voir les résultats
Write-Host
Write-Host "Appuyez sur une touche pour quitter..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 