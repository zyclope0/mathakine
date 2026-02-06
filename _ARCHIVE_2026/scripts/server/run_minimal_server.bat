@echo off
echo ===================================================
echo    Math Trainer Backend - Serveur Minimal
echo ===================================================
echo.

REM Se placer dans le dossier du projet principal
cd /d "%~dp0"
cd ..\..
echo Repertoire actuel: %CD%
echo.

REM Charger les variables d'environnement
call scripts\utils\load_env.bat
echo.

REM Afficher la configuration du serveur
echo Configuration du serveur:
echo - Profil: %MATH_TRAINER_PROFILE%
echo - Port: %MATH_TRAINER_PORT%
echo - Mode debug: %MATH_TRAINER_DEBUG%
echo - Niveau de log: %MATH_TRAINER_LOG_LEVEL%
echo.

echo Demarrage du serveur minimal (API)...
python minimal_server.py

pause 