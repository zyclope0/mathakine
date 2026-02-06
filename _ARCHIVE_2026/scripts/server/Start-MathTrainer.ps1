# Mathakine - Script PowerShell
Write-Host "===================================================" -ForegroundColor Green
Write-Host "   Mathakine Backend - Choix du serveur" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Se placer dans le dossier du projet principal
Set-Location $PSScriptRoot
Set-Location ..\..\
$projectRoot = $PWD.Path

Write-Host "Répertoire actuel: $PWD"
Write-Host ""

# Vérifier si le fichier .env existe
if (-not (Test-Path "$projectRoot\.env")) {
    Write-Host "[INFO] Fichier .env non trouvé, initialisation de l'environnement..." -ForegroundColor Yellow
    & "$projectRoot\scripts\utils\init_env.bat"
}

# Charger les variables d'environnement
$envFile = Get-Content "$projectRoot\.env" -ErrorAction SilentlyContinue
if ($envFile) {
    foreach ($line in $envFile) {
        if ($line -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Afficher la version de Python
python --version
Write-Host ""

# Afficher la configuration
Write-Host "Configuration actuelle:" -ForegroundColor Cyan
Write-Host "- Profil: $env:MATH_TRAINER_PROFILE"
Write-Host "- Port: $env:MATH_TRAINER_PORT"
Write-Host "- Mode debug: $env:MATH_TRAINER_DEBUG"
Write-Host ""

# Vérifier que les variables sont définies
if (-not $env:MATH_TRAINER_PROFILE -or -not $env:MATH_TRAINER_PORT) {
    Write-Host "[ERREUR] Variables d'environnement manquantes" -ForegroundColor Red
    Write-Host "Réinitialisation du fichier .env recommandée:" -ForegroundColor Yellow
    Write-Host "   scripts\utils\init_env.bat" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host "Veuillez choisir l'option de serveur à démarrer:"
Write-Host ""
Write-Host "1 - Serveur minimal (simple API, sans interface graphique)"
Write-Host "2 - Serveur amélioré (avec interface graphique complète)"
Write-Host "3 - Configurer l'environnement avant démarrage"
Write-Host ""

$choix = Read-Host "Entrez votre choix (1, 2 ou 3)"

try {
    if ($choix -eq "1") {
        Write-Host ""
        Write-Host "Démarrage du serveur minimal sur le port $env:MATH_TRAINER_PORT..." -ForegroundColor Cyan
        Write-Host ""
        python "$projectRoot\minimal_server.py"
    }
    elseif ($choix -eq "2") {
        Write-Host ""
        Write-Host "Démarrage du serveur amélioré sur le port $env:MATH_TRAINER_PORT..." -ForegroundColor Cyan
        Write-Host ""
        python "$projectRoot\enhanced_server.py"
    }
    elseif ($choix -eq "3") {
        Write-Host ""
        Write-Host "Configuration de l'environnement..." -ForegroundColor Cyan
        Write-Host ""
        & "$projectRoot\scripts\config_menu.bat"
        
        # Recharger les variables après configuration
        $envFile = Get-Content "$projectRoot\.env"
        foreach ($line in $envFile) {
            if ($line -match '^([^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                Set-Item -Path "env:$name" -Value $value
            }
        }
        
        Write-Host ""
        $restart = Read-Host "Souhaitez-vous démarrer un serveur maintenant? (O/N)"
        
        if ($restart -eq "O" -or $restart -eq "o") {
            Clear-Host
            Write-Host "===================================================" -ForegroundColor Green
            Write-Host "   Mathakine Backend - Choix du serveur" -ForegroundColor Green
            Write-Host "===================================================" -ForegroundColor Green
            Write-Host ""
            
            Write-Host "Configuration actuelle:" -ForegroundColor Cyan
            Write-Host "- Profil: $env:MATH_TRAINER_PROFILE"
            Write-Host "- Port: $env:MATH_TRAINER_PORT"
            Write-Host "- Mode debug: $env:MATH_TRAINER_DEBUG"
            Write-Host ""
            
            Write-Host "1 - Serveur minimal (simple API)"
            Write-Host "2 - Serveur amélioré (interface graphique)"
            Write-Host ""
            $serverChoice = Read-Host "Entrez votre choix (1 ou 2)"
            
            if ($serverChoice -eq "1") {
                python "$projectRoot\minimal_server.py"
            }
            else {
                python "$projectRoot\enhanced_server.py"
            }
        }
    }
    else {
        Write-Host ""
        Write-Host "Choix invalide! Utilisation du serveur amélioré par défaut..." -ForegroundColor Yellow
        Write-Host ""
        python "$projectRoot\enhanced_server.py"
    }
}
catch {
    Write-Host "[ERREUR] Une erreur s'est produite:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Pause à la fin
Write-Host "Appuyez sur une touche pour quitter..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 