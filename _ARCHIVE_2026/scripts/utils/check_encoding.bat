@echo off
setlocal

REM Script pour vérifier l'encodage des fichiers du projet
REM Ce script identifie les fichiers avec des problèmes d'encodage des caractères accentués

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Vérifier si Python est disponible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Erreur: Python n'est pas disponible dans le PATH.
    exit /b 1
)

REM Installer colorama si nécessaire (pour les couleurs dans la console)
pip show colorama >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation du module colorama pour l'affichage en couleur...
    pip install colorama
)

REM Installer chardet si nécessaire (pour la détection d'encodage)
pip show chardet >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation du module chardet pour la détection d'encodage...
    pip install chardet
)

REM Exécuter le script de vérification d'encodage
python check_encoding.py

REM Récupérer le code de retour
set EXIT_CODE=%errorlevel%

REM Retourner le code de sortie
exit /b %EXIT_CODE% 