@echo off
echo Optimisation de la base de données PostgreSQL
echo ================================

REM Vérifier si Python est installé
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH
    exit /b 1
)

REM Vérifier si l'environnement virtuel existe
if not exist venv (
    echo Création de l'environnement virtuel
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
pip install psycopg2-binary dotenv loguru

REM Vérifier si le fichier .env existe avec les informations PostgreSQL
if not exist .env (
    echo ERREUR: Fichier .env non trouvé!
    echo Veuillez créer un fichier .env avec les informations de connexion PostgreSQL:
    echo   POSTGRES_USER=postgres
    echo   POSTGRES_PASSWORD=votre_mot_de_passe
    echo   POSTGRES_HOST=localhost
    echo   POSTGRES_PORT=5432
    echo   POSTGRES_DB=mathakine
    exit /b 1
)

REM Exécuter le script d'optimisation
echo Exécution du script d'optimisation PostgreSQL...
python scripts/optimize_postgres.py

REM Vérifier le code de retour
if %errorlevel% neq 0 (
    echo ERREUR: L'optimisation a échoué avec le code %errorlevel%
    exit /b %errorlevel%
)

REM Désactiver l'environnement virtuel
call venv\Scripts\deactivate.bat

echo ================================
echo Optimisation terminée avec succès!
echo.
echo Pour plus d'informations sur PostgreSQL, consultez:
echo docs\POSTGRESQL_MIGRATION.md
echo.
pause 