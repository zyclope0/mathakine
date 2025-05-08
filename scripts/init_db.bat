@echo off
REM Script d'initialisation de la base de données
echo ===================================================
echo =  INITIALISATION DE LA BASE DE DONNÉES  =
echo ===================================================
echo.

REM Vérification de Python
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
  echo Python n'est pas installé ou n'est pas dans le PATH.
  echo Veuillez installer Python 3.8 ou supérieur.
  echo.
  exit /b 1
)

for /f "tokens=2" %%I in ('python --version') do set PYTHON_VERSION=%%I
echo Version de Python détectée: %PYTHON_VERSION%
if "%PYTHON_VERSION:~0,4%" == "3.13" (
  echo Note: Python 3.13 est supporté avec les versions appropriées des dépendances.
  echo - SQLAlchemy 2.0.27+
  echo - pydantic 2.0.0+ avec pydantic-settings
  echo - FastAPI 0.100.0+
  echo.
)

REM Initialisation de la base de données
echo.
echo Initialisation de la base de données en cours...
python app/db/init_db.py
if %ERRORLEVEL% NEQ 0 (
  echo Erreur lors de l'initialisation de la base de données.
  exit /b 1
)

echo.
echo Base de données initialisée avec succès !
echo.

exit /b 0 