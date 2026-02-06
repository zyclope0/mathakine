@echo off
REM Script pour lancer le serveur en mode test avec les bonnes variables d'environnement

echo ========================================
echo DEMARRAGE SERVEUR EN MODE TEST
echo ========================================
echo.

REM Activer l'environnement virtuel si disponible
if exist ".venv\Scripts\Activate.bat" (
    echo Activation de l'environnement virtuel (.venv)...
    call .venv\Scripts\Activate.bat
) else if exist "venv\Scripts\Activate.bat" (
    echo Activation de l'environnement virtuel (venv)...
    call venv\Scripts\Activate.bat
) else (
    echo Aucun environnement virtuel trouve, utilisation de Python systeme
)

echo.

REM Configuration pour les tests
set MATH_TRAINER_DEBUG=true
set MATH_TRAINER_PROFILE=dev
set LOG_LEVEL=DEBUG

REM Securite - Mode developpement (relaxe pour les tests)
set REQUIRE_STRONG_DEFAULT_ADMIN=false
set RUN_STARTUP_MIGRATIONS=true

REM Base de donnees (utiliser la base de test si disponible)
if "%TEST_DATABASE_URL%"=="" (
    echo TEST_DATABASE_URL non defini, utilisation de DATABASE_URL
) else (
    echo Utilisation de TEST_DATABASE_URL pour les tests
)

echo.
echo Configuration:
echo   - DEBUG: %MATH_TRAINER_DEBUG%
echo   - RUN_STARTUP_MIGRATIONS: %RUN_STARTUP_MIGRATIONS%
echo   - REQUIRE_STRONG_DEFAULT_ADMIN: %REQUIRE_STRONG_DEFAULT_ADMIN%
echo.

REM Vérifier que les dépendances essentielles sont installées
python -c "import loguru, dotenv, uvicorn, starlette" 2>nul
if errorlevel 1 (
    echo Installation des dependances essentielles manquantes...
    pip install loguru python-dotenv uvicorn starlette fastapi
)

echo.
echo Demarrage du serveur...
echo.

python enhanced_server.py
