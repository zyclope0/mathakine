@echo off
echo Migration de SQLite vers PostgreSQL
echo ================================

REM Vérifier si Python est installé et la version
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8 à 3.11
    exit /b 1
)

REM Vérifier la version de Python
python -c "import sys; version=sys.version_info[:2]; is_compatible=(version[0]==3 and version[1]>=8 and version[1]<=11); print('Version Python %d.%d %s' % (version[0], version[1], 'compatible' if is_compatible else 'non supportée')); sys.exit(0 if is_compatible else 1)" >nul 2>nul
if %errorlevel% neq 0 (
    echo Version de Python non supportée. Veuillez utiliser Python 3.8 à 3.11
    echo Python 3.12+ n'est pas encore supporté par toutes les dépendances
    exit /b 1
)

REM Vérifier si l'environnement virtuel existe
if not exist venv (
    echo Création de l'environnement virtuel
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Installer les dépendances
echo Installation des dépendances...
pip install -r requirements.txt
pip install psycopg2-binary

REM Vérifier si le fichier .env existe
if not exist .env (
    echo Création du fichier .env avec les paramètres par défaut
    echo POSTGRES_USER=postgres> .env
    echo POSTGRES_PASSWORD=postgres>> .env
    echo POSTGRES_HOST=localhost>> .env
    echo POSTGRES_PORT=5432>> .env
    echo POSTGRES_DB=mathakine>> .env
    echo.
    echo Fichier .env créé. Veuillez modifier les paramètres selon votre configuration PostgreSQL.
    echo.
    pause
)

REM Exécuter le script de migration
echo Exécution de la migration...
python scripts/migrate_to_postgres.py

REM Désactiver l'environnement virtuel
call venv\Scripts\deactivate.bat

echo ================================
echo Migration terminée!
pause 