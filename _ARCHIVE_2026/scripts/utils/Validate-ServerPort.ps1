# ===================================================
# Script pour valider que le port du serveur correspond à l'environnement
# Version PowerShell
# ===================================================

param(
    [switch]$Check,
    [switch]$Fix,
    [switch]$Verbose,
    [switch]$Help
)

# Afficher l'aide si demandé
if ($Help) {
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Validation du port serveur Math Trainer" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Ce script vérifie que le port configuré dans l'environnement correspond"
    Write-Host "au port utilisé par le serveur en cours d'exécution."
    Write-Host
    Write-Host "Options:"
    Write-Host "  -Check       Vérifier sans modifier (par défaut)"
    Write-Host "  -Fix         Modifier le fichier .env pour corriger le port"
    Write-Host "  -Verbose     Afficher plus d'informations"
    Write-Host "  -Help        Afficher cette aide"
    
    exit 0
}

# Définir les chemins
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptPath\..\..").FullName
$EnvManagerPath = Join-Path -Path $ProjectRoot -ChildPath "scripts\utils\env_manager.ps1"
$ResultsDir = Join-Path -Path $ProjectRoot -ChildPath "test_results"

# Créer le répertoire de résultats si nécessaire
if (-not (Test-Path -Path $ResultsDir)) {
    New-Item -Path $ResultsDir -ItemType Directory | Out-Null
}

# Définir les ports attendus pour chaque environnement
$PortDev = 8081
$PortTest = 8082
$PortProd = 8080

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Validation du port serveur Math Trainer" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

# Récupérer le profil actuel et le port configuré
$envVariables = & $EnvManagerPath -List | Out-String
$currentProfile = ($envVariables -split "`n" | Where-Object { $_ -match "MATH_TRAINER_PROFILE" } | ForEach-Object { $_.Split("=")[1].Trim() })
$configuredPort = [int]($envVariables -split "`n" | Where-Object { $_ -match "MATH_TRAINER_PORT" } | ForEach-Object { $_.Split("=")[1].Trim() })

# Déterminer le port attendu en fonction du profil
$expectedPort = 0
switch -Exact ($currentProfile) {
    "dev" { $expectedPort = $PortDev }
    "test" { $expectedPort = $PortTest }
    "prod" { $expectedPort = $PortProd }
    default {
        Write-Host "[ERREUR] Profil non reconnu: $currentProfile" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Profil actuel: $currentProfile" -ForegroundColor Yellow
Write-Host "Port configuré: $configuredPort" -ForegroundColor Yellow
Write-Host "Port attendu: $expectedPort" -ForegroundColor Yellow
Write-Host

# Vérifier si le serveur est en cours d'exécution
Write-Host "Vérification du serveur en cours d'exécution..." -ForegroundColor Yellow
$serverRunning = $false
$activePort = 0
$ports = @($PortDev, $PortTest, $PortProd)

foreach ($port in $ports) {
    if ($Verbose) {
        Write-Host "Vérification du port $port..." -ForegroundColor Gray
    }
    
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:$port/status" -UseBasicParsing -ErrorAction Stop
        $serverRunning = $true
        $activePort = $port
        
        if ($Verbose) {
            Write-Host "Serveur trouvé sur le port $port" -ForegroundColor Green
        }
        
        break
    }
    catch {
        # Aucun serveur sur ce port, continuer
    }
}

if (-not $serverRunning) {
    Write-Host "[INFO] Aucun serveur en cours d'exécution." -ForegroundColor Yellow
    Write-Host
    
    # Vérifier si la configuration est cohérente avec le profil
    if ($configuredPort -eq $expectedPort) {
        Write-Host "[OK] Le port configuré ($configuredPort) correspond au profil ($currentProfile)." -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host "[AVERTISSEMENT] Le port configuré ($configuredPort) ne correspond pas au profil ($currentProfile)." -ForegroundColor Yellow
        
        if ($Fix) {
            Write-Host "Correction du port..." -ForegroundColor Yellow
            & $EnvManagerPath -Key "MATH_TRAINER_PORT" -Value $expectedPort -Export
            Write-Host "[OK] Port corrigé dans le fichier .env." -ForegroundColor Green
        }
        else {
            Write-Host "Pour corriger, utilisez l'option -Fix." -ForegroundColor Yellow
        }
        exit 1
    }
}
else {
    Write-Host "Serveur en cours d'exécution sur le port $activePort" -ForegroundColor Green
    
    # Récupérer le profil du serveur actif
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:$activePort/status" -Method Get
    $activeProfile = $statusResponse.profile
    
    Write-Host "Profil du serveur actif: $activeProfile" -ForegroundColor Yellow
    Write-Host
    
    # Vérifier si le port actif correspond au profil actif
    if ($activePort -eq $expectedPort) {
        Write-Host "[OK] Le serveur utilise le port correct pour le profil $currentProfile." -ForegroundColor Green
    }
    else {
        Write-Host "[AVERTISSEMENT] Le serveur utilise un port ($activePort) qui ne correspond pas au profil actuel ($currentProfile)." -ForegroundColor Yellow
        Write-Host "Le port attendu pour le profil $currentProfile est $expectedPort." -ForegroundColor Yellow
        Write-Host
        
        if ($activeProfile -eq $currentProfile) {
            Write-Host "[AVERTISSEMENT] Le serveur utilise le bon profil mais le mauvais port." -ForegroundColor Yellow
            
            if ($Fix) {
                Write-Host "Pour corriger ce problème, veuillez redémarrer le serveur." -ForegroundColor Yellow
            }
            else {
                Write-Host "Pour résoudre ce problème, redémarrez le serveur." -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "[AVERTISSEMENT] Le serveur utilise un profil ($activeProfile) différent du profil actuel ($currentProfile)." -ForegroundColor Yellow
            
            if ($Fix) {
                Write-Host "Adaptation du fichier .env au serveur en cours d'exécution..." -ForegroundColor Yellow
                
                # Déterminer le port attendu pour le profil actif du serveur
                $serverExpectedPort = 0
                switch -Exact ($activeProfile) {
                    "dev" { $serverExpectedPort = $PortDev }
                    "test" { $serverExpectedPort = $PortTest }
                    "prod" { $serverExpectedPort = $PortProd }
                }
                
                if ($activePort -eq $serverExpectedPort) {
                    & $EnvManagerPath -Profile $activeProfile -Export
                    Write-Host "[OK] Environnement adapté au serveur en cours d'exécution." -ForegroundColor Green
                }
                else {
                    & $EnvManagerPath -Profile $activeProfile -Export
                    & $EnvManagerPath -Key "MATH_TRAINER_PORT" -Value $activePort -Export
                    Write-Host "[OK] Environnement et port adaptés au serveur en cours d'exécution." -ForegroundColor Green
                }
            }
            else {
                Write-Host "Pour adapter l'environnement au serveur, utilisez l'option -Fix." -ForegroundColor Yellow
            }
        }
        exit 1
    }
}

exit 0 