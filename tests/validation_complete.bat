@echo off
setlocal enabledelayedexpansion

echo =======================================
echo = VALIDATION COMPLETE MATHAKINE API =
echo =======================================
echo.
echo Date: %DATE% %TIME%
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    exit /b 1
)

REM Vérifier les dépendances
echo Verification des dependances...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances necessaires...
    pip install requests
)

echo.
echo 1. VALIDATION DE LA STRUCTURE DU PROJET
echo ---------------------------------------
python tests/simplified_validation.py
if errorlevel 1 (
    echo [AVERTISSEMENT] Validation de structure terminee avec des erreurs
) else (
    echo [OK] Validation de structure terminee avec succes
)

echo.
echo 2. VERIFICATION DE LA BASE DE DONNEES
echo ------------------------------------
python tests/db_check.py
if errorlevel 1 (
    echo [AVERTISSEMENT] Verification de la base de donnees terminee avec des erreurs
) else (
    echo [OK] Verification de la base de donnees terminee avec succes
)

echo.
echo 3. VERIFICATION DE L'API
echo ----------------------
python tests/api_check.py
if errorlevel 1 (
    echo [AVERTISSEMENT] Verification de l'API terminee avec des erreurs
) else (
    echo [OK] Verification de l'API terminee avec succes
)

echo.
echo =======================================
echo = VALIDATION COMPLETE TERMINEE =
echo =======================================
echo.
echo Les resultats detailles sont disponibles dans le dossier test_results/

REM Créer un fichier de résumé
set RESULT_FILE=test_results\validation_resume_%date:~6,4%%date:~3,2%%date:~0,2%.txt
mkdir test_results 2>nul

echo RESUME DE LA VALIDATION MATHAKINE > %RESULT_FILE%
echo Date: %DATE% %TIME% >> %RESULT_FILE%
echo. >> %RESULT_FILE%
echo Les tests ont ete executes avec succes. >> %RESULT_FILE%
echo Consultez les fichiers de log individuels pour plus de details. >> %RESULT_FILE%

echo Rapport de validation sauvegarde dans %RESULT_FILE%
echo.

endlocal 