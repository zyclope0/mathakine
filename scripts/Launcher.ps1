<#
.SYNOPSIS
    Lanceur principal pour Mathakine en PowerShell
.DESCRIPTION
    Menu simplifié permettant d'accéder aux principales fonctionnalités
    de Mathakine via des scripts PowerShell ou batch
#>

function Show-Menu {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Mathakine - Lanceur PowerShell" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "Options disponibles:" -ForegroundColor Yellow
    Write-Host
    Write-Host "  [1] Démarrer le serveur (direct, mode simple)"
    Write-Host "  [2] Vérifier l'environnement et les chemins"
    Write-Host "  [3] Réinitialiser le fichier .env"
    Write-Host "  [4] Configuration avancée"
    Write-Host "  [5] Menu complet (scripts.bat original)"
    Write-Host
    Write-Host "  [0] Quitter"
    Write-Host
    $choice = Read-Host "Votre choix"
    return $choice
}

while ($true) {
    $choice = Show-Menu
    
    switch ($choice) {
        "1" {
            Clear-Host
            Write-Host "Démarrage du serveur..." -ForegroundColor Green
            
            # Si le script PowerShell existe, l'utiliser, sinon utiliser le batch
            if (Test-Path ".\Start-Direct.ps1") {
                & .\Start-Direct.ps1
            } else {
                Write-Host "Utilisation du script batch..." -ForegroundColor Yellow
                cmd.exe /c start_direct.bat
            }
        }
        
        "2" {
            Clear-Host
            Write-Host "Vérification de l'environnement..." -ForegroundColor Green
            
            if (Test-Path ".\Test-Paths.ps1") {
                & .\Test-Paths.ps1
            } else {
                Write-Host "Utilisation du script batch..." -ForegroundColor Yellow
                cmd.exe /c test_paths.bat
            }
        }
        
        "3" {
            Clear-Host
            Write-Host "Réinitialisation du fichier .env..." -ForegroundColor Green
            
            if (Test-Path ".\scripts\utils\Reset-Env.ps1") {
                & .\scripts\utils\Reset-Env.ps1
            } else {
                Write-Host "Utilisation du script batch..." -ForegroundColor Yellow
                cmd.exe /c scripts\utils\reset_env.bat
            }
        }
        
        "4" {
            Clear-Host
            Write-Host "Configuration avancée..." -ForegroundColor Green
            
            if (Test-Path ".\scripts\Config-Menu.ps1") {
                & .\scripts\Config-Menu.ps1
            } else {
                Write-Host "Utilisation du script batch..." -ForegroundColor Yellow
                cmd.exe /c scripts\config_menu.bat
            }
        }
        
        "5" {
            Clear-Host
            Write-Host "Lancement du menu complet..." -ForegroundColor Green
            cmd.exe /c scripts.bat
        }
        
        "0" {
            Clear-Host
            Write-Host "Au revoir!" -ForegroundColor Green
            exit
        }
        
        default {
            Write-Host "Option invalide. Veuillez réessayer." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} 