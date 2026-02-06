@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo    Mathakine Backend - Choix du serveur
echo ===================================================
echo.

REM Déterminer le répertoire racine du projet
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"
set "PORT_VALIDATOR=%PROJECT_ROOT%scripts\utils\validate_server_port.bat"
set "INIT_ENV=%PROJECT_ROOT%scripts\utils\init_env.bat"

REM Se placer dans le dossier racine du projet
cd /d "%PROJECT_ROOT%"
echo Repertoire actuel: %CD%
echo.

REM Vérifier si le fichier .env existe
if not exist "%PROJECT_ROOT%.env" (
    echo [INFO] Fichier .env non trouvé, initialisation de l'environnement...
    call "%INIT_ENV%"
)

REM Charger les variables d'environnement
call "%PROJECT_ROOT%scripts\utils\load_env.bat" dev
if %errorlevel% neq 0 (
    echo [ERREUR] Échec du chargement des variables d'environnement
    pause
    exit /b 1
)

REM Afficher la version de Python
python --version
echo.

echo Configuration actuelle:
echo - Profil: %MATH_TRAINER_PROFILE%
echo - Port: %MATH_TRAINER_PORT%
echo - Mode debug: %MATH_TRAINER_DEBUG%
echo.

REM Vérifier que les variables sont correctement définies
if not defined MATH_TRAINER_PROFILE (
    echo [ERREUR] Variable MATH_TRAINER_PROFILE non définie
    echo Réinitialisation du fichier .env recommandée:
    echo    scripts\utils\init_env.bat
    pause
    exit /b 1
)

if not defined MATH_TRAINER_PORT (
    echo [ERREUR] Variable MATH_TRAINER_PORT non définie
    echo Réinitialisation du fichier .env recommandée:
    echo    scripts\utils\init_env.bat
    pause
    exit /b 1
)

REM Vérifier la cohérence entre le profil et le port
echo Validation de la configuration des ports...
call "%PORT_VALIDATOR%" --check
if %errorlevel% neq 0 (
    echo.
    echo ATTENTION: La configuration des ports n'est pas cohérente avec le profil.
    
    set "fix_port="
    set /p fix_port=Souhaitez-vous corriger automatiquement? (O/N, défaut: O): 
    
    if not defined fix_port set "fix_port=O"
    if /i "%fix_port%"=="O" (
        call "%PORT_VALIDATOR%" --fix
        
        REM Recharger les variables d'environnement après la correction
        call "%PROJECT_ROOT%scripts\utils\load_env.bat"
        
        echo.
        echo Configuration mise à jour:
        echo - Profil: %MATH_TRAINER_PROFILE%
        echo - Port: %MATH_TRAINER_PORT%
        echo.
    )
)

echo Veuillez choisir l'option de serveur a demarrer:
echo.
echo 1 - Serveur minimal (simple API, sans interface graphique)
echo 2 - Serveur ameliore (avec interface graphique complete)
echo 3 - Configurer l'environnement avant demarrage
echo.

:choix_serveur
set "choix="
set /p choix=Entrez votre choix (1, 2 ou 3): 

if not defined choix goto choix_defaut

if "%choix%"=="1" (
    goto serveur_minimal
) else if "%choix%"=="2" (
    goto serveur_ameliore
) else if "%choix%"=="3" (
    goto configurer_env
) else (
    goto choix_defaut
)

:serveur_minimal
echo.
echo Demarrage du serveur minimal sur le port %MATH_TRAINER_PORT%...
echo.
python "%PROJECT_ROOT%minimal_server.py"
goto fin

:serveur_ameliore
echo.
echo Demarrage du serveur ameliore sur le port %MATH_TRAINER_PORT%...
echo.
python "%PROJECT_ROOT%enhanced_server.py"
goto fin

:configurer_env
echo.
echo Configuration de l'environnement...
echo.
call "%PROJECT_ROOT%scripts\config_menu.bat"

REM Recharger les variables après configuration
call "%PROJECT_ROOT%scripts\utils\load_env.bat"

REM Vérifier à nouveau la cohérence après configuration
call "%PORT_VALIDATOR%" --check --fix

echo.
set "restart="
set /p restart=Souhaitez-vous demarrer un serveur maintenant? (O/N): 

if not defined restart goto fin
if /i "%restart%"=="O" (
    cls
    echo ===================================================
    echo    Mathakine Backend - Choix du serveur
    echo ===================================================
    echo.
    echo Configuration actuelle:
    echo - Profil: %MATH_TRAINER_PROFILE%
    echo - Port: %MATH_TRAINER_PORT%
    echo - Mode debug: %MATH_TRAINER_DEBUG%
    echo.
    echo 1 - Serveur minimal (simple API)
    echo 2 - Serveur ameliore (interface graphique)
    echo.
    
    set "server_choice="
    set /p server_choice=Entrez votre choix (1 ou 2): 
    
    if not defined server_choice goto choix_defaut
    if "%server_choice%"=="1" (
        python "%PROJECT_ROOT%minimal_server.py"
    ) else (
        python "%PROJECT_ROOT%enhanced_server.py"
    )
)
goto fin

:choix_defaut
echo.
echo Choix invalide! Utilisation du serveur ameliore par defaut...
echo.
python "%PROJECT_ROOT%enhanced_server.py"

:fin
pause
endlocal 