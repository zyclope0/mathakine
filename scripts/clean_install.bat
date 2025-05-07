@echo off
echo === Math Trainer Backend - Nettoyage et reinstallation ===
echo.

REM Se placer dans le dossier du script
cd /d "%~dp0"
echo Repertoire actuel: %CD%
echo.

REM Supprimer l'environnement virtuel s'il existe
if exist venv (
    echo Suppression de l'environnement virtuel existant...
    rmdir /s /q venv
    echo Environnement virtuel supprime.
)

REM Desinstaller les packages existants
echo Desinstallation des packages existants...
pip uninstall -y fastapi uvicorn pydantic sqlalchemy
echo Packages desinstallés.

REM Creer un nouvel environnement virtuel
echo Creation d'un nouvel environnement virtuel...
python -m venv venv
echo Environnement virtuel cree.

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances avec les versions specifiques
echo Installation des dependances...
pip install -r requirements.txt

REM Créer le fichier .env si nécessaire
if not exist .env (
    echo Creation du fichier .env...
    if exist sample.env (
        copy sample.env .env >nul
        echo Fichier .env cree avec succes
    ) else (
        echo sample.env non trouve, creation d'un .env par defaut...
        echo # Configuration de base > .env
        echo DEBUG=True >> .env
        echo DATABASE_URL=sqlite:///./math_trainer.db >> .env
        echo Fichier .env cree avec succes
    )
)

echo.
echo Installation complete. Pour demarrer le serveur, executez:
echo start_server.bat
echo.

pause 