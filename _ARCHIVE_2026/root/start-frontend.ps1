# Script PowerShell pour démarrer le frontend depuis la racine du projet

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Démarrage du frontend Mathakine..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Chercher npm.cmd dans plusieurs emplacements (évite problème ExecutionPolicy)
$npmCmd = $null

# 1. Essayer npm.cmd dans le PATH (priorité à .cmd pour éviter ExecutionPolicy)
$npmCmdPath = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($npmCmdPath) {
    $npmCmd = "npm.cmd"
}

# 2. Essayer dans Program Files
if (-not $npmCmd -and (Test-Path "C:\Program Files\nodejs\npm.cmd")) {
    $npmCmd = "C:\Program Files\nodejs\npm.cmd"
}

# 3. Essayer dans AppData
if (-not $npmCmd -and (Test-Path "$env:APPDATA\npm\npm.cmd")) {
    $npmCmd = "$env:APPDATA\npm\npm.cmd"
}

# 4. Essayer avec nvm-windows
if (-not $npmCmd -and (Test-Path "$env:USERPROFILE\.nvm")) {
    $nvmPath = Get-ChildItem "$env:USERPROFILE\.nvm" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($nvmPath) {
        $npmPath = Get-ChildItem "$($nvmPath.FullName)\*\npm.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($npmPath) {
            $npmCmd = $npmPath.FullName
        }
    }
}

# 5. Dernier recours : essayer npm (peut être npm.ps1, mais on essaie quand même)
if (-not $npmCmd) {
    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        # Si c'est npm.ps1, utiliser cmd.exe pour le lancer
        if ($npmPath.Source -like "*.ps1") {
            Write-Host "⚠️  Attention: npm.ps1 détecté. Utilisation de cmd.exe pour contourner ExecutionPolicy..." -ForegroundColor Yellow
            $npmCmd = "cmd.exe /c npm"
        } else {
            $npmCmd = "npm"
        }
    }
}

if (-not $npmCmd) {
    Write-Host "❌ ERREUR: npm n'est pas trouvé" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions possibles:" -ForegroundColor Yellow
    Write-Host "  1. Installer Node.js depuis https://nodejs.org/" -ForegroundColor White
    Write-Host "  2. Redémarrer le terminal après installation" -ForegroundColor White
    Write-Host "  3. Vérifier que Node.js est dans le PATH" -ForegroundColor White
    Write-Host ""
    Write-Host "Vous pouvez aussi lancer manuellement:" -ForegroundColor Cyan
    Write-Host "  cd frontend" -ForegroundColor Gray
    Write-Host "  npm run dev" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

# Aller dans le dossier frontend
Set-Location frontend

Write-Host "📍 Répertoire: $(Get-Location)" -ForegroundColor Green
Write-Host "🚀 Lancement du serveur de développement..." -ForegroundColor Green
Write-Host "   Frontend accessible sur: http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend attendu sur: http://localhost:10000" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur de développement
& $npmCmd run dev

