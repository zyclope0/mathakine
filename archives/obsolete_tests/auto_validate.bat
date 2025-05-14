@echo off
setlocal enabledelayedexpansion

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installé ou n'est pas dans le PATH
    exit /b 1
)

:: Vérifier les dépendances
echo Vérification des dépendances...
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo Installation de pytest...
    pip install pytest pytest-cov loguru
)

:: Exécuter la validation
echo Démarrage de la validation automatique...
python tests/auto_validation.py

:: Vérifier le résultat
if errorlevel 1 (
    echo.
    echo La validation a échoué. Consultez les logs dans test_results/
    exit /b 1
) else (
    echo.
    echo Validation réussie !
    exit /b 0
) 