@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Script de gestion des variables d'environnement pour Math Trainer
REM ===================================================

REM Se placer dans le dossier du script
cd /d "%~dp0"

REM Chemin vers la racine du projet
set "PROJECT_ROOT=%~dp0..\.."

REM Récupération des paramètres
set "PROFILE=dev"
set "LIST_MODE="
set "EXPORT_MODE="
set "VALIDATE_MODE="
set "FIX_MODE="
set "ENV_FILE=%PROJECT_ROOT%\.env"
set "CUSTOM_KEY="
set "CUSTOM_VALUE="

:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="--profile" (
    set "PROFILE=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--list" (
    set "LIST_MODE=1"
    shift
    goto :parse_args
)
if /i "%~1"=="--export" (
    set "EXPORT_MODE=1"
    shift
    goto :parse_args
)
if /i "%~1"=="--validate" (
    set "VALIDATE_MODE=1"
    shift
    goto :parse_args
)
if /i "%~1"=="--fix" (
    set "FIX_MODE=1"
    shift
    goto :parse_args
)
if /i "%~1"=="--env-file" (
    set "ENV_FILE=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--key" (
    set "CUSTOM_KEY=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--value" (
    set "CUSTOM_VALUE=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo ===================================================
echo    Math Trainer - Aide de gestion d'environnement
echo ===================================================
echo.
echo Profils disponibles:
echo   dev  - Environnement de développement (debug:true, port:8081)
echo   test - Environnement de test (debug:true, port:8082)
echo   prod - Environnement de production (debug:false, port:8080)
echo.
echo Options:
echo   --profile NOM    Définir le profil à utiliser
echo   --export         Exporter les variables vers .env
echo   --list           Lister les variables du profil
echo   --validate       Valider les variables d'environnement
echo   --fix            Tenter de corriger les variables invalides
echo   --key NOM        Spécifier une variable
echo   --value VAL      Définir la valeur d'une variable
echo   --env-file FICHIER Spécifier un fichier .env différent
echo   --help           Afficher cette aide
echo.
exit /b 0

:main
REM Initialiser les variables
set "MATH_TRAINER_DEBUG="
set "MATH_TRAINER_PORT="
set "MATH_TRAINER_LOG_LEVEL="
set "MATH_TRAINER_TEST_MODE="
set "MATH_TRAINER_PROFILE="

REM Utiliser le module Python pour charger les profils - Utilise des barres obliques avant pour éviter les problèmes d'échappement
set "script_path=%~dp0"
set "script_path=%script_path:\=/%"
python -c "import sys; sys.path.append('%script_path%'); from load_profiles import get_profile; profile = get_profile('%PROFILE%'); print('\n'.join([f'{k}={v}' for k, v in profile.items()]))" > "%TEMP%\profile_vars.txt"

REM En cas d'erreur avec le module Python, utiliser le fallback
if %errorlevel% neq 0 (
    echo Erreur lors du chargement du profil. Utilisation des valeurs par défaut.
    goto :fallback_profiles
) else (
    REM Charger les variables depuis le fichier temporaire
    for /f "usebackq tokens=*" %%a in ("%TEMP%\profile_vars.txt") do (
        set "%%a"
    )
    del "%TEMP%\profile_vars.txt"
)

goto :after_profile_load

:fallback_profiles
if /i "%PROFILE%"=="dev" (
    set "MATH_TRAINER_DEBUG=true"
    set "MATH_TRAINER_PORT=8081"
    set "MATH_TRAINER_LOG_LEVEL=DEBUG"
    set "MATH_TRAINER_TEST_MODE=true"
    set "MATH_TRAINER_PROFILE=dev"
) else if /i "%PROFILE%"=="test" (
    set "MATH_TRAINER_DEBUG=true"
    set "MATH_TRAINER_PORT=8082"
    set "MATH_TRAINER_LOG_LEVEL=INFO"
    set "MATH_TRAINER_TEST_MODE=true"
    set "MATH_TRAINER_PROFILE=test"
) else if /i "%PROFILE%"=="prod" (
    set "MATH_TRAINER_DEBUG=false"
    set "MATH_TRAINER_PORT=8080"
    set "MATH_TRAINER_LOG_LEVEL=WARNING"
    set "MATH_TRAINER_TEST_MODE=false"
    set "MATH_TRAINER_PROFILE=prod"
)

:after_profile_load
REM Importer les variables d'un fichier .env existant seulement si on n'exporte pas
if not defined EXPORT_MODE (
    if exist "%ENV_FILE%" (
        for /f "usebackq tokens=*" %%a in ("%ENV_FILE%") do (
            set "line=%%a"
            if not "!line:~0,1!"=="#" (
                for /f "tokens=1,* delims==" %%b in ("!line!") do (
                    if not "%%b"=="" if not "%%c"=="" (
                        set "%%b=%%c"
                    )
                )
            )
        )
    )
)

REM Définir une variable spécifique si demandé
if not "%CUSTOM_KEY%"=="" if not "%CUSTOM_VALUE%"=="" (
    set "%CUSTOM_KEY%=%CUSTOM_VALUE%"
    echo Variable '%CUSTOM_KEY%' définie à '%CUSTOM_VALUE%'
)

REM Valider les variables si demandé
if defined VALIDATE_MODE (
    echo.
    echo Validation des variables d'environnement...
    echo.
    
    REM Créer un fichier temporaire avec les variables actuelles
    set "TEMP_ENV=%TEMP%\temp_env.env"
    (
        echo # Fichier d'environnement temporaire
        echo MATH_TRAINER_DEBUG=%MATH_TRAINER_DEBUG%
        echo MATH_TRAINER_PORT=%MATH_TRAINER_PORT%
        echo MATH_TRAINER_LOG_LEVEL=%MATH_TRAINER_LOG_LEVEL%
        echo MATH_TRAINER_TEST_MODE=%MATH_TRAINER_TEST_MODE%
        echo MATH_TRAINER_PROFILE=%MATH_TRAINER_PROFILE%
        if defined OPENAI_API_KEY (
            echo OPENAI_API_KEY=%OPENAI_API_KEY%
        )
    ) > "%TEMP_ENV%"
    
    REM Valider avec le module de validation
    python "%~dp0validate_env.py" --env-file "%TEMP_ENV%"
    set "VALIDATION_RESULT=%errorlevel%"
    
    REM Supprimer le fichier temporaire
    del "%TEMP_ENV%"
    
    REM Si la validation échoue et que le mode fix est activé, tenter de corriger
    if %VALIDATION_RESULT% neq 0 (
        if defined FIX_MODE (
            echo.
            echo Tentative de correction des variables...
            
            REM Cas connus: correction des valeurs booléennes
            for %%v in (MATH_TRAINER_DEBUG MATH_TRAINER_TEST_MODE) do (
                call :fix_boolean %%v
            )
            
            REM Cas connus: correction des niveaux de log
            call :fix_log_level MATH_TRAINER_LOG_LEVEL
            
            REM Cas connus: correction des ports
            call :fix_port MATH_TRAINER_PORT
            
            REM Cas connus: correction des profils
            call :fix_profile MATH_TRAINER_PROFILE
            
            echo.
            echo Variables corrigées. Nouvelle validation:
            goto :validate_again
        )
    )
)

REM Lister les variables d'environnement
if defined LIST_MODE (
    echo.
    echo Variables d'environnement pour le profil: %PROFILE%
    echo ====================================================
    echo MATH_TRAINER_DEBUG=%MATH_TRAINER_DEBUG%
    echo MATH_TRAINER_PORT=%MATH_TRAINER_PORT%
    echo MATH_TRAINER_LOG_LEVEL=%MATH_TRAINER_LOG_LEVEL%
    echo MATH_TRAINER_TEST_MODE=%MATH_TRAINER_TEST_MODE%
    echo MATH_TRAINER_PROFILE=%MATH_TRAINER_PROFILE%
    
    REM Afficher les variables OpenAI avec masquage
    if defined OPENAI_API_KEY (
        REM Afficher les premiers caractères de la clé, masquer le reste
        set "masked_key=!OPENAI_API_KEY:~0,4!********"
        echo OPENAI_API_KEY=!masked_key!
    )
    echo.
)

REM Exporter les variables dans un fichier .env
if defined EXPORT_MODE (
    REM Vérifier que le profil est valide
    set "VALID_PROFILE=0"
    if /i "%MATH_TRAINER_PROFILE%"=="dev" set "VALID_PROFILE=1"
    if /i "%MATH_TRAINER_PROFILE%"=="test" set "VALID_PROFILE=1"
    if /i "%MATH_TRAINER_PROFILE%"=="prod" set "VALID_PROFILE=1"
    
    if "!VALID_PROFILE!"=="0" (
        echo [AVERTISSEMENT] Profil '%MATH_TRAINER_PROFILE%' invalide, utilisation du profil spécifié: %PROFILE%
        set "MATH_TRAINER_PROFILE=%PROFILE%"
    )
    
    REM Créer le fichier .env
    echo # Fichier d'environnement Math Trainer> "%ENV_FILE%"
    echo # Généré le %date%>> "%ENV_FILE%"
    echo.>> "%ENV_FILE%"
    echo DATABASE_URL=sqlite:///./math_trainer.db>> "%ENV_FILE%"
    echo MATH_TRAINER_DEBUG=%MATH_TRAINER_DEBUG%>> "%ENV_FILE%"
    echo MATH_TRAINER_LOG_LEVEL=%MATH_TRAINER_LOG_LEVEL%>> "%ENV_FILE%"
    echo MATH_TRAINER_PORT=%MATH_TRAINER_PORT%>> "%ENV_FILE%"
    echo MATH_TRAINER_PROFILE=%MATH_TRAINER_PROFILE%>> "%ENV_FILE%"
    echo MATH_TRAINER_TEST_MODE=%MATH_TRAINER_TEST_MODE%>> "%ENV_FILE%"
    
    if defined OPENAI_API_KEY (
        echo OPENAI_API_KEY=%OPENAI_API_KEY%>> "%ENV_FILE%"
    )
    
    echo Variables d'environnement exportées vers %ENV_FILE%
)

REM Fin du script en mode local
if defined LIST_MODE (
    echo Utilisez --export pour sauvegarder ces variables dans un fichier .env
)
if defined EXPORT_MODE (
    echo Pour appliquer ces variables à votre session, utilisez:
    echo call %~nx0 --profile %PROFILE%
)

exit /b 0

:validate_again
REM Créer un fichier temporaire avec les variables corrigées
set "TEMP_ENV=%TEMP%\temp_env.env"
(
    echo # Fichier d'environnement temporaire
    echo MATH_TRAINER_DEBUG=%MATH_TRAINER_DEBUG%
    echo MATH_TRAINER_PORT=%MATH_TRAINER_PORT%
    echo MATH_TRAINER_LOG_LEVEL=%MATH_TRAINER_LOG_LEVEL%
    echo MATH_TRAINER_TEST_MODE=%MATH_TRAINER_TEST_MODE%
    echo MATH_TRAINER_PROFILE=%MATH_TRAINER_PROFILE%
    if defined OPENAI_API_KEY (
        echo OPENAI_API_KEY=%OPENAI_API_KEY%
    )
) > "%TEMP_ENV%"

REM Valider avec le module de validation
python "%~dp0validate_env.py" --env-file "%TEMP_ENV%"
set "VALIDATION_RESULT=%errorlevel%"

REM Supprimer le fichier temporaire
del "%TEMP_ENV%"

if %VALIDATION_RESULT% neq 0 (
    echo Impossible de corriger toutes les variables. Utilisez --list pour voir les valeurs actuelles.
) else (
    echo Toutes les variables sont maintenant valides.
)

goto :eof

:fix_boolean
REM Correction des valeurs booléennes
set "var_name=%~1"
set "var_value=!%var_name%!"

if /i "%var_value%"=="1" (
    set "%var_name%=true"
    echo - Corrigé: %var_name% (1 -> true)
) else if /i "%var_value%"=="0" (
    set "%var_name%=false"
    echo - Corrigé: %var_name% (0 -> false)
) else if /i "%var_value%"=="yes" (
    set "%var_name%=true"
    echo - Corrigé: %var_name% (yes -> true)
) else if /i "%var_value%"=="no" (
    set "%var_name%=false"
    echo - Corrigé: %var_name% (no -> false)
) else if /i "%var_value%"=="oui" (
    set "%var_name%=true"
    echo - Corrigé: %var_name% (oui -> true)
) else if /i "%var_value%"=="non" (
    set "%var_name%=false"
    echo - Corrigé: %var_name% (non -> false)
) else if /i "%var_value%"=="y" (
    set "%var_name%=true"
    echo - Corrigé: %var_name% (y -> true)
) else if /i "%var_value%"=="n" (
    set "%var_name%=false"
    echo - Corrigé: %var_name% (n -> false)
)

goto :eof

:fix_log_level
REM Correction des niveaux de log
set "var_name=%~1"
set "var_value=!%var_name%!"

if /i "%var_value%"=="debug" (
    set "%var_name%=DEBUG"
    echo - Corrigé: %var_name% (debug -> DEBUG)
) else if /i "%var_value%"=="info" (
    set "%var_name%=INFO"
    echo - Corrigé: %var_name% (info -> INFO)
) else if /i "%var_value%"=="warning" (
    set "%var_name%=WARNING"
    echo - Corrigé: %var_name% (warning -> WARNING)
) else if /i "%var_value%"=="error" (
    set "%var_name%=ERROR"
    echo - Corrigé: %var_name% (error -> ERROR)
) else if /i "%var_value%"=="critical" (
    set "%var_name%=CRITICAL"
    echo - Corrigé: %var_name% (critical -> CRITICAL)
) else if /i "%var_value%"=="warn" (
    set "%var_name%=WARNING"
    echo - Corrigé: %var_name% (warn -> WARNING)
) else if /i "%var_value%"=="err" (
    set "%var_name%=ERROR"
    echo - Corrigé: %var_name% (err -> ERROR)
)

goto :eof

:fix_port
REM Correction des ports
set "var_name=%~1"
set "var_value=!%var_name%!"

REM Extraire le nombre du port s'il contient des caractères non numériques
set "port_number="
for /f "delims=0123456789" %%i in ("%var_value%") do (
    set "non_numeric=%%i"
)

if defined non_numeric (
    REM Extraire uniquement les chiffres
    set "port_number="
    for /l %%i in (0,1,9) do call set "port_number=%%port_number:%%i=%%i%%"
    
    REM Si le port extrait est valide, l'utiliser
    if !port_number! geq 1024 if !port_number! leq 65535 (
        set "%var_name%=!port_number!"
        echo - Corrigé: %var_name% (%var_value% -> !port_number!)
    ) else (
        REM Si le port est invalide, utiliser le port par défaut du profil
        if /i "%PROFILE%"=="dev" (
            set "%var_name%=8081"
            echo - Corrigé: %var_name% (%var_value% -> 8081)
        ) else if /i "%PROFILE%"=="test" (
            set "%var_name%=8082"
            echo - Corrigé: %var_name% (%var_value% -> 8082)
        ) else (
            set "%var_name%=8080"
            echo - Corrigé: %var_name% (%var_value% -> 8080)
        )
    )
)

goto :eof

:fix_profile
REM Correction des profils
set "var_name=%~1"
set "var_value=!%var_name%!"

REM Convertir en minuscules pour la comparaison
set "lower_value=%var_value%"
for %%i in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
    set "lower_value=!lower_value:%%i=%%i!"
    set "lower_value=!lower_value:%%i=%%i!"
)

REM Correction basée sur des correspondances partielles
if not "%lower_value%"=="dev" if not "%lower_value%"=="test" if not "%lower_value%"=="prod" (
    if "%lower_value:dev=%" neq "%lower_value%" (
        set "%var_name%=dev"
        echo - Corrigé: %var_name% (%var_value% -> dev)
    ) else if "%lower_value:test=%" neq "%lower_value%" (
        set "%var_name%=test"
        echo - Corrigé: %var_name% (%var_value% -> test)
    ) else if "%lower_value:prod=%" neq "%lower_value%" (
        set "%var_name%=prod"
        echo - Corrigé: %var_name% (%var_value% -> prod)
    ) else (
        set "%var_name%=%PROFILE%"
        echo - Corrigé: %var_name% (%var_value% -> %PROFILE%)
    )
)

goto :eof 