# Exemples de syntaxe PowerShell pour l'exécution de commandes multiples
# ===================================================

# 1. Utilisation de point-virgule (;) au lieu de && pour exécuter plusieurs commandes
Write-Host "`n=== Exemple 1: Point-virgule au lieu de && ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: cd C:\ProjetCursor\math-trainer-backend; Get-ChildItem -Filter *.bat"
Write-Host "CMD équivalent: cd C:\ProjetCursor\math-trainer-backend && dir *.bat`n"

# 2. Navigation dans les dossiers
Write-Host "`n=== Exemple 2: Navigation dans les dossiers ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: Push-Location C:\ProjetCursor\math-trainer-backend; Get-ChildItem; Pop-Location"
Write-Host "CMD équivalent: pushd C:\ProjetCursor\math-trainer-backend && dir && popd`n"

# 3. Exécution conditionnelle
Write-Host "`n=== Exemple 3: Exécution conditionnelle ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: if (Test-Path '.\requirements.txt') { Write-Host 'Le fichier existe' }"
Write-Host "CMD équivalent: if exist requirements.txt echo Le fichier existe`n"

# 4. Lancement d'un processus
Write-Host "`n=== Exemple 4: Lancement d'un processus ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: Start-Process python -ArgumentList 'enhanced_server.py'"
Write-Host "CMD équivalent: start python enhanced_server.py`n"

# 5. Obtention du répertoire actuel
Write-Host "`n=== Exemple 5: Répertoire actuel ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: Get-Location"
Write-Host "CMD équivalent: cd`n"

# 6. Redirection et piping
Write-Host "`n=== Exemple 6: Redirection et piping ===`n" -ForegroundColor Cyan
Write-Host "PowerShell: Get-ChildItem | Where-Object { `$_.Extension -eq '.py' }"
Write-Host "CMD équivalent: dir | findstr .py`n"

Write-Host "`n=== Rappel: Comment utiliser ce script ===`n" -ForegroundColor Green
Write-Host "Exécutez-le avec: run_ps1.bat scripts\utils\powershell_examples.ps1"
Write-Host "Ce script contourne les restrictions d'exécution de PowerShell.`n" 