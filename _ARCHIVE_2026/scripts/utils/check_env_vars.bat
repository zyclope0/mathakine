@echo off
setlocal enabledelayedexpansion

REM =======================================================
REM Script pour vérifier la validité des variables d'environnement
REM Ce script détecte les problèmes potentiels dans la configuration
REM =======================================================

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Variables
set "PROJECT_ROOT=%~dp0..\.."
set "ENV_FILE=%PROJECT_ROOT%\.env"
set "VERBOSE="
set "RETURN_CODE=0"

REM Analyse des arguments
:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="--env-file" (
    set "ENV_FILE=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--verbose" (
    set "VERBOSE=--verbose"
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo =======================================================
echo    Vérification des variables d'environnement
echo =======================================================
echo.
echo Options:
echo   --env-file FICHIER    Spécifier un fichier .env à valider
echo   --verbose             Afficher plus de détails
echo   --help                Afficher cette aide
echo.
exit /b 0

:main
echo =======================================================
echo    Vérification des variables d'environnement
echo =======================================================
echo.

REM Vérifier si Python est disponible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas disponible. Veuillez l'installer.
    exit /b 1
)

REM Vérifier si le fichier .env existe
if not exist "%ENV_FILE%" (
    echo [ATTENTION] Le fichier %ENV_FILE% n'existe pas.
    echo Utilisation des variables d'environnement système.
    
    REM Valider les variables d'environnement système
    python validate_env.py %VERBOSE%
    set RETURN_CODE=%errorlevel%
) else (
    echo Validation du fichier %ENV_FILE%...
    
    REM Valider le fichier .env
    python validate_env.py --env-file "%ENV_FILE%" %VERBOSE%
    set RETURN_CODE=%errorlevel%
    
    if %RETURN_CODE% neq 0 (
        echo.
        echo [ATTENTION] Des problèmes ont été détectés dans votre configuration.
        echo Vous pouvez corriger manuellement le fichier %ENV_FILE%
        echo ou utiliser les scripts de configuration:
        echo.
        echo scripts\config_menu.bat          # Menu interactif de configuration
        echo scripts\utils\env_manager.bat    # Gestion en ligne de commande
    ) else (
        echo.
        echo [OK] La configuration est valide.
    )
)

exit /b %RETURN_CODE% 