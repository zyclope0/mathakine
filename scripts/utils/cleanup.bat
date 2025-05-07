@echo off
echo ===================================================
echo    Math Trainer Backend - Nettoyage du projet
echo ===================================================
echo.

REM Se placer dans le dossier du projet principal
cd /d "%~dp0"
cd ..\..
echo Repertoire actuel: %CD%
echo.

echo 1. Suppression des fichiers de cache Python...
FOR /R . %%G IN (__pycache__\*.pyc) DO (
    echo Suppression: %%G
    del /Q "%%G" 2>nul
)

echo 2. Suppression des repertoires __pycache__...
FOR /D /R . %%G IN (__pycache__) DO (
    echo Suppression du dossier: %%G
    rd /S /Q "%%G" 2>nul
)

echo 3. Suppression des fichiers temporaires...
FOR %%G IN (*.log *.tmp test_*.db) DO (
    if exist %%G (
        echo Suppression: %%G
        del /Q "%%G" 2>nul
    )
)

echo 4. Verification de la structure du projet...
if not exist tests (
    echo Creation du dossier "tests"...
    mkdir tests
)

echo 5. Verification du fichier .env...
if not exist .env (
    echo Creation du fichier .env...
    if exist sample.env (
        copy sample.env .env >nul
        echo Fichier .env cree.
    ) else (
        echo # Configuration de base > .env
        echo DEBUG=True >> .env
        echo DATABASE_URL=sqlite:///./math_trainer.db >> .env
        echo Fichier .env cree.
    )
)

echo.
echo ===================================================
echo    Nettoyage termine!
echo ===================================================
echo.
echo Lancement de l'application:
echo.
echo   scripts\server\start_math_trainer.bat     (Interface interactive)
echo   scripts\server\run_enhanced_server.bat    (Version complete avec UI)
echo   scripts\server\run_minimal_server.bat     (Version API uniquement)
echo.
echo Tests:
echo.
echo   scripts\tests\auto_test.bat              (Tests de non-regression rapides)
echo   scripts\tests\run_tests.bat              (Tests complets)
echo.

pause 