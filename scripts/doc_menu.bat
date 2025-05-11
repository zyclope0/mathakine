@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Menu de gestion de la documentation Mathakine
REM ===================================================

:menu
cls
echo ===================================================
echo   Mathakine - Menu de Gestion de la Documentation
echo ===================================================
echo.
echo  GÉNÉRATION DE CONTEXTE
echo  ---------------------
echo  1. Générer un rapport de contexte (afficher)
echo  2. Mettre à jour le fichier CONTEXT.md
echo  3. Générer un rapport JSON (pour intégration)
echo.
echo  CONSOLIDATION ET NETTOYAGE
echo  -------------------------
echo  4. Consolider les documents qui se chevauchent
echo  5. Vérifier les fichiers redondants
echo  6. Supprimer les fichiers redondants
echo  7. Archiver les fichiers obsolètes et sauvegardes
echo.
echo  VALIDATION ET MAINTENANCE
echo  -----------------------
echo  8. Valider l'intégrité de la documentation
echo  9. Vérifier les liens dans la documentation
echo.
echo  0. Retour au menu principal
echo.
set /p choix="Votre choix (0-9): "

if "%choix%"=="1" goto :generate_context
if "%choix%"=="2" goto :update_context
if "%choix%"=="3" goto :json_context
if "%choix%"=="4" goto :consolidate_docs
if "%choix%"=="5" goto :check_redundant
if "%choix%"=="6" goto :remove_redundant
if "%choix%"=="7" goto :archive_files
if "%choix%"=="8" goto :validate_docs
if "%choix%"=="9" goto :check_links
if "%choix%"=="0" goto :exit

echo.
echo Choix invalide! Veuillez réessayer.
timeout /t 2 >nul
goto :menu

:generate_context
cls
echo Génération d'un rapport de contexte...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\generate_context.py" (
    echo ERREUR: Script generate_context.py introuvable!
    echo Vérifiez que le fichier scripts\generate_context.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script
python "%~dp0..\scripts\generate_context.py"
echo.
pause
goto :menu

:update_context
cls
echo Mise à jour du fichier CONTEXT.md...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\generate_context.py" (
    echo ERREUR: Script generate_context.py introuvable!
    echo Vérifiez que le fichier scripts\generate_context.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script avec l'option --update
python "%~dp0..\scripts\generate_context.py" --update
echo.
pause
goto :menu

:json_context
cls
echo Génération d'un rapport JSON...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\generate_context.py" (
    echo ERREUR: Script generate_context.py introuvable!
    echo Vérifiez que le fichier scripts\generate_context.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script avec l'option --json
python "%~dp0..\scripts\generate_context.py" --json > "%~dp0..\docs\context_report.json"
echo Rapport JSON généré: docs\context_report.json
echo.
pause
goto :menu

:consolidate_docs
cls
echo Consolidation des documents qui se chevauchent...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\consolidate_docs.py" (
    echo ERREUR: Script consolidate_docs.py introuvable!
    echo Vérifiez que le fichier scripts\consolidate_docs.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script
python "%~dp0..\scripts\consolidate_docs.py"
echo.
pause
goto :menu

:check_redundant
cls
echo Vérification des fichiers redondants...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\cleanup_redundant_docs.py" (
    echo ERREUR: Script cleanup_redundant_docs.py introuvable!
    echo Vérifiez que le fichier scripts\cleanup_redundant_docs.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script avec l'option check
python "%~dp0..\scripts\cleanup_redundant_docs.py" check
echo.
pause
goto :menu

:remove_redundant
cls
echo Suppression des fichiers redondants...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\cleanup_redundant_docs.py" (
    echo ERREUR: Script cleanup_redundant_docs.py introuvable!
    echo Vérifiez que le fichier scripts\cleanup_redundant_docs.py existe.
    echo.
    pause
    goto :menu
)

REM Demander confirmation
echo ATTENTION: Cette opération va supprimer les fichiers redondants.
echo Des sauvegardes (.bak) seront créées, mais assurez-vous d'avoir
echo vérifié que la consolidation est correcte avant de continuer.
echo.
set /p confirm="Êtes-vous sûr de vouloir continuer? (o/n): "
if /i not "%confirm%"=="o" goto :menu

REM Exécuter le script avec l'option remove
python "%~dp0..\scripts\cleanup_redundant_docs.py" remove
echo.
pause
goto :menu

:archive_files
cls
echo Archivage des fichiers obsolètes et sauvegardes...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\move_obsolete_files.py" (
    echo ERREUR: Script move_obsolete_files.py introuvable!
    echo Vérifiez que le fichier scripts\move_obsolete_files.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script
python "%~dp0..\scripts\move_obsolete_files.py"
echo.
pause
goto :menu

:validate_docs
cls
echo Validation de l'intégrité de la documentation...
echo.

REM Vérifier que le script existe
if not exist "%~dp0..\scripts\validate_docs.py" (
    echo ERREUR: Script validate_docs.py introuvable!
    echo Vérifiez que le fichier scripts\validate_docs.py existe.
    echo.
    pause
    goto :menu
)

REM Exécuter le script
python "%~dp0..\scripts\validate_docs.py"
echo.
pause
goto :menu

:check_links
cls
echo Vérification des liens dans la documentation...
echo.

REM Cette fonctionnalité nécessiterait un script Python dédié
echo Cette fonctionnalité n'est pas encore implémentée.
echo Elle nécessiterait un script Python pour analyser les liens
echo dans les fichiers Markdown et vérifier leur validité.
echo.
pause
goto :menu

:exit
exit /b 0 