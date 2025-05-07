@echo off
setlocal enabledelayedexpansion

REM ====================================================
REM Script d'installation pour Math Trainer
REM Installe les dépendances et configure l'environnement
REM ====================================================

echo ===================================================
echo    Math Trainer Backend - Installation
echo ===================================================
echo.

REM Déterminer le répertoire racine du projet
set "PROJECT_ROOT=%~dp0"
set "SETUP_BATCH=%PROJECT_ROOT%scripts\setup\install_and_run.bat"
set "SETUP_PS1=%PROJECT_ROOT%scripts\setup\Install-Dependencies.ps1"

REM Détecter si l'exécution est dans PowerShell
set "IS_POWERSHELL="
for /f "tokens=*" %%a in ('echo %PSModulePath%') do (
    if not "%%a"=="" set "IS_POWERSHELL=1"
)

if defined IS_POWERSHELL (
    echo Environnement PowerShell détecté.
    echo Lancement du script PowerShell d'installation...
    echo.
    
    REM Vérifier que PowerShell est disponible
    where powershell >nul 2>&1
    if %errorlevel% equ 0 (
        powershell -ExecutionPolicy Bypass -File "%SETUP_PS1%"
    ) else (
        echo ERREUR: PowerShell n'est pas disponible dans le chemin.
        echo Utilisation du script batch à la place.
        if exist "%SETUP_BATCH%" (
            call "%SETUP_BATCH%"
        ) else (
            echo ERREUR: Script batch introuvable: %SETUP_BATCH%
            echo.
            echo Appuyez sur une touche pour quitter...
            pause > nul
            exit /b 1
        )
    )
) else (
    echo Environnement CMD détecté.
    echo Lancement du script batch d'installation...
    echo.
    
    if exist "%SETUP_BATCH%" (
        call "%SETUP_BATCH%"
    ) else (
        echo ERREUR: Script batch introuvable: %SETUP_BATCH%
        echo.
        echo Appuyez sur une touche pour quitter...
        pause > nul
        exit /b 1
    )
)

REM Installation réussie, afficher les instructions de démarrage
echo.
echo ===================================================
echo    Installation terminée
echo ===================================================
echo.
echo Pour démarrer Math Trainer:
echo  - Exécutez run_server.bat à la racine du projet
echo.
echo Pour plus d'informations, consultez GETTING_STARTED.md
echo.
pause

endlocal 