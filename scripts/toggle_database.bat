@echo off
setlocal

echo.
echo Basculer entre SQLite et PostgreSQL
echo ====================================
echo.
echo 1. Utiliser SQLite (base de données locale)
echo 2. Utiliser PostgreSQL (base de données serveur)
echo.

set /p choice="Entrez votre choix (1 ou 2): "

if "%choice%"=="1" (
    echo.
    echo Configuration pour SQLite...
    python scripts/toggle_database.py sqlite
) else if "%choice%"=="2" (
    echo.
    echo Configuration pour PostgreSQL...
    python scripts/toggle_database.py postgres
) else (
    echo.
    echo Choix invalide. Veuillez entrer 1 ou 2.
    exit /b 1
)

echo.
echo Configuration terminée.
echo.
echo Démarrer le serveur avec la nouvelle configuration ? (o/n)
set /p start_server="Votre choix : "

if "%start_server%"=="o" (
    echo.
    echo Démarrage du serveur...
    python enhanced_server.py
) else (
    echo.
    echo Vous pouvez démarrer le serveur manuellement avec 'python enhanced_server.py'
)

pause 