<#
.SYNOPSIS
    Menu interactif de configuration des environnements pour Math Trainer.
.DESCRIPTION
    Permet de gérer les différents profils d'environnement (dev, test, prod)
    et de configurer les variables d'environnement pour le projet Math Trainer.
.NOTES
    Auteur: Claude
    Date: 2024
#>

# Chemins des fichiers nécessaires
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvManagerPath = Join-Path -Path (Join-Path -Path $ScriptPath -ChildPath "utils") -ChildPath "env_manager.ps1"
$ProjectRoot = Split-Path -Parent $ScriptPath
$EnvFilePath = Join-Path -Path $ProjectRoot -ChildPath ".env"
$ScriptDir = Split-Path -Parent $ScriptPath

# Vérifier l'existence du gestionnaire d'environnement
if (-not (Test-Path $EnvManagerPath)) {
    Write-Error "Fichier env_manager.ps1 introuvable: $EnvManagerPath"
    exit 1
}

function Show-Menu {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Math Trainer - Menu de Configuration" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "  1. Afficher la configuration actuelle"
    Write-Host "  2. Utiliser le profil DEV (développement)"
    Write-Host "  3. Utiliser le profil TEST"
    Write-Host "  4. Utiliser le profil PROD (production)"
    Write-Host "  5. Modifier une variable d'environnement"
    Write-Host "  6. Ouvrir le fichier .env dans un éditeur"
    Write-Host "  7. Créer ou réinitialiser le fichier .env"
    Write-Host "  8. Configurer la clé API OpenAI"
    Write-Host "  9. Créer le fichier .env.example (modèle)"
    Write-Host "  R. Réparer la configuration (reset complet)"
    Write-Host "  0. Retour au menu principal"
    Write-Host
    
    $choice = Read-Host "Votre choix (0-9, R)"
    return $choice
}

function Show-CurrentConfig {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Configuration Actuelle" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    
    # Vérifier si le fichier .env existe
    if (-not (Test-Path $EnvFilePath)) {
        Write-Host "Le fichier .env n'existe pas encore." -ForegroundColor Yellow
        Write-Host
        Write-Host "Création d'un fichier .env par défaut (profil DEV)..." -ForegroundColor Yellow
        & $EnvManagerPath -Profile dev -Export
        Start-Sleep -Seconds 1
    }
    
    # Afficher la configuration actuelle
    & $EnvManagerPath -Profile dev -List
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Set-Profile {
    param (
        [string]$Profile
    )
    
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Application du profil $Profile" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    
    & $EnvManagerPath -Profile $Profile -Export
    
    Write-Host
    Write-Host "Le profil $Profile a été appliqué avec succès." -ForegroundColor Green
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Edit-EnvVariable {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Modification d'une variable d'environnement" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Variables disponibles :" -ForegroundColor Yellow
    Write-Host
    Write-Host "  - MATH_TRAINER_DEBUG (true/false)"
    Write-Host "  - MATH_TRAINER_PORT (numéro de port)"
    Write-Host "  - MATH_TRAINER_LOG_LEVEL (DEBUG/INFO/WARNING/ERROR)"
    Write-Host "  - MATH_TRAINER_TEST_MODE (true/false)"
    Write-Host "  - OPENAI_API_KEY (clé API)"
    Write-Host "  - MATH_TRAINER_PROFILE (nom du profil)"
    Write-Host
    
    $varName = Read-Host "Nom de la variable à modifier"
    if ([string]::IsNullOrWhiteSpace($varName)) {
        Write-Host "Nom de variable invalide." -ForegroundColor Red
        Start-Sleep -Seconds 2
        return
    }
    
    $varValue = Read-Host "Nouvelle valeur"
    
    # Mettre à jour la variable
    & $EnvManagerPath -Key $varName -Value $varValue -Export
    
    Write-Host
    Write-Host "Variable $varName mise à jour avec la valeur $varValue" -ForegroundColor Green
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Open-EnvFile {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Ouverture du fichier .env" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    
    # Vérifier si le fichier .env existe
    if (-not (Test-Path $EnvFilePath)) {
        Write-Host "Le fichier .env n'existe pas encore." -ForegroundColor Yellow
        Write-Host
        Write-Host "Création d'un fichier .env par défaut (profil DEV)..." -ForegroundColor Yellow
        & $EnvManagerPath -Profile dev -Export
        Start-Sleep -Seconds 1
    }
    
    # Ouvrir le fichier dans l'éditeur par défaut
    Write-Host "Ouverture du fichier $EnvFilePath..."
    
    # Utiliser notepad pour ouvrir le fichier (plus compatible)
    Start-Process "notepad.exe" -ArgumentList $EnvFilePath
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Reset-EnvFile {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Réinitialisation du fichier .env" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Cette action va réinitialiser toutes vos configurations." -ForegroundColor Yellow
    Write-Host
    
    $confirm = Read-Host "Êtes-vous sûr de vouloir continuer ? (O/N)"
    
    if ($confirm -eq "O" -or $confirm -eq "o") {
        Write-Host
        Write-Host "Choisissez le profil pour le nouveau fichier .env :" -ForegroundColor Yellow
        Write-Host
        Write-Host "  1. DEV (développement)"
        Write-Host "  2. TEST"
        Write-Host "  3. PROD (production)"
        Write-Host
        
        $profileChoice = Read-Host "Votre choix (1-3)"
        
        $profile = "dev"
        if ($profileChoice -eq "2") { $profile = "test" }
        if ($profileChoice -eq "3") { $profile = "prod" }
        
        # Supprimer le fichier existant s'il y en a un
        if (Test-Path $EnvFilePath) {
            Remove-Item $EnvFilePath -Force
        }
        
        # Créer un nouveau fichier
        & $EnvManagerPath -Profile $profile -Export
        
        Write-Host
        Write-Host "Fichier .env réinitialisé avec le profil $profile." -ForegroundColor Green
    }
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Set-ApiKey {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Configuration de la clé API OpenAI" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Entrez votre clé API OpenAI pour activer les fonctionnalités d'IA." -ForegroundColor Yellow
    Write-Host "(Vous pouvez obtenir une clé sur https://platform.openai.com)"
    Write-Host
    Write-Host "Pour annuler, laissez le champ vide et appuyez sur Entrée."
    Write-Host
    
    $apiKey = Read-Host "Clé API OpenAI"
    
    if (-not [string]::IsNullOrWhiteSpace($apiKey)) {
        # Mettre à jour la clé API
        & $EnvManagerPath -Key "OPENAI_API_KEY" -Value $apiKey -Export
        
        Write-Host
        Write-Host "Clé API OpenAI configurée avec succès." -ForegroundColor Green
    } else {
        Write-Host
        Write-Host "Configuration annulée." -ForegroundColor Yellow
    }
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Create-EnvExample {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Création du fichier .env.example (modèle)" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Cette action va créer un fichier modèle .env.example" -ForegroundColor Yellow
    Write-Host "à la racine du projet pour aider les nouveaux développeurs."
    Write-Host
    
    $createEnvExamplePath = Join-Path -Path (Join-Path -Path $ScriptPath -ChildPath "utils") -ChildPath "Create-EnvExample.ps1"
    
    & $createEnvExamplePath
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Ajouter la fonction pour réparer complètement la configuration
function Repair-EnvConfig {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Réparation complète du fichier .env" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Cette action va effectuer une remise à zéro complète de votre configuration." -ForegroundColor Yellow
    Write-Host "Utilisez cette option seulement si vous rencontrez des problèmes persistants." -ForegroundColor Yellow
    Write-Host
    
    & "$ScriptDir\utils\Reset-Env.ps1"
    
    Write-Host
    Write-Host "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Boucle principale du menu
while ($true) {
    $choice = Show-Menu
    
    switch ($choice) {
        "1" { Show-CurrentConfig }
        "2" { Set-Profile -Profile "dev" }
        "3" { Set-Profile -Profile "test" }
        "4" { Set-Profile -Profile "prod" }
        "5" { Edit-EnvVariable }
        "6" { Open-EnvFile }
        "7" { Reset-EnvFile }
        "8" { Set-ApiKey }
        "9" { Create-EnvExample }
        { $_ -eq "R" -or $_ -eq "r" } { Repair-EnvConfig }
        "0" { return }
        default {
            Write-Host "Choix invalide! Veuillez réessayer." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} 