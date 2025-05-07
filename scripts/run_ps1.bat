@echo off
setlocal enabledelayedexpansion

REM ===================================================
REM Wrapper pour l'exécution de scripts PowerShell
REM Contourne les restrictions de politique d'exécution
REM ===================================================

if "%~1"=="" (
    echo Erreur: Vous devez spécifier un script PowerShell à exécuter.
    echo.
    echo Usage: run_ps1.bat script.ps1 [arguments]
    exit /b 1
)

set "PS_SCRIPT=%~1"
shift

REM Vérifier que PowerShell est disponible
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Erreur: PowerShell n'est pas disponible dans votre système.
    echo Veuillez installer PowerShell pour utiliser cette fonctionnalité.
    exit /b 1
)

REM Construire les arguments pour PowerShell
set "PS_ARGS="
:build_args
if "%~1"=="" goto :execute
set "PS_ARGS=%PS_ARGS% %1"
shift
goto :build_args

:execute
echo Exécution de %PS_SCRIPT% avec droits d'exécution...
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %PS_ARGS%
exit /b %errorlevel% 