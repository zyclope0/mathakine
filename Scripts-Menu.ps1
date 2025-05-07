# ===================================================
# Menu Principal de Mathakine - Version PowerShell
# Accès à tous les scripts du projet
# ===================================================

function Show-Menu {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Mathakine - Menu Principal (PowerShell)" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "  INSTALLATION ET CONFIGURATION" -ForegroundColor Yellow
    Write-Host "  ----------------------------"
    Write-Host "  1. Installation complète et démarrage"
    Write-Host "  2. Configuration des environnements"
    Write-Host
    Write-Host "  SERVEUR" -ForegroundColor Yellow
    Write-Host "  -------"
    Write-Host "  3. Démarrer le serveur Mathakine"
    Write-Host "  4. Démarrer le serveur minimal (API uniquement)"
    Write-Host "  5. Démarrer le serveur amélioré (Interface complète)"
    Write-Host
    Write-Host "  TESTS" -ForegroundColor Yellow
    Write-Host "  -----"
    Write-Host "  6. Exécuter tous les tests"
    Write-Host "  7. Tests automatiques rapides" 
    Write-Host "  8. Tester le système d'environnement"
    Write-Host "  9. Tester les endpoints API"
    Write-Host
    Write-Host "  UTILITAIRES" -ForegroundColor Yellow
    Write-Host "  ----------"
    Write-Host "  A. Vérifier l'environnement"
    Write-Host "  0. Quitter"
    Write-Host
    
    $choice = Read-Host "Votre choix (0-9, A)"
    return $choice
}

function Show-ApiTestMenu {
    Clear-Host
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "   Test des endpoints API" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host
    Write-Host "  Choisissez l'environnement à tester:"
    Write-Host "  1. Environnement de développement (dev)"
    Write-Host "  2. Environnement de test (test)"
    Write-Host "  3. Environnement de production (prod)"
    Write-Host "  4. Tous les environnements"
    Write-Host "  0. Retour au menu principal"
    Write-Host
    
    $choice = Read-Host "Votre choix (0-4)"
    return $choice
}

# Détermine le répertoire du script et le répertoire racine du projet
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptPath

# Boucle principale du menu
while ($true) {
    $choice = Show-Menu
    
    switch ($choice) {
        "1" {
            Clear-Host
            Write-Host "Lancement de l'installation complète..." -ForegroundColor Green
            & "$projectRoot\scripts\setup\Install-Dependencies.ps1"
        }
        
        "2" {
            Clear-Host
            Write-Host "Ouverture du menu de configuration des environnements..." -ForegroundColor Green
            & "$projectRoot\scripts\Config-Menu.ps1"
        }
        
        "3" {
            Clear-Host
            Write-Host "Démarrage du serveur Mathakine..." -ForegroundColor Green
            & "$projectRoot\scripts\server\Start-MathTrainer.ps1"
        }
        
        "4" {
            Clear-Host
            Write-Host "Démarrage du serveur minimal..." -ForegroundColor Green
            & "$projectRoot\scripts\server\Run-MathTrainer.ps1" -Minimal
        }
        
        "5" {
            Clear-Host
            Write-Host "Démarrage du serveur amélioré..." -ForegroundColor Green
            & "$projectRoot\scripts\server\Run-MathTrainer.ps1" -Enhanced
        }
        
        "6" {
            Clear-Host
            Write-Host "Exécution de tous les tests..." -ForegroundColor Green
            & "$projectRoot\scripts\tests\Run-Tests.ps1"
        }
        
        "7" {
            Clear-Host
            Write-Host "Exécution des tests automatiques rapides..." -ForegroundColor Green
            & "$projectRoot\scripts\tests\Auto-Test.ps1"
        }
        
        "8" {
            Clear-Host
            Write-Host "Test du système d'environnement..." -ForegroundColor Green
            & "$projectRoot\scripts\tests\Test-EnvSystem.ps1"
        }
        
        "9" {
            $apiChoice = Show-ApiTestMenu
            
            switch ($apiChoice) {
                "1" {
                    Clear-Host
                    Write-Host "Test des endpoints API en environnement DEV..." -ForegroundColor Green
                    & "$projectRoot\scripts\tests\Test-ApiEndpoints.ps1" dev
                }
                "2" {
                    Clear-Host
                    Write-Host "Test des endpoints API en environnement TEST..." -ForegroundColor Green
                    & "$projectRoot\scripts\tests\Test-ApiEndpoints.ps1" test
                }
                "3" {
                    Clear-Host
                    Write-Host "Test des endpoints API en environnement PROD..." -ForegroundColor Green
                    & "$projectRoot\scripts\tests\Test-ApiEndpoints.ps1" prod
                }
                "4" {
                    Clear-Host
                    Write-Host "Test des endpoints API dans tous les environnements..." -ForegroundColor Green
                    & "$projectRoot\scripts\tests\Test-ApiEndpoints.ps1" all
                }
                "0" {
                    # Retour au menu principal, ne rien faire car la boucle continuera
                }
                default {
                    Write-Host "Choix invalide! Retour au menu principal." -ForegroundColor Red
                    Start-Sleep -Seconds 2
                }
            }
        }
        
        { $_ -eq "A" -or $_ -eq "a" } {
            Clear-Host
            Write-Host "Vérification de l'environnement..." -ForegroundColor Green
            & "$projectRoot\scripts\utils\Check-EnvVars.ps1"
        }
        
        "0" {
            Clear-Host
            Write-Host "Au revoir!" -ForegroundColor Green
            exit
        }
        
        default {
            Write-Host "Choix invalide! Veuillez réessayer." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
    
    # Pause après l'exécution de chaque option
    if ($choice -ne "0") {
        Write-Host
        Write-Host "Appuyez sur une touche pour revenir au menu principal..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} 