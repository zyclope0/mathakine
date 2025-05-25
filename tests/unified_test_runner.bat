@echo off
rem -----------------------------------------------
rem Lanceur unifié des tests pour Mathakine
rem -----------------------------------------------
rem Ce script batch exécute unified_test_runner.py en
rem transmettant tous les arguments.
rem 
rem Usage: unified_test_runner.bat [options]
rem 
rem Exemples:
rem   unified_test_runner.bat --unit --fix-enums
rem   unified_test_runner.bat --all --verbose
rem   unified_test_runner.bat --api --fast
rem -----------------------------------------------

setlocal

echo ===================================================
echo    MATHAKINE - EXÉCUTION DES TESTS
echo ===================================================

rem Obtenir le répertoire où se trouve ce script
set "SCRIPT_DIR=%~dp0"
set "PYTHON_CMD=python"

rem Vérifier si Python est disponible
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Erreur: Python n'est pas disponible. Vérifiez votre installation.
    exit /b 1
)

rem Vérifier si le script unified_test_runner.py existe
if not exist "%SCRIPT_DIR%unified_test_runner.py" (
    echo Erreur: Le script unified_test_runner.py est introuvable.
    exit /b 1
)

rem Afficher la commande qui sera exécutée
echo Exécution de: %PYTHON_CMD% "%SCRIPT_DIR%unified_test_runner.py" %*
echo.

rem Exécuter le script Python en transmettant tous les arguments
%PYTHON_CMD% "%SCRIPT_DIR%unified_test_runner.py" %*

rem Capturer le code de retour
set RETURN_CODE=%ERRORLEVEL%

rem Afficher un message de résultat
if %RETURN_CODE% equ 0 (
    echo.
    echo ===================================================
    echo    RÉSULTAT: SUCCÈS - Tous les tests ont réussi
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo    RÉSULTAT: ÉCHEC - Des tests ont échoué
    echo ===================================================
)

exit /b %RETURN_CODE% 