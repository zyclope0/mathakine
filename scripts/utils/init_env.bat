@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Script pour initialiser l'environnement Mathakine
REM ===================================================

REM Déterminer le répertoire racine du projet
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"

REM Créer le fichier .env avec les valeurs par défaut
echo MATH_TRAINER_PROFILE=dev> "%PROJECT_ROOT%.env"
echo MATH_TRAINER_PORT=8081>> "%PROJECT_ROOT%.env"
echo MATH_TRAINER_DEBUG=true>> "%PROJECT_ROOT%.env"

echo Environnement initialisé avec succès!
echo.
echo Configuration:
echo - Profil: dev
echo - Port: 8081
echo - Mode debug: true
echo.
echo Pour modifier ces valeurs, utilisez le script config_menu.bat

endlocal 