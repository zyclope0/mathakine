@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Script de réinitialisation du fichier .env
REM ===================================================

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers la racine du projet
set "PROJECT_ROOT=%~dp0..\.."

REM Chemin vers le fichier .env
set "ENV_FILE=%PROJECT_ROOT%\.env"

REM Demander confirmation à l'utilisateur
echo ===================================================
echo    Mathakine - Réinitialisation du fichier .env
echo ===================================================
echo.
echo Ce script va supprimer votre fichier .env actuel et
echo créer un nouveau fichier avec les paramètres par défaut.
echo.
set /p confirm="Êtes-vous sûr de vouloir continuer ? (O/N) : "

if /i not "%confirm%"=="O" (
    echo Opération annulée.
    goto :end
)

REM Supprimer le fichier .env existant s'il existe
if exist "%ENV_FILE%" (
    del "%ENV_FILE%"
    echo Fichier .env supprimé.
)

REM Demander quel profil utiliser
echo.
echo Choisissez le profil pour le nouveau fichier .env :
echo  1. DEV (développement) - Port 8081
echo  2. TEST - Port 8082
echo  3. PROD (production) - Port 8080
echo.
set /p profile_choice="Votre choix (1-3, défaut=1) : "

REM Définir le profil en fonction du choix
set "profile=dev"
set "port=8081"
set "debug=true"
set "log_level=DEBUG"
set "test_mode=true"

if "%profile_choice%"=="2" (
    set "profile=test"
    set "port=8082"
    set "log_level=INFO"
) else if "%profile_choice%"=="3" (
    set "profile=prod"
    set "port=8080"
    set "debug=false"
    set "log_level=WARNING"
    set "test_mode=false"
)

REM Créer le nouveau fichier .env
echo # Fichier d'environnement Math Trainer> "%ENV_FILE%"
echo # Généré le %date% %time%>> "%ENV_FILE%"
echo.>> "%ENV_FILE%"
echo DATABASE_URL=sqlite:///./math_trainer.db>> "%ENV_FILE%"
echo MATH_TRAINER_DEBUG=%debug%>> "%ENV_FILE%"
echo MATH_TRAINER_LOG_LEVEL=%log_level%>> "%ENV_FILE%"
echo MATH_TRAINER_PORT=%port%>> "%ENV_FILE%"
echo MATH_TRAINER_PROFILE=%profile%>> "%ENV_FILE%"
echo MATH_TRAINER_TEST_MODE=%test_mode%>> "%ENV_FILE%"

echo.
echo Fichier .env créé avec succès avec le profil %profile%.
echo.
echo Configuration :
echo  - Profil: %profile%
echo  - Port: %port%
echo  - Debug: %debug%
echo  - Log Level: %log_level%
echo  - Test Mode: %test_mode%

:end
echo.
pause 