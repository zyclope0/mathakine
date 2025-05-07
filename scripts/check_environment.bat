@echo off
echo === Math Trainer Backend - Verification de l'environnement ===
echo.

REM Se placer dans le dossier du script
cd /d "%~dp0"
echo Repertoire actuel: %CD%

echo.
echo 1. Verification de Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.8+ depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher l'option "Add Python to PATH" lors de l'installation.
    set /a erreurs+=1
) else (
    python --version
    echo [OK] Python est installe.
)

echo.
echo 2. Verification des fichiers de projet essentiels...
set /a manquants=0
if not exist requirements.txt (
    echo [MANQUANT] requirements.txt
    set /a manquants+=1
)
if not exist app\main.py (
    echo [MANQUANT] app\main.py
    set /a manquants+=1
)
if not exist app\core\config.py (
    echo [MANQUANT] app\core\config.py
    set /a manquants+=1
)
if not exist app\db\base.py (
    echo [MANQUANT] app\db\base.py
    set /a manquants+=1
)
if %manquants% equ 0 (
    echo [OK] Tous les fichiers essentiels sont presents.
) else (
    echo [ATTENTION] %manquants% fichiers essentiels sont manquants.
    set /a erreurs+=1
)

echo.
echo 3. Verification du fichier .env...
if not exist .env (
    echo [MANQUANT] Fichier .env
    echo Creation du fichier .env par defaut...
    echo # Configuration de base > .env
    echo DEBUG=True >> .env
    echo DATABASE_URL=sqlite:///./math_trainer.db >> .env
    echo [REPARE] Fichier .env cree.
) else (
    echo [OK] Fichier .env present.
)

echo.
echo 4. Verification des packages Python...
echo --- Tentative d'importation des packages essentiels ---

REM Créer un script temporaire pour tester les imports
echo import sys > check_imports.py
echo packages_requis = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "dotenv", "loguru"] >> check_imports.py
echo manquants = [] >> check_imports.py
echo for pkg in packages_requis: >> check_imports.py
echo     try: >> check_imports.py
echo         __import__(pkg) >> check_imports.py
echo         print(f"[OK] {pkg} est installe") >> check_imports.py
echo     except ImportError: >> check_imports.py
echo         manquants.append(pkg) >> check_imports.py
echo         print(f"[MANQUANT] {pkg} n'est pas installe") >> check_imports.py
echo if manquants: >> check_imports.py
echo     print(f"\n[ERREUR] {len(manquants)} packages sont manquants") >> check_imports.py
echo     sys.exit(1) >> check_imports.py
echo else: >> check_imports.py
echo     print("\n[OK] Tous les packages essentiels sont installes") >> check_imports.py
echo     sys.exit(0) >> check_imports.py

python check_imports.py
if %errorlevel% neq 0 (
    echo.
    echo [CONSEIL] Executez clean_install.bat ou run_simple.bat pour installer les dependances manquantes.
    set /a erreurs+=1
) else (
    echo [OK] Tous les packages sont correctement installes.
)

REM Supprimer le script temporaire
del check_imports.py

echo.
echo 5. Verification des versions des packages...
echo --- Verification de la compatibilite des versions ---

REM Créer un script temporaire pour vérifier les versions
echo import sys > check_versions.py
echo import pkg_resources >> check_versions.py
echo versions_requises = { >> check_versions.py
echo     "fastapi": "0.95.2", >> check_versions.py
echo     "uvicorn": "0.22.0", >> check_versions.py
echo     "pydantic": "1.10.8", >> check_versions.py
echo     "sqlalchemy": "2.0.20" >> check_versions.py
echo } >> check_versions.py
echo incompatibles = [] >> check_versions.py
echo for pkg, version in versions_requises.items(): >> check_versions.py
echo     try: >> check_versions.py
echo         installed = pkg_resources.get_distribution(pkg).version >> check_versions.py
echo         print(f"{pkg}: version installee = {installed}, version recommandee = {version}") >> check_versions.py
echo         if installed != version: >> check_versions.py
echo             incompatibles.append(f"{pkg} (installe: {installed}, requis: {version})") >> check_versions.py
echo     except pkg_resources.DistributionNotFound: >> check_versions.py
echo         print(f"{pkg}: Non installe") >> check_versions.py
echo         incompatibles.append(f"{pkg} (non installe)") >> check_versions.py
echo if incompatibles: >> check_versions.py
echo     print(f"\n[ATTENTION] {len(incompatibles)} packages ont des versions differentes des recommandations:") >> check_versions.py
echo     for pkg in incompatibles: >> check_versions.py
echo         print(f"  - {pkg}") >> check_versions.py
echo     print("\nCela peut causer des problemes de compatibilite.") >> check_versions.py
echo     sys.exit(1) >> check_versions.py
echo else: >> check_versions.py
echo     print("\n[OK] Toutes les versions sont compatibles.") >> check_versions.py
echo     sys.exit(0) >> check_versions.py

python check_versions.py
if %errorlevel% neq 0 (
    echo.
    echo [CONSEIL] Executez clean_install.bat pour installer les versions exactes recommandees.
    set /a erreurs+=1
)

echo.
echo 6. Verification de l'acces au port 8000...
REM Vérifier si le port 8000 est déjà utilisé
netstat -ano | find "LISTENING" | find ":8000" > nul
if %errorlevel% equ 0 (
    echo [ATTENTION] Le port 8000 est deja utilise par un autre processus.
    echo Vous devrez peut-etre utiliser un port different en modifiant le script de demarrage.
    set /a erreurs+=1
) else (
    echo [OK] Le port 8000 est disponible.
)

echo.
echo === Recapitulatif de la verification ===
if defined erreurs (
    if %erreurs% gtr 0 (
        echo [ATTENTION] %erreurs% problemes detectes.
        echo Pour resoudre ces problemes, executez clean_install.bat pour une installation complete.
    ) else (
        echo [OK] Aucun probleme detecte.
        echo Vous pouvez demarrer le serveur avec start_server.bat ou run_simple.bat
    )
) else (
    echo [OK] Aucun probleme detecte.
    echo Vous pouvez demarrer le serveur avec start_server.bat ou run_simple.bat
)

echo.
echo Appuyez sur une touche pour fermer...
pause > nul 