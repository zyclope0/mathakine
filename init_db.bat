@echo off
echo Initialisation de la base de données Mathakine
echo ===========================================

REM Vérifier si Python est installé
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8 ou supérieur
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

REM Exécuter le script d'initialisation de la base de données
echo Initialisation de la base de données...
python scripts/create_database.py

REM Désactiver l'environnement virtuel
call venv\Scripts\deactivate.bat

echo ===========================================
echo Base de données initialisée avec succès!
echo Vous pouvez maintenant lancer le serveur avec run_server.bat
pause 