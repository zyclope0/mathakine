@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Script pour valider que le port du serveur correspond à l'environnement 
REM ===================================================

REM Variables
set "PROJECT_ROOT=%~dp0..\..\"
set "ENV_MANAGER=%PROJECT_ROOT%scripts\utils\env_manager.bat"
set "RESULTS_DIR=%PROJECT_ROOT%test_results"

REM Arguments
set "CHECK_ONLY=false"
set "FIX_ISSUES=false"
set "VERBOSE=false"

REM Analyse des arguments
:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="--check" (
    set "CHECK_ONLY=true"
    shift
    goto :parse_args
)
if /i "%~1"=="--fix" (
    set "FIX_ISSUES=true"
    shift
    goto :parse_args
)
if /i "%~1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo ===================================================
echo    Validation du port serveur Math Trainer
echo ===================================================
echo.
echo Ce script vérifie que le port configuré dans l'environnement correspond
echo au port utilisé par le serveur en cours d'exécution.
echo.
echo Options:
echo   --check       Vérifier sans modifier (par défaut)
echo   --fix         Modifier le fichier .env pour corriger le port
echo   --verbose     Afficher plus d'informations
echo   --help        Afficher cette aide
echo.
exit /b 0

:main
echo ===================================================
echo    Validation du port serveur Math Trainer
echo ===================================================
echo.

REM Créer le répertoire de résultats si nécessaire
if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"

REM Définir les ports attendus pour chaque environnement
set "PORT_DEV=8081"
set "PORT_TEST=8082"
set "PORT_PROD=8080"

REM Récupérer le profil actuel
for /f "tokens=1,* delims==" %%a in ('type "%PROJECT_ROOT%.env" ^| findstr "MATH_TRAINER_PROFILE"') do (
    set "CURRENT_PROFILE=%%b"
)

REM Nettoyer les caractères potentiellement problématiques du profil
set "CURRENT_PROFILE=!CURRENT_PROFILE: =!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:"=!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:,=!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:;=!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:'=!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:.=!"
set "CURRENT_PROFILE=!CURRENT_PROFILE:-=!"

REM Si le profile est toujours vide ou malformé, utiliser le profil par défaut
if "!CURRENT_PROFILE!"=="" (
    echo [AVERTISSEMENT] Profil non défini, utilisation du profil par défaut: dev
    set "CURRENT_PROFILE=dev"
)

REM Récupérer le port configuré
for /f "tokens=1,* delims==" %%a in ('type "%PROJECT_ROOT%.env" ^| findstr "MATH_TRAINER_PORT"') do (
    set "CONFIGURED_PORT=%%b"
)

REM Nettoyer le port configuré
set "CONFIGURED_PORT=!CONFIGURED_PORT: =!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:"=!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:,=!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:;=!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:'=!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:.=!"
set "CONFIGURED_PORT=!CONFIGURED_PORT:-=!"

REM Déterminer le port attendu en fonction du profil
set "EXPECTED_PORT=0"
if /i "!CURRENT_PROFILE!"=="dev" (
    set "EXPECTED_PORT=%PORT_DEV%"
) else if /i "!CURRENT_PROFILE!"=="test" (
    set "EXPECTED_PORT=%PORT_TEST%"
) else if /i "!CURRENT_PROFILE!"=="prod" (
    set "EXPECTED_PORT=%PORT_PROD%"
) else (
    echo [AVERTISSEMENT] Profil '!CURRENT_PROFILE!' non reconnu ou invalide
    echo Tentative de faire correspondre à un profil valide...
    
    REM Essayer de reconnaître le profil par correspondance partielle
    if /i "!CURRENT_PROFILE:dev=!" neq "!CURRENT_PROFILE!" (
        echo [INFO] Profil interprété comme 'dev'
        set "CURRENT_PROFILE=dev"
        set "EXPECTED_PORT=%PORT_DEV%"
    ) else if /i "!CURRENT_PROFILE:test=!" neq "!CURRENT_PROFILE!" (
        echo [INFO] Profil interprété comme 'test'
        set "CURRENT_PROFILE=test"
        set "EXPECTED_PORT=%PORT_TEST%"
    ) else if /i "!CURRENT_PROFILE:prod=!" neq "!CURRENT_PROFILE!" (
        echo [INFO] Profil interprété comme 'prod'
        set "CURRENT_PROFILE=prod"
        set "EXPECTED_PORT=%PORT_PROD%"
    ) else (
        echo [AVERTISSEMENT] Impossible de déterminer le profil, utilisation du profil par défaut: dev
        set "CURRENT_PROFILE=dev"
        set "EXPECTED_PORT=%PORT_DEV%"
    )
)

echo Profil actuel: !CURRENT_PROFILE!
echo Port configuré: !CONFIGURED_PORT!
echo Port attendu: !EXPECTED_PORT!
echo.

REM Vérifier si le serveur est en cours d'exécution
echo Vérification du serveur en cours d'exécution...
set "SERVER_RUNNING=false"
set "ACTIVE_PORT=0"

REM Tester les ports possibles
for %%p in (%PORT_DEV% %PORT_TEST% %PORT_PROD%) do (
    if "!VERBOSE!"=="true" echo Vérification du port %%p...
    curl -s http://localhost:%%p/status -o "%RESULTS_DIR%\port_check.json" >nul 2>&1
    if !errorlevel! equ 0 (
        set "SERVER_RUNNING=true"
        set "ACTIVE_PORT=%%p"
        if "!VERBOSE!"=="true" echo Serveur trouvé sur le port %%p
    )
)

if "!SERVER_RUNNING!"=="false" (
    echo [INFO] Aucun serveur en cours d'exécution.
    echo.
    
    REM Vérifier si la configuration est cohérente avec le profil
    if "!CONFIGURED_PORT!"=="!EXPECTED_PORT!" (
        echo [OK] Le port configuré (!CONFIGURED_PORT!) correspond au profil (!CURRENT_PROFILE!).
        exit /b 0
    ) else (
        echo [AVERTISSEMENT] Le port configuré (!CONFIGURED_PORT!) ne correspond pas au profil (!CURRENT_PROFILE!).
        
        if "!FIX_ISSUES!"=="true" (
            echo Correction du port...
            echo MATH_TRAINER_PORT=!EXPECTED_PORT!> "%PROJECT_ROOT%.env.tmp"
            type "%PROJECT_ROOT%.env" | findstr /v "MATH_TRAINER_PORT" >> "%PROJECT_ROOT%.env.tmp"
            move /y "%PROJECT_ROOT%.env.tmp" "%PROJECT_ROOT%.env" >nul
            echo [OK] Port corrigé dans le fichier .env.
        ) else (
            echo Pour corriger, utilisez l'option --fix.
        )
        exit /b 1
    )
) else (
    echo Serveur en cours d'exécution sur le port !ACTIVE_PORT!
    
    REM Récupérer le profil du serveur actif
    curl -s http://localhost:!ACTIVE_PORT!/status > "%RESULTS_DIR%\active_profile.json"
    for /f "tokens=1,* delims=:" %%a in ('type "%RESULTS_DIR%\active_profile.json" ^| findstr "profile"') do (
        set "ACTIVE_PROFILE=%%b"
    )
    set "ACTIVE_PROFILE=!ACTIVE_PROFILE: =!"
    set "ACTIVE_PROFILE=!ACTIVE_PROFILE:,=!"
    set "ACTIVE_PROFILE=!ACTIVE_PROFILE:"=!"
    
    echo Profil du serveur actif: !ACTIVE_PROFILE!
    echo.
    
    REM Vérifier si le port actif correspond au profil actif
    if "!ACTIVE_PORT!"=="!EXPECTED_PORT!" (
        echo [OK] Le serveur utilise le port correct pour le profil !CURRENT_PROFILE!.
    ) else (
        echo [AVERTISSEMENT] Le serveur utilise un port (!ACTIVE_PORT!) qui ne correspond pas au profil actuel (!CURRENT_PROFILE!).
        echo Le port attendu pour le profil !CURRENT_PROFILE! est !EXPECTED_PORT!.
        echo.
        
        if "!ACTIVE_PROFILE!"=="!CURRENT_PROFILE!" (
            echo [AVERTISSEMENT] Le serveur utilise le bon profil mais le mauvais port.
            
            if "!FIX_ISSUES!"=="true" (
                echo Pour corriger ce problème, veuillez redémarrer le serveur.
            ) else (
                echo Pour résoudre ce problème, redémarrez le serveur.
            )
        ) else (
            echo [AVERTISSEMENT] Le serveur utilise un profil différent (!ACTIVE_PROFILE!) du profil actuel (!CURRENT_PROFILE!).
            
            if "!FIX_ISSUES!"=="true" (
                echo Pour corriger ce problème, veuillez redémarrer le serveur avec le bon profil.
            ) else (
                echo Pour résoudre ce problème, redémarrez le serveur avec le bon profil.
            )
        )
        exit /b 1
    )
)

exit /b 0 