@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Menu de Configuration des Environnements Mathakine
REM ===================================================

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers le gestionnaire d'environnement
set "ENV_MANAGER=%~dp0utils\env_manager.bat"

REM Chemin vers le fichier .env
set "ENV_FILE=%~dp0..\.env"

:menu
cls
echo ===================================================
echo    Mathakine - Menu de Configuration
echo ===================================================
echo.
echo  1. Afficher la configuration actuelle
echo  2. Utiliser le profil DEV (développement)
echo  3. Utiliser le profil TEST
echo  4. Utiliser le profil PROD (production)
echo  5. Modifier une variable d'environnement
echo  6. Ouvrir le fichier .env dans un éditeur
echo  7. Créer ou réinitialiser le fichier .env
echo  8. Configurer la clé API OpenAI
echo  9. Créer le fichier .env.example (modèle)
echo  R. Réparer la configuration (reset complet)
echo  0. Retour au menu principal
echo.
set /p choix="Votre choix (0-9, R): "

if "%choix%"=="1" goto :show_config
if "%choix%"=="2" goto :set_dev
if "%choix%"=="3" goto :set_test
if "%choix%"=="4" goto :set_prod
if "%choix%"=="5" goto :edit_var
if "%choix%"=="6" goto :open_env
if "%choix%"=="7" goto :reset_env
if "%choix%"=="8" goto :set_api_key
if "%choix%"=="9" goto :create_env_example
if /i "%choix%"=="R" goto :repair_config
if "%choix%"=="0" (
    REM Retourner au menu principal
    exit /b 0
)

echo.
echo Choix invalide! Veuillez réessayer.
timeout /t 2 >nul
goto :menu

:show_config
cls
echo ===================================================
echo    Configuration Actuelle
echo ===================================================
echo.

REM Vérifier si le fichier .env existe
if not exist "%ENV_FILE%" (
    echo Le fichier .env n'existe pas encore.
    echo.
    echo Création d'un fichier .env par défaut (profil DEV)...
    call "%ENV_MANAGER%" --profile dev --export
    timeout /t 2 >nul
)

REM Afficher la configuration actuelle
call "%ENV_MANAGER%" --list

echo.
pause
goto :menu

:set_dev
cls
echo ===================================================
echo    Application du profil DEV
echo ===================================================
echo.
call "%ENV_MANAGER%" --profile dev --export
echo.
echo Le profil DEV a été appliqué avec succès.
echo.
pause
goto :menu

:set_test
cls
echo ===================================================
echo    Application du profil TEST
echo ===================================================
echo.
call "%ENV_MANAGER%" --profile test --export
echo.
echo Le profil TEST a été appliqué avec succès.
echo.
pause
goto :menu

:set_prod
cls
echo ===================================================
echo    Application du profil PROD
echo ===================================================
echo.
call "%ENV_MANAGER%" --profile prod --export
echo.
echo Le profil PROD a été appliqué avec succès.
echo.
pause
goto :menu

:edit_var
cls
echo ===================================================
echo    Modification d'une variable d'environnement
echo ===================================================
echo.
echo Variables disponibles :
echo.
echo  - MATH_TRAINER_DEBUG (true/false)
echo  - MATH_TRAINER_PORT (numéro de port)
echo  - MATH_TRAINER_LOG_LEVEL (DEBUG/INFO/WARNING/ERROR)
echo  - MATH_TRAINER_TEST_MODE (true/false)
echo  - OPENAI_API_KEY (clé API)
echo  - MATH_TRAINER_PROFILE (nom du profil)
echo.
set /p var_name="Nom de la variable à modifier : "
set /p var_value="Nouvelle valeur : "

if "%var_name%"=="" (
    echo Nom de variable invalide.
    timeout /t 2 >nul
    goto :edit_var
)

REM Mettre à jour la variable
call "%ENV_MANAGER%" --key %var_name% --value %var_value% --export

echo.
echo Variable %var_name% mise à jour avec la valeur %var_value%
echo.
pause
goto :menu

:open_env
cls
echo ===================================================
echo    Ouverture du fichier .env
echo ===================================================
echo.

REM Vérifier si le fichier .env existe
if not exist "%ENV_FILE%" (
    echo Le fichier .env n'existe pas encore.
    echo.
    echo Création d'un fichier .env par défaut (profil DEV)...
    call "%ENV_MANAGER%" --profile dev --export
    timeout /t 2 >nul
)

REM Ouvrir le fichier dans Notepad
echo Ouverture du fichier %ENV_FILE%...
start notepad "%ENV_FILE%"
echo.
pause
goto :menu

:reset_env
cls
echo ===================================================
echo    Réinitialisation du fichier .env
echo ===================================================
echo.
echo Cette action va réinitialiser toutes vos configurations.
echo.
set /p confirm="Êtes-vous sûr de vouloir continuer ? (O/N) : "

if /i "%confirm%"=="O" (
    echo.
    echo Choisissez le profil pour le nouveau fichier .env :
    echo.
    echo  1. DEV (développement)
    echo  2. TEST
    echo  3. PROD (production)
    echo.
    set /p profile_choice="Votre choix (1-3) : "
    
    set "profile=dev"
    if "%profile_choice%"=="2" set "profile=test"
    if "%profile_choice%"=="3" set "profile=prod"
    
    REM Supprimer le fichier existant s'il y en a un
    if exist "%ENV_FILE%" del "%ENV_FILE%" 
    
    REM Créer un nouveau fichier
    call "%ENV_MANAGER%" --profile %profile% --export
    
    echo.
    echo Fichier .env réinitialisé avec le profil %profile%.
)
echo.
pause
goto :menu

:set_api_key
cls
echo ===================================================
echo    Configuration de la clé API OpenAI
echo ===================================================
echo.
echo Entrez votre clé API OpenAI pour activer les fonctionnalités d'IA.
echo (Vous pouvez obtenir une clé sur https://platform.openai.com)
echo.
echo Pour annuler, laissez le champ vide et appuyez sur Entrée.
echo.
set /p api_key="Clé API OpenAI : "

if not "%api_key%"=="" (
    REM Mettre à jour la clé API
    call "%ENV_MANAGER%" --key OPENAI_API_KEY --value %api_key% --export
    
    echo.
    echo Clé API OpenAI configurée avec succès.
) else (
    echo.
    echo Configuration annulée.
)
echo.
pause
goto :menu

:create_env_example
cls
echo ===================================================
echo    Création du fichier .env.example (modèle)
echo ===================================================
echo.
echo Cette action va créer un fichier modèle .env.example
echo à la racine du projet pour aider les nouveaux développeurs.
echo.

call "%~dp0utils\create_env_example.bat"

echo.
pause
goto :menu

:repair_config
cls
echo ===================================================
echo    Réparation complète du fichier .env
echo ===================================================
echo.
echo Cette action va effectuer une remise à zéro complète de votre configuration.
echo Utilisez cette option seulement si vous rencontrez des problèmes persistants.
echo.
call "%~dp0utils\reset_env.bat"
echo.
pause
goto :menu

:end
exit /b 0 