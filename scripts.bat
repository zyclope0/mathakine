@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Menu Principal de Mathakine - Accès à tous les scripts
REM ===================================================

:menu
cls
echo ===================================================
echo    Mathakine - Menu Principal
echo ===================================================
echo.
echo  INSTALLATION ET CONFIGURATION
echo  ----------------------------
echo  1. Installation complète et démarrage
echo  2. Configuration des environnements
echo.
echo  SERVEUR
echo  -------
echo  3. Démarrer le serveur Mathakine
echo  4. Démarrer le serveur minimal (API uniquement)
echo  5. Démarrer le serveur amélioré (Interface complète)
echo.
echo  TESTS
echo  -----
echo  6. Exécuter tous les tests
echo  7. Tests automatiques rapides
echo  8. Tester le système d'environnement
echo  9. Tester les endpoints API
echo.
echo  DÉPLOIEMENT ET GESTION
echo  ---------------------
echo  D. Déployer l'application (GitHub + hébergement)
echo  G. Gérer le dépôt Git (commit, push)
echo.
echo  DOCUMENTATION
echo  -------------
echo  M. Menu de gestion de la documentation
echo.
echo  UTILITAIRES
echo  ----------
echo  A. Vérifier l'environnement
echo  0. Quitter
echo.
set /p choix="Votre choix (0-9, A, D, G, M): "

if "%choix%"=="1" goto :install_and_run
if "%choix%"=="2" goto :config_env
if "%choix%"=="3" goto :start_server
if "%choix%"=="4" goto :start_minimal
if "%choix%"=="5" goto :start_enhanced
if "%choix%"=="6" goto :run_tests
if "%choix%"=="7" goto :auto_tests
if "%choix%"=="8" goto :test_env
if "%choix%"=="9" goto :test_api
if /i "%choix%"=="A" goto :check_env
if /i "%choix%"=="D" goto :deploy
if /i "%choix%"=="G" goto :git_manage
if /i "%choix%"=="M" goto :doc_menu
if "%choix%"=="0" goto :exit

echo.
echo Choix invalide! Veuillez réessayer.
timeout /t 2 >nul
goto :menu

:install_and_run
cls
echo Lancement de l'installation complète...
call scripts\setup\install_and_run.bat
goto :menu

:config_env
cls
echo Ouverture du menu de configuration des environnements...
call scripts\config_menu.bat
goto :menu

:start_server
cls
echo Démarrage du serveur Mathakine...
call scripts\server\start_math_trainer.bat
goto :menu

:start_minimal
cls
echo Démarrage du serveur minimal...
call scripts\server\run_minimal_server.bat
goto :menu

:start_enhanced
cls
echo Démarrage du serveur amélioré...
call scripts\server\run_enhanced_server.bat
goto :menu

:run_tests
cls
echo Exécution de tous les tests...
call scripts\tests\run_tests.bat
goto :menu

:auto_tests
cls
echo Exécution des tests automatiques rapides...
call scripts\tests\auto_test.bat
goto :menu

:test_env
cls
echo Test du système d'environnement...
call scripts\tests\test_env_system.bat
goto :menu

:test_api
cls
echo Test des endpoints API...
echo.
echo Choisissez l'environnement à tester:
echo  1. Environnement de développement (dev)
echo  2. Environnement de test (test)
echo  3. Environnement de production (prod)
echo  4. Tous les environnements
echo  0. Retour au menu principal
echo.
set /p env_choice="Votre choix (0-4): "

if "%env_choice%"=="1" (
    echo.
    echo Test des endpoints API en environnement DEV...
    call scripts\tests\test_api_endpoints.bat dev
    pause
) else if "%env_choice%"=="2" (
    echo.
    echo Test des endpoints API en environnement TEST...
    call scripts\tests\test_api_endpoints.bat test
    pause
) else if "%env_choice%"=="3" (
    echo.
    echo Test des endpoints API en environnement PROD...
    call scripts\tests\test_api_endpoints.bat prod
    pause
) else if "%env_choice%"=="4" (
    echo.
    echo Test des endpoints API dans tous les environnements...
    call scripts\tests\test_api_endpoints.bat all
    pause
) else if "%env_choice%"=="0" (
    goto :menu
) else (
    echo.
    echo Choix invalide! Retour au menu principal.
    timeout /t 2 >nul
)
goto :menu

:check_env
cls
echo Vérification de l'environnement...
call scripts\check_environment.bat
goto :menu

:deploy
cls
echo Déploiement de l'application Mathakine...
call scripts\deploy.bat
goto :menu

:git_manage
cls
echo Gestion du dépôt Git...
echo.
echo Choisissez une option:
echo  1. Vérifier les changements (git status)
echo  2. Créer un commit et pousser les changements
echo  3. Afficher l'historique des commits
echo  0. Retour au menu principal
echo.
set /p git_choice="Votre choix (0-3): "

if "%git_choice%"=="1" (
    echo.
    echo Vérification des changements...
    cd "%~dp0"
    git status
    pause
) else if "%git_choice%"=="2" (
    echo.
    echo Création d'un commit et push...
    cd "%~dp0"
    git add .
    set /p commit_msg="Message de commit: "
    git commit -m "%commit_msg%"
    git push
    echo.
    echo Opération terminée!
    pause
) else if "%git_choice%"=="3" (
    echo.
    echo Affichage de l'historique des commits...
    cd "%~dp0"
    git log --oneline -n 10
    pause
) else if "%git_choice%"=="0" (
    goto :menu
) else (
    echo.
    echo Choix invalide! Retour au menu principal.
    timeout /t 2 >nul
)
goto :menu

:doc_menu
cls
echo Lancement du menu de gestion de la documentation...
call scripts\doc_menu.bat
goto :menu

:exit
cls
echo Au revoir!
exit /b 0 