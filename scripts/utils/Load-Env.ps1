<#
.SYNOPSIS
    Script de chargement des variables d'environnement pour les scripts PowerShell.
.DESCRIPTION
    Ce script permet aux autres scripts PowerShell de charger facilement
    les variables d'environnement à partir du fichier .env ou des profils prédéfinis.
.PARAMETER Profile
    Le profil d'environnement à utiliser: dev, test, ou prod.
.EXAMPLE
    . .\Load-Env.ps1 -Profile dev
    # Charge le profil de développement et rend les variables disponibles
.NOTES
    Doit être appelé avec le "dot sourcing" (.) pour que les variables soient disponibles
    dans le script appelant.
#>

[CmdletBinding()]
param (
    [Parameter()]
    [ValidateSet("dev", "test", "prod")]
    [string]$Profile = "dev"
)

# Vérifier si on est exécuté avec dot sourcing
$isDotSourced = $MyInvocation.InvocationName -eq '.'
if (-not $isDotSourced) {
    Write-Warning "Ce script doit être appelé avec dot sourcing pour exporter les variables"
    Write-Warning "Exemple: . .\Load-Env.ps1 -Profile dev"
}

# Chemins vers les fichiers requis
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$envManagerPath = Join-Path $scriptPath "env_manager.ps1"
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$envFilePath = Join-Path $projectRoot ".env"

# Vérifier l'existence du script env_manager.ps1
if (-not (Test-Path $envManagerPath)) {
    Write-Error "Fichier env_manager.ps1 introuvable: $envManagerPath"
    return 1
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path $envFilePath)) {
    try {
        & $envManagerPath -Profile $Profile -Export
    }
    catch {
        Write-Error "Échec de création du fichier .env: $_"
        return 1
    }
}

# Charger les variables d'environnement
$envVars = & $envManagerPath -Profile $Profile

# Exporter les variables dans le scope parent (si en dot-sourcing)
if ($isDotSourced) {
    foreach ($key in $envVars.Keys) {
        Set-Variable -Name $key -Value $envVars[$key] -Scope 1
    }
    
    # Ajouter une variable spéciale pour indiquer le profil utilisé
    Set-Variable -Name "MATH_TRAINER_PROFILE" -Value $Profile -Scope 1
}

# Renvoyer les variables même si pas appelé avec dot sourcing
return $envVars 