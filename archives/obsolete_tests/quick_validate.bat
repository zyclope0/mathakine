@echo off
echo === Mathakine - Validation Rapide ===
echo.

REM Activer l'environnement virtuel si présent
if exist "%~dp0\..\venv\Scripts\activate.bat" (
    call "%~dp0\..\venv\Scripts\activate.bat"
    echo Environnement virtuel activé
) else (
    echo ATTENTION: Environnement virtuel non trouvé
)

REM Exécuter le script de validation rapide
echo Lancement de la validation rapide...
echo.
python "%~dp0\quick_validation.py"

REM Capturer le code de retour
set RESULT=%ERRORLEVEL%

echo.
if %RESULT% EQU 0 (
    echo Validation rapide terminée avec succès.
) else (
    echo Validation rapide terminée avec des erreurs.
)

REM Mettre en pause uniquement si l'exécution est interactive
if not defined CI pause 