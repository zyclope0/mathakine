# Script pour créer un fichier .env.example à la racine du projet

# Déterminer le chemin du script et du répertoire racine
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Source et destination
$SourceFile = Join-Path $ScriptDir "env.example"
$DestFile = Join-Path $ProjectRoot ".env.example"

try {
    # Copier le fichier
    Copy-Item -Path $SourceFile -Destination $DestFile -Force
    
    # Vérifier si le fichier a bien été créé
    if (Test-Path $DestFile) {
        Write-Host "Fichier .env.example créé avec succès à la racine du projet" -ForegroundColor Green
    } else {
        Write-Host "Erreur: Le fichier n'a pas été créé correctement" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Erreur lors de la création du fichier .env.example: $_" -ForegroundColor Red
    exit 1
}

exit 0 