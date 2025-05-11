@echo off
setlocal enabledelayedexpansion

echo =======================================
echo =     MATHAKINE TEST RUNNER          =
echo =======================================
echo.

rem Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    exit /b 1
)

rem Créer le dossier de résultats s'il n'existe pas
mkdir test_results 2>nul

rem Analyser les arguments
set MODE=help
set VERBOSE=
set COVERAGE=
set TEST_TYPE=
set TEST_FILE=

:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--full" set MODE=full
if /i "%~1"=="--basic" set MODE=basic
if /i "%~1"=="--report" set MODE=report
if /i "%~1"=="--unit" set MODE=type& set TEST_TYPE=unit
if /i "%~1"=="--api" set MODE=type& set TEST_TYPE=api
if /i "%~1"=="--integration" set MODE=type& set TEST_TYPE=integration
if /i "%~1"=="--functional" set MODE=type& set TEST_TYPE=functional
if /i "%~1"=="--file" set MODE=file& set TEST_FILE=%~2& shift
if /i "%~1"=="--verbose" set VERBOSE=--verbose
if /i "%~1"=="--no-coverage" set COVERAGE=--no-coverage
if /i "%~1"=="--help" set MODE=help
shift
goto :parse_args
:end_parse_args

rem Exécuter le mode choisi
if "%MODE%"=="help" (
    echo UTILISATION: run_tests.bat [OPTIONS]
    echo.
    echo Options:
    echo   --full           Execute une validation complete
    echo   --basic          Execute une validation basique (tests unitaires et API)
    echo   --report         Genere uniquement les rapports
    echo   --unit           Execute uniquement les tests unitaires
    echo   --api            Execute uniquement les tests d'API
    echo   --integration    Execute uniquement les tests d'integration
    echo   --functional     Execute uniquement les tests fonctionnels
    echo   --file FILE      Execute un fichier de test specifique
    echo   --verbose        Mode verbeux
    echo   --no-coverage    Desactive la couverture de code
    echo   --help           Affiche ce message d'aide
    echo.
    echo Exemples:
    echo   run_tests.bat --full
    echo   run_tests.bat --unit --verbose
    echo   run_tests.bat --file tests/unit/test_models.py
    exit /b 0
)

if "%MODE%"=="full" (
    echo Execution de la validation complete...
    python tests/automation/run_tests.py --full
    goto :end
)

if "%MODE%"=="basic" (
    echo Execution de la validation basique...
    python tests/automation/run_tests.py --basic
    goto :end
)

if "%MODE%"=="report" (
    echo Generation des rapports...
    python tests/automation/run_tests.py --report
    goto :end
)

if "%MODE%"=="type" (
    echo Execution des tests de type %TEST_TYPE%...
    python tests/automation/run_tests.py --type %TEST_TYPE% %VERBOSE% %COVERAGE%
    goto :end
)

if "%MODE%"=="file" (
    echo Execution du fichier de test %TEST_FILE%...
    python tests/automation/run_tests.py --file %TEST_FILE% %VERBOSE% %COVERAGE%
    goto :end
)

:end
if errorlevel 1 (
    echo [ERREUR] Les tests ont echoue avec le code %errorlevel%
) else (
    echo [SUCCES] Tous les tests ont reussi
)

echo.
echo Consultez les rapports dans le dossier test_results/
echo =======================================
endlocal
exit /b %errorlevel% 