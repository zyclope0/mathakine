<#
.SYNOPSIS
    Script de réinitialisation du fichier .env pour Mathakine.
.DESCRIPTION
    Ce script va supprimer le fichier .env existant et en créer un nouveau
    avec les paramètres par défaut selon le profil choisi.
#>

# Définir les chemins
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Get-Item "$scriptPath\..\..\").FullName
$envFile = Join-Path -Path $projectRoot -ChildPath ".env"

# Afficher le titre
Clear-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Mathakine - Réinitialisation du fichier .env" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host

# Demander confirmation à l'utilisateur
Write-Host "Ce script va supprimer votre fichier .env actuel et" -ForegroundColor Yellow
Write-Host "créer un nouveau fichier avec les paramètres par défaut." -ForegroundColor Yellow
Write-Host

$confirm = Read-Host "Êtes-vous sûr de vouloir continuer ? (O/N)"

if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "Opération annulée." -ForegroundColor Red
    exit
}

# Supprimer le fichier .env existant s'il existe
if (Test-Path $envFile) {
    Remove-Item -Path $envFile -Force
    Write-Host "Fichier .env supprimé." -ForegroundColor Green
}

# Demander quel profil utiliser
Write-Host
Write-Host "Choisissez le profil pour le nouveau fichier .env :" -ForegroundColor Yellow
Write-Host "  1. DEV (développement) - Port 8081"
Write-Host "  2. TEST - Port 8082"
Write-Host "  3. PROD (production) - Port 8080"
Write-Host

$profileChoice = Read-Host "Votre choix (1-3, défaut=1)"

# Définir le profil en fonction du choix
$profile = "dev"
$port = 8081
$debug = "true"
$logLevel = "DEBUG"
$testMode = "true"

if ($profileChoice -eq "2") {
    $profile = "test"
    $port = 8082
    $logLevel = "INFO"
} elseif ($profileChoice -eq "3") {
    $profile = "prod"
    $port = 8080
    $debug = "false"
    $logLevel = "WARNING"
    $testMode = "false"
}

# Créer le nouveau fichier .env
$envContent = @"
# Fichier d'environnement Math Trainer
# Généré le $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

DATABASE_URL=sqlite:///./math_trainer.db
MATH_TRAINER_DEBUG=$debug
MATH_TRAINER_LOG_LEVEL=$logLevel
MATH_TRAINER_PORT=$port
MATH_TRAINER_PROFILE=$profile
MATH_TRAINER_TEST_MODE=$testMode
"@

$envContent | Out-File -FilePath $envFile -Encoding UTF8

Write-Host
Write-Host "Fichier .env créé avec succès avec le profil $profile." -ForegroundColor Green
Write-Host
Write-Host "Configuration :" -ForegroundColor Cyan
Write-Host "  - Profil: $profile"
Write-Host "  - Port: $port"
Write-Host "  - Debug: $debug"
Write-Host "  - Log Level: $logLevel"
Write-Host "  - Test Mode: $testMode"

Write-Host
Write-Host "Appuyez sur une touche pour continuer..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 