@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Script de chargement des variables d'environnement
REM ===================================================

REM Ce script permet aux autres scripts de charger facilement
REM les variables d'environnement à partir du fichier .env

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers le fichier env_manager.bat
set "ENV_MANAGER=%~dp0env_manager.bat"

REM Profil par défaut (peut être surchargé via param)
set "PROFILE=%~1"
if "%PROFILE%"=="" set "PROFILE=dev"

REM Vérifier l'existence du script env_manager.bat
if not exist "%ENV_MANAGER%" (
    echo [ERREUR] Fichier env_manager.bat introuvable: %ENV_MANAGER%
    exit /b 1
)

REM Chemin vers le fichier .env (racine du projet)
set "ENV_FILE=%~dp0..\..\\.env"

REM Créer le fichier .env s'il n'existe pas
if not exist "%ENV_FILE%" (
    call "%ENV_MANAGER%" --profile %PROFILE% --export
    if not %ERRORLEVEL%==0 (
        echo [ERREUR] Échec de création du fichier .env
        exit /b 1
    )
)

REM Définir les variables par défaut
set "MATH_TRAINER_DEBUG=true"
set "MATH_TRAINER_PORT=8081"
set "MATH_TRAINER_LOG_LEVEL=DEBUG"
set "MATH_TRAINER_TEST_MODE=true"
set "MATH_TRAINER_PROFILE=dev"

REM Lire le fichier .env ligne par ligne
for /f "usebackq tokens=*" %%a in ("%ENV_FILE%") do (
    set "line=%%a"
    if "!line:~0,1!" neq "#" (
        if "!line!" neq "" (
            for /f "tokens=1,* delims==" %%b in ("!line!") do (
                if "%%b" neq "" if "%%c" neq "" (
                    set "%%b=%%c"
                )
            )
        )
    )
)

REM Exporter les variables vers le script appelant
endlocal & (
    set "MATH_TRAINER_DEBUG=%MATH_TRAINER_DEBUG%"
    set "MATH_TRAINER_PORT=%MATH_TRAINER_PORT%"
    set "MATH_TRAINER_LOG_LEVEL=%MATH_TRAINER_LOG_LEVEL%"
    set "MATH_TRAINER_TEST_MODE=%MATH_TRAINER_TEST_MODE%"
    set "MATH_TRAINER_PROFILE=%MATH_TRAINER_PROFILE%"
    if defined OPENAI_API_KEY set "OPENAI_API_KEY=%OPENAI_API_KEY%"
)

exit /b 0 