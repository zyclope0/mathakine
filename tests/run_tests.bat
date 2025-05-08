@echo off
setlocal enabledelayedexpansion

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

:: Parser les arguments
set TEST_TYPE=all
if "%~1"=="" goto :run_tests
if "%~1"=="--help" goto :show_help
if "%~1"=="--unit" set TEST_TYPE=unit
if "%~1"=="--api" set TEST_TYPE=api
if "%~1"=="--integration" set TEST_TYPE=integration
if "%~1"=="--functional" set TEST_TYPE=functional
if "%~1"=="--all" set TEST_TYPE=all

:run_tests
echo Exécution des tests %TEST_TYPE%...
python run_tests.py --type %TEST_TYPE%

:: Vérifier le résultat
if %ERRORLEVEL% equ 0 (
    echo.
    echo Tests terminés avec succès!
    echo Les résultats sont disponibles dans le dossier test_results/
) else (
    echo.
    echo Certains tests ont échoué.
    echo Consultez les logs dans le dossier test_results/ pour plus de détails.
)

exit /b %ERRORLEVEL% 