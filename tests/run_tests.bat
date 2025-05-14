@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Vérifier si Python est installé
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH
    exit /b 1
)

:: Vérifier si les dépendances sont installées
echo Vérification des dépendances...
python -c "import pytest" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installation de pytest...
    pip install pytest pytest-cov
)

:: Définir les options par défaut
set TEST_TYPE=all

:: Parser les arguments
if "%~1"=="" goto :run_tests
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="--unit" set TEST_TYPE=unit & goto :run_tests
if /i "%~1"=="--api" set TEST_TYPE=api & goto :run_tests
if /i "%~1"=="--integration" set TEST_TYPE=integration & goto :run_tests
if /i "%~1"=="--functional" set TEST_TYPE=functional & goto :run_tests
if /i "%~1"=="--all" set TEST_TYPE=all & goto :run_tests
goto :show_help

:: Fonction pour afficher l'aide
:show_help
echo Usage: run_tests.bat [--unit ^| --api ^| --integration ^| --functional ^| --all]
echo.
echo Options:
echo   --unit         Exécuter uniquement les tests unitaires
echo   --api          Exécuter uniquement les tests API
echo   --integration  Exécuter uniquement les tests d'intégration
echo   --functional   Exécuter uniquement les tests fonctionnels
echo   --all          Exécuter tous les tests (par défaut)
echo   --help         Afficher cette aide
exit /b 0

:run_tests
echo.
echo === Script de test Mathakine - Compatible avec PowerShell et CMD ===
if "%TEST_TYPE%"=="all" (
    echo Exécution des tests all...
) else (
    echo Exécution des tests %TEST_TYPE%...
)
echo.

:: Exécuter le script Python de test
cd %~dp0
python run_tests.py --type %TEST_TYPE%

:: Vérifier le résultat
if %ERRORLEVEL% equ 0 (
    echo.
    echo Tests terminés avec succès
    echo Les résultats sont disponibles dans le dossier test_results/
) else (
    echo.
    echo Certains tests ont échoué.
    echo Consultez les logs dans le dossier test_results/ pour plus de détails.
)

exit /b %ERRORLEVEL% 