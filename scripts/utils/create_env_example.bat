@echo off
setlocal

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers la racine du projet
set "PROJECT_ROOT=%~dp0..\.."

REM Copier le fichier d'exemple vers .env.example à la racine
copy /Y "%~dp0env.example" "%PROJECT_ROOT%\.env.example"

if %errorlevel% equ 0 (
    echo Fichier .env.example créé avec succès à la racine du projet
) else (
    echo Erreur lors de la création du fichier .env.example
)

exit /b %errorlevel% 