<#
.SYNOPSIS
    Script de gestion des variables d'environnement pour Math Trainer.
.DESCRIPTION
    Ce script permet de gérer les variables d'environnement pour différents
    profils (développement, test, production) et facilite la configuration
    du projet Math Trainer dans différents environnements.
.NOTES
    Auteur: Claude
    Date: 2024
#>

[CmdletBinding()]
param (
    [Parameter()]
    [string]$Profile = "dev", # Valeurs possibles: dev, test, prod
    
    [Parameter()]
    [switch]$List,
    
    [Parameter()]
    [switch]$Export,
    
    [Parameter()]
    [string]$EnvFile = ".env",
    
    [Parameter()]
    [string]$Key,
    
    [Parameter()]
    [string]$Value,
    
    [Parameter()]
    [switch]$Help,
    
    [Parameter()]
    [switch]$Validate,
    
    [Parameter()]
    [switch]$Fix
)

# Si l'aide est demandée, afficher les informations et sortir
if ($Help) {
    Write-Host "===================================================`n" -ForegroundColor Cyan
    Write-Host "    Math Trainer - Aide de gestion d'environnement`n" -ForegroundColor Cyan
    Write-Host "===================================================`n" -ForegroundColor Cyan
    
    Write-Host "Profils disponibles:" -ForegroundColor Yellow
    Write-Host "  dev  - Environnement de développement (debug:true, port:8081)"
    Write-Host "  test - Environnement de test (debug:true, port:8082)"
    Write-Host "  prod - Environnement de production (debug:false, port:8080)`n"
    
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Profile <nom>   Définir le profil à utiliser"
    Write-Host "  -Export          Exporter les variables vers .env"
    Write-Host "  -List            Lister les variables du profil"
    Write-Host "  -Validate        Valider les variables d'environnement"
    Write-Host "  -Fix             Tenter de corriger les variables invalides"
    Write-Host "  -Key <nom>       Spécifier une variable"
    Write-Host "  -Value <val>     Définir la valeur d'une variable"
    Write-Host "  -Help            Afficher cette aide`n"
    
    return
}

# Chemin vers le fichier d'environnement
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptRoot)
$defaultEnvFile = Join-Path $projectRoot $EnvFile

# Fonction pour charger les profils à partir du fichier JSON
function Get-EnvironmentProfiles {
    $profilesPath = Join-Path $scriptRoot "profiles.json"
    
    if (-not (Test-Path $profilesPath)) {
        Write-Warning "Fichier de profils non trouvé: $profilesPath. Utilisation des valeurs par défaut."
        return $null
    }
    
    try {
        $profilesContent = Get-Content $profilesPath -Raw -Encoding UTF8
        
        # Convertir le JSON en objet PowerShell de manière compatible avec toutes les versions
        $profiles = ConvertFrom-Json $profilesContent
        
        # Convertir manuellement en hashtable pour compatibilité
        $result = @{}
        
        foreach ($property in $profiles.PSObject.Properties) {
            $profileName = $property.Name
            $profileValues = @{}
            
            # Convertir les propriétés du profil en hashtable
            foreach ($varProperty in $property.Value.PSObject.Properties) {
                $profileValues[$varProperty.Name] = $varProperty.Value
            }
            
            $result[$profileName] = $profileValues
        }
        
        return $result
    }
    catch {
        Write-Warning "Erreur lors du chargement des profils: $_. Utilisation des valeurs par défaut."
        return $null
    }
}

# Fonction pour obtenir un profil spécifique
function Get-ProfileVariables {
    param (
        [string]$ProfileName
    )
    
    # Essayer de charger les profils depuis le fichier JSON
    $profiles = Get-EnvironmentProfiles
    
    if ($profiles -and $profiles.ContainsKey($ProfileName)) {
        return $profiles[$ProfileName]
    }
    
    # Fallback si le chargement échoue
    Write-Warning "Utilisation des valeurs codées en dur pour le profil '$ProfileName'."
    
    # Profils d'environnement prédéfinis (fallback)
    $defaultProfiles = @{
        "dev" = @{
            "MATH_TRAINER_DEBUG" = "true"
            "MATH_TRAINER_PORT" = "8081"
            "MATH_TRAINER_LOG_LEVEL" = "DEBUG"
            "MATH_TRAINER_TEST_MODE" = "true"
            "MATH_TRAINER_PROFILE" = "dev"
        }
        "test" = @{
            "MATH_TRAINER_DEBUG" = "true"
            "MATH_TRAINER_PORT" = "8082"
            "MATH_TRAINER_LOG_LEVEL" = "INFO"
            "MATH_TRAINER_TEST_MODE" = "true"
            "MATH_TRAINER_PROFILE" = "test"
        }
        "prod" = @{
            "MATH_TRAINER_DEBUG" = "false"
            "MATH_TRAINER_PORT" = "8080"
            "MATH_TRAINER_LOG_LEVEL" = "WARNING"
            "MATH_TRAINER_TEST_MODE" = "false"
            "MATH_TRAINER_PROFILE" = "prod"
        }
    }
    
    # Si le profil n'existe pas dans le fallback, utiliser dev par défaut
    if (-not $defaultProfiles.ContainsKey($ProfileName)) {
        Write-Warning "Profil '$ProfileName' non trouvé, utilisation du profil 'dev'"
        $ProfileName = "dev"
    }
    
    return $defaultProfiles[$ProfileName]
}

function Import-EnvFile {
    param (
        [string]$FilePath = $defaultEnvFile
    )
    
    $envVars = @{}
    
    if (Test-Path $FilePath) {
        Get-Content $FilePath | ForEach-Object {
            $line = $_.Trim()
            if ($line -and -not $line.StartsWith('#')) {
                $key, $value = $line -split '=', 2
                $envVars[$key] = $value
            }
        }
    }
    
    return $envVars
}

function Export-EnvFile {
    param (
        [hashtable]$EnvVars,
        [string]$FilePath = $defaultEnvFile
    )
    
    $content = "# Fichier d'environnement Math Trainer`n"
    $content += "# Généré le $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    
    foreach ($key in $EnvVars.Keys | Sort-Object) {
        $content += "$key=$($EnvVars[$key])`n"
    }
    
    Set-Content -Path $FilePath -Value $content -Encoding UTF8
    Write-Host "Variables d'environnement exportées vers $FilePath" -ForegroundColor Green
}

function Set-EnvVar {
    param (
        [string]$Key,
        [string]$Value,
        [hashtable]$EnvVars
    )
    
    $EnvVars[$Key] = $Value
    return $EnvVars
}

# Fonction pour valider les variables d'environnement
function Test-EnvVars {
    param (
        [hashtable]$EnvVars,
        [switch]$Fix
    )
    
    # Créer un fichier temporaire pour la validation
    $tempEnvFile = [System.IO.Path]::GetTempFileName()
    
    # Écrire les variables dans le fichier temporaire
    $content = "# Fichier d'environnement temporaire pour validation`n"
    foreach ($key in $EnvVars.Keys) {
        $content += "$key=$($EnvVars[$key])`n"
    }
    Set-Content -Path $tempEnvFile -Value $content -Encoding UTF8
    
    # Valider les variables avec le script Python
    $validateScript = Join-Path $scriptRoot "validate_env.py"
    $validationOutput = & python $validateScript --env-file $tempEnvFile 2>&1
    $validationSuccess = $LASTEXITCODE -eq 0
    
    # Afficher les résultats de validation
    $validationOutput | ForEach-Object { Write-Host $_ }
    
    # Si la validation a échoué et que la correction est demandée
    if (-not $validationSuccess -and $Fix) {
        Write-Host "`nTentative de correction des variables..." -ForegroundColor Yellow
        
        # Corriger les valeurs booléennes
        foreach ($key in @("MATH_TRAINER_DEBUG", "MATH_TRAINER_TEST_MODE")) {
            if ($EnvVars.ContainsKey($key)) {
                $value = $EnvVars[$key]
                if ($value -ne "true" -and $value -ne "false") {
                    # Convertir les valeurs proches de true/false
                    if ($value -in @("yes", "y", "1", "on", "enabled", "active")) {
                        $EnvVars[$key] = "true"
                        Write-Host "  Corrigé: $key = true (était: $value)" -ForegroundColor Green
                    } else {
                        $EnvVars[$key] = "false"
                        Write-Host "  Corrigé: $key = false (était: $value)" -ForegroundColor Green
                    }
                }
            }
        }
        
        # Corriger les niveaux de log
        if ($EnvVars.ContainsKey("MATH_TRAINER_LOG_LEVEL")) {
            $value = $EnvVars["MATH_TRAINER_LOG_LEVEL"]
            $validLevels = @("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            if ($value.ToUpper() -notin $validLevels) {
                # Trouver le niveau le plus proche ou utiliser INFO par défaut
                $EnvVars["MATH_TRAINER_LOG_LEVEL"] = "INFO"
                Write-Host "  Corrigé: MATH_TRAINER_LOG_LEVEL = INFO (était: $value)" -ForegroundColor Green
            } else {
                # Normaliser la casse
                $EnvVars["MATH_TRAINER_LOG_LEVEL"] = $value.ToUpper()
            }
        }
        
        # Corriger les ports
        if ($EnvVars.ContainsKey("MATH_TRAINER_PORT")) {
            $value = $EnvVars["MATH_TRAINER_PORT"]
            $isValid = $false
            [int]$portNum = 0
            
            if ([int]::TryParse($value, [ref]$portNum)) {
                if ($portNum -lt 1024 -or $portNum -gt 65535) {
                    # Si le port est invalide, utiliser 8080 par défaut
                    $EnvVars["MATH_TRAINER_PORT"] = "8080"
                    Write-Host "  Corrigé: MATH_TRAINER_PORT = 8080 (était: $value)" -ForegroundColor Green
                }
            } else {
                # Si la valeur n'est pas un nombre, utiliser 8080 par défaut
                $EnvVars["MATH_TRAINER_PORT"] = "8080"
                Write-Host "  Corrigé: MATH_TRAINER_PORT = 8080 (était: $value)" -ForegroundColor Green
            }
        }
        
        # Corriger les profils
        if ($EnvVars.ContainsKey("MATH_TRAINER_PROFILE")) {
            $value = $EnvVars["MATH_TRAINER_PROFILE"]
            $validProfiles = @("dev", "test", "prod")
            if ($value.ToLower() -notin $validProfiles) {
                # Utiliser dev par défaut
                $EnvVars["MATH_TRAINER_PROFILE"] = "dev"
                Write-Host "  Corrigé: MATH_TRAINER_PROFILE = dev (était: $value)" -ForegroundColor Green
            } else {
                # Normaliser la casse (lowercase)
                $EnvVars["MATH_TRAINER_PROFILE"] = $value.ToLower()
            }
        }
        
        # Valider à nouveau après les corrections
        Write-Host "`nNouvelle validation après corrections:" -ForegroundColor Cyan
        
        # Mettre à jour le fichier temporaire
        $content = "# Fichier d'environnement temporaire pour validation`n"
        foreach ($key in $EnvVars.Keys) {
            $content += "$key=$($EnvVars[$key])`n"
        }
        Set-Content -Path $tempEnvFile -Value $content -Encoding UTF8
        
        # Valider à nouveau
        $validationOutput = & python $validateScript --env-file $tempEnvFile 2>&1
        $validationSuccess = $LASTEXITCODE -eq 0
        $validationOutput | ForEach-Object { Write-Host $_ }
    }
    
    # Supprimer le fichier temporaire
    Remove-Item -Path $tempEnvFile -Force
    
    return $EnvVars
}

# Fonction principale
function Main {
    # Obtenir les variables du profil sélectionné
    $profileVars = Get-ProfileVariables -ProfileName $Profile
    
    # Convertir de PSCustomObject à hashtable si nécessaire
    if ($profileVars -is [PSCustomObject]) {
        $hashtable = @{}
        $profileVars.PSObject.Properties | ForEach-Object { $hashtable[$_.Name] = $_.Value }
        $profileVars = $hashtable
    }
    
    # Importer les variables d'environnement existantes
    $envVars = Import-EnvFile
    
    # Fusionner avec les variables du profil
    foreach ($key in $profileVars.Keys) {
        $envVars[$key] = $profileVars[$key]
    }
    
    # Définir une variable spécifique si demandé
    if ($Key -and $Value) {
        $envVars = Set-EnvVar -Key $Key -Value $Value -EnvVars $envVars
        Write-Host "Variable '$Key' définie à '$Value'" -ForegroundColor Green
    }
    
    # Valider les variables d'environnement si demandé
    if ($Validate) {
        Write-Host "`nValidation des variables d'environnement..." -ForegroundColor Cyan
        $envVars = Test-EnvVars -EnvVars $envVars -Fix:$Fix
    }
    
    # Lister les variables d'environnement
    if ($List) {
        Write-Host "`nVariables d'environnement pour le profil: $Profile" -ForegroundColor Cyan
        Write-Host "====================================================" -ForegroundColor Cyan
        foreach ($key in $envVars.Keys | Sort-Object) {
            # Masquer les clés API et les mots de passe
            $value = $envVars[$key]
            if ($key -like "*API_KEY*" -or $key -like "*PASSWORD*" -or $key -like "*SECRET*") {
                $value = "********" + $value.Substring([Math]::Min($value.Length, 4))
            }
            Write-Host "$key = $value"
        }
    }
    
    # Exporter les variables dans un fichier .env
    if ($Export) {
        Export-EnvFile -EnvVars $envVars -FilePath $defaultEnvFile
    }
    
    # Retourner les variables si nécessaire
    return $envVars
}

# Exécution
$result = Main

# Si exécuté directement (pas en tant que module importé), retourner les variables
if ($MyInvocation.InvocationName -ne '.') {
    return $result
} 