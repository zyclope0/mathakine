@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo =      AUTO-VALIDATEUR MATHAKINE - v1.0          =
echo ===================================================
echo.
echo Date: %DATE% %TIME%
echo.
echo Ce script va effectuer une validation complete du projet
echo et générer un rapport détaillé.
echo.
echo Appuyez sur une touche pour continuer ou CTRL+C pour annuler...
pause > nul

echo.
echo 1. VERIFICATION DE BASE
echo ---------------------
python tests/basic_check.py
if errorlevel 1 (
    echo [!] La vérification de base a échoué. Correction nécessaire avant de continuer.
    goto :end
)

echo.
echo 2. VALIDATION DE LA STRUCTURE
echo ---------------------------
python tests/simplified_validation.py
if errorlevel 1 (
    echo [i] Des avertissements ont été détectés dans la structure. Voir les détails ci-dessus.
) else (
    echo [OK] Structure validée avec succès.
)

echo.
echo 3. GENERATION DU RAPPORT COMPLET
echo ----------------------------
python tests/generate_report.py > nul
if errorlevel 1 (
    echo [!] Erreur lors de la génération du rapport.
) else (
    echo [OK] Rapport généré avec succès.
    
    rem Récupérer le chemin du rapport le plus récent
    for /f "delims=" %%i in ('dir /b /o-d test_results\rapport_complet_*.md') do (
        set "latest_report=test_results\%%i"
        goto :found_report
    )
    
    :found_report
    echo      Rapport disponible: !latest_report!
    
    rem Afficher un résumé du rapport
    echo.
    echo 4. RESUME DU RAPPORT
    echo -----------------
    echo Statut global:
    
    rem Vérifier si Python 3.13 est utilisé
    findstr /c:"Python 3.13" "!latest_report!" > nul
    if not errorlevel 1 (
        echo [!] PYTHON 3.13 DETECTE - PROBLEMES DE COMPATIBILITE
        echo     Recommendation: Utiliser Python 3.11 ou 3.12
    )
    
    rem Vérifier si des problèmes critiques sont présents
    findstr /c:"🔴 Haute" "!latest_report!" > nul
    if not errorlevel 1 (
        echo [!] PROBLEMES CRITIQUES DETECTES
        echo     Des problèmes de priorité haute requièrent votre attention
    )
    
    rem Ouvrir le rapport dans le navigateur par défaut
    echo.
    echo Voulez-vous ouvrir le rapport dans le navigateur ? (O/N)
    choice /c ON /n
    if errorlevel 2 goto :skip_open
    start "" "!latest_report!"
    :skip_open
)

:end
echo.
echo ===================================================
echo =          VALIDATION TERMINEE                    =
echo ===================================================
echo.
endlocal 