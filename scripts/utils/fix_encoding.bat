@echo off
setlocal

REM Ce script corrige l'encodage des caractères accentués dans le fichier env.example
REM et recrée le fichier .env.example avec le bon encodage (UTF-8)

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers la racine du projet
set "PROJECT_ROOT=%~dp0..\.."
set "ENV_EXAMPLE=%~dp0env.example"
set "ENV_EXAMPLE_TMP=%~dp0env_example_utf8.tmp"
set "ENV_EXAMPLE_DEST=%PROJECT_ROOT%\.env.example"

echo ===================================================
echo Correction de l'encodage des caractères accentués
echo ===================================================

REM Créer un nouveau fichier encodé en UTF-8
echo # Math Trainer - Fichier d'environnement exemple> "%ENV_EXAMPLE_TMP%"
echo # Copiez ce fichier vers .env à la racine du projet et ajustez les valeurs selon votre environnement>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Configuration du serveur>> "%ENV_EXAMPLE_TMP%"
echo MATH_TRAINER_DEBUG=true                # Active/désactive le mode debug (true/false)>> "%ENV_EXAMPLE_TMP%"
echo MATH_TRAINER_PORT=8081                 # Port du serveur web>> "%ENV_EXAMPLE_TMP%"
echo MATH_TRAINER_LOG_LEVEL=INFO            # Niveau de logs (DEBUG, INFO, WARNING, ERROR)>> "%ENV_EXAMPLE_TMP%"
echo MATH_TRAINER_TEST_MODE=false           # Active/désactive le mode test (true/false)>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Base de données>> "%ENV_EXAMPLE_TMP%"
echo DATABASE_URL=sqlite:///./math_trainer.db # URL de connexion à la base de données>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Intégration OpenAI (optionnel)>> "%ENV_EXAMPLE_TMP%"
echo OPENAI_API_KEY=votre_clé_api_ici       # Clé API OpenAI (ne pas committer ce fichier avec une vraie clé)>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Profil d'environnement>> "%ENV_EXAMPLE_TMP%"
echo MATH_TRAINER_PROFILE=dev               # Profil actif (dev, test, prod)>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Variables spécifiques aux tests>> "%ENV_EXAMPLE_TMP%"
echo # TEST_DATABASE_URL=sqlite:///./math_trainer_test.db  # Base de données dédiée aux tests>> "%ENV_EXAMPLE_TMP%"
echo.>> "%ENV_EXAMPLE_TMP%"
echo # Variables spécifiques à la production>> "%ENV_EXAMPLE_TMP%"
echo # ALLOWED_HOSTS=mathtrainer.example.com,localhost  # Hôtes autorisés en production>> "%ENV_EXAMPLE_TMP%"
echo # SESSION_COOKIE_SECURE=true                       # Cookies sécurisés en production>> "%ENV_EXAMPLE_TMP%"

REM Remplacer le fichier env.example par la version avec encodage corrigé
copy /Y "%ENV_EXAMPLE_TMP%" "%ENV_EXAMPLE%"
if %errorlevel% neq 0 (
    echo Erreur lors de la mise à jour du fichier env.example
    goto :cleanup
)

REM Copier le fichier corrigé vers .env.example à la racine du projet
copy /Y "%ENV_EXAMPLE_TMP%" "%ENV_EXAMPLE_DEST%"
if %errorlevel% neq 0 (
    echo Erreur lors de la création du fichier .env.example
    goto :cleanup
) else (
    echo Le fichier .env.example a été créé avec succès avec le bon encodage des caractères accentués
)

:cleanup
REM Supprimer le fichier temporaire
if exist "%ENV_EXAMPLE_TMP%" del "%ENV_EXAMPLE_TMP%"

exit /b %errorlevel% 