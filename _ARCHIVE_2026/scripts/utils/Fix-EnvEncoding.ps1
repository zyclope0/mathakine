# Script pour corriger l'encodage du fichier env.example et .env.example
# en UTF-8 avec les accents correctement affichés

# Déterminer le chemin du script et du répertoire racine
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Chemins des fichiers
$EnvExampleSrc = Join-Path $ScriptDir "env.example.corrected.txt"
$EnvExampleUtil = Join-Path $ScriptDir "env.example"
$EnvExampleDest = Join-Path $ProjectRoot ".env.example"

# Écrire un nouveau fichier avec l'encodage UTF-8
$envContent = @"
# Math Trainer - Fichier d'environnement exemple
# Copiez ce fichier vers .env à la racine du projet et ajustez les valeurs selon votre environnement

# Configuration du serveur
MATH_TRAINER_DEBUG=true                # Active/désactive le mode debug (true/false)
MATH_TRAINER_PORT=8081                 # Port du serveur web
MATH_TRAINER_LOG_LEVEL=INFO            # Niveau de logs (DEBUG, INFO, WARNING, ERROR)
MATH_TRAINER_TEST_MODE=false           # Active/désactive le mode test (true/false)

# Base de données
DATABASE_URL=sqlite:///./math_trainer.db # URL de connexion à la base de données

# Intégration OpenAI (optionnel)
OPENAI_API_KEY=votre_clé_api_ici       # Clé API OpenAI (ne pas committer ce fichier avec une vraie clé)

# Profil d'environnement
MATH_TRAINER_PROFILE=dev               # Profil actif (dev, test, prod)

# Variables spécifiques aux tests
# TEST_DATABASE_URL=sqlite:///./math_trainer_test.db  # Base de données dédiée aux tests

# Variables spécifiques à la production
# ALLOWED_HOSTS=mathtrainer.example.com,localhost  # Hôtes autorisés en production
# SESSION_COOKIE_SECURE=true                       # Cookies sécurisés en production
"@

try {
    # Écrire le contenu dans le fichier source avec encodage UTF-8
    [System.IO.File]::WriteAllText($EnvExampleSrc, $envContent, [System.Text.Encoding]::UTF8)
    
    # Copier vers les fichiers cibles
    Copy-Item -Path $EnvExampleSrc -Destination $EnvExampleUtil -Force
    Copy-Item -Path $EnvExampleSrc -Destination $EnvExampleDest -Force
    
    Write-Host "Fichiers env.example et .env.example mis à jour avec l'encodage UTF-8" -ForegroundColor Green
    
    # Supprimer le fichier temporaire
    Remove-Item -Path $EnvExampleSrc -Force
    
} catch {
    Write-Host "Erreur lors de la correction de l'encodage: $_" -ForegroundColor Red
    exit 1
}

# Vérifier l'encodage du fichier .env.example
$fileEncoding = [System.Text.Encoding]::UTF8
$fileContent = [System.IO.File]::ReadAllText($EnvExampleDest, $fileEncoding)

# Vérifier si les caractères accentués sont correctement affichés
if ($fileContent -like "*désactive*" -and $fileContent -like "*données*") {
    Write-Host "Vérification réussie : Les caractères accentués sont correctement encodés" -ForegroundColor Green
} else {
    Write-Host "Attention : Possible problème d'encodage des caractères accentués" -ForegroundColor Yellow
}

exit 0 