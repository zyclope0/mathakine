@echo off
echo ===================================================
echo    Math Trainer Backend - Installation et Demarrage
echo ===================================================
echo.

REM Se placer dans le dossier du projet principal
cd /d "%~dp0"
cd ..\..
echo Repertoire actuel: %CD%
echo.

REM Verifier si Python est installe
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.8+ depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher l'option "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

REM Afficher la version de Python
python --version
echo.

echo ===== INSTALLATION DES DEPENDANCES =====

REM Verifier si requirements.txt existe
if not exist requirements.txt (
    echo [ERREUR] Le fichier requirements.txt est manquant.
    pause
    exit /b 1
)

REM Installation des dependances
echo Installation des dependances...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] L'installation des dependances a echoue.
    pause
    exit /b 1
)
echo [OK] Dependances installees avec succes.
echo.

REM Choisir un profil d'environnement
echo ===== CONFIGURATION DE L'ENVIRONNEMENT =====
echo Choisissez un profil d'environnement:
echo.
echo 1 - DEV (Developpement - debug actif, port 8081)
echo 2 - TEST (Tests et validation - debug actif, port 8082)
echo 3 - PROD (Production - optimise, port 8080)
echo.
set /p profile_choice="Votre choix (1-3, defaut: 1): "

set "profile=dev"
if "%profile_choice%"=="2" set "profile=test"
if "%profile_choice%"=="3" set "profile=prod"

REM Configurer l'environnement
echo.
echo Configuration du profil %profile%...
call scripts\utils\env_manager.bat --profile %profile% --export
echo [OK] Configuration creee.
echo.

REM Configurer la clé API OpenAI si demandé
echo Souhaitez-vous configurer une cle API OpenAI pour les fonctionnalites IA?
echo (Necessite un compte sur https://platform.openai.com)
set /p api_choice="Configurer la cle API maintenant? (O/N, defaut: N): "

if /i "%api_choice%"=="O" (
    echo.
    echo Entrez votre cle API OpenAI:
    set /p api_key="OPENAI_API_KEY: "
    if not "%api_key%"=="" (
        call scripts\utils\env_manager.bat --key OPENAI_API_KEY --value %api_key% --export
        echo [OK] Cle API configuree.
    )
    echo.
)

REM Executer les tests de base
echo ===== VERIFICATION DE L'INSTALLATION =====
echo Execution des tests rapides...
call scripts\tests\auto_test.bat
echo.

REM Charger les variables d'environnement pour le démarrage du serveur
call scripts\utils\load_env.bat %profile%

echo ===== DEMARRAGE DE L'APPLICATION =====
echo.
echo Veuillez choisir une option:
echo.
echo 1 - Demarrer le serveur avance (interface graphique complete)
echo 2 - Demarrer le serveur minimal (API uniquement)
echo 3 - Ouvrir le menu de configuration des environnements
echo 4 - Quitter sans demarrer de serveur
echo.
set /p choix="Votre choix (1-4): "

if "%choix%"=="1" (
    echo.
    echo Demarrage du serveur avance sur le port %MATH_TRAINER_PORT%...
    echo Mode debug: %MATH_TRAINER_DEBUG%
    echo.
    python enhanced_server.py
) else if "%choix%"=="2" (
    echo.
    echo Demarrage du serveur minimal sur le port %MATH_TRAINER_PORT%...
    echo Mode debug: %MATH_TRAINER_DEBUG%
    echo.
    python minimal_server.py
) else if "%choix%"=="3" (
    echo.
    echo Ouverture du menu de configuration...
    call scripts\config_menu.bat
) else (
    echo.
    echo Installation terminee sans demarrer de serveur.
    echo.
    echo Pour demarrer plus tard:
    echo - Menu principal: scripts.bat
    echo - Demarrage rapide: scripts\server\start_math_trainer.bat
    echo - Configuration: scripts\config_menu.bat
    echo.
)

pause 