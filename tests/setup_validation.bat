@echo off
echo ===================================================
echo =  CONFIGURATION ENVIRONNEMENT DE VALIDATION     =
echo ===================================================
echo.
echo Ce script va configurer l'environnement pour les validations
echo en installant les dépendances nécessaires et en créant
echo les dossiers requis.
echo.
echo Appuyez sur une touche pour continuer ou CTRL+C pour annuler...
pause > nul

python tests/setup_validation.py

if errorlevel 1 (
    echo.
    echo La configuration a échoué. Veuillez vérifier les erreurs ci-dessus.
    exit /b 1
) else (
    echo.
    echo Configuration réussie !
    echo.
    echo Vous pouvez maintenant exécuter :
    echo  - tests\auto_validate.bat
    echo  - tests\auto_validator.bat
    echo.
    exit /b 0
) 