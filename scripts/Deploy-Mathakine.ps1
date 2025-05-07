#Requires -Version 5.0

Write-Host "===== DEPLOIEMENT MATHAKINE =====" -ForegroundColor Cyan
Write-Host

# Vérifier les changements Git
Write-Host "[1/5] Vérification des changements Git..." -ForegroundColor Yellow
git status

# Demander confirmation pour commit
$CommitMsg = Read-Host "Message de commit (ou 'skip' pour passer)"
if ($CommitMsg -ne "skip") {
    Write-Host "[2/5] Ajout des fichiers modifiés..." -ForegroundColor Yellow
    git add .
    
    Write-Host "[3/5] Création du commit..." -ForegroundColor Yellow
    git commit -m "$CommitMsg"
    
    Write-Host "[4/5] Push vers GitHub..." -ForegroundColor Yellow
    git push
} else {
    Write-Host "Commit ignoré." -ForegroundColor Gray
}

# Choix de la plateforme de déploiement
Write-Host
Write-Host "[5/5] Déploiement..." -ForegroundColor Yellow
Write-Host "Sélectionnez la plateforme de déploiement:"
Write-Host "1. Render (recommandé)"
Write-Host "2. Heroku"
Write-Host "3. Fly.io (Docker)"
Write-Host "4. Annuler le déploiement"

$Choice = Read-Host "Votre choix (1-4)"

switch ($Choice) {
    "1" {
        Write-Host "Déploiement sur Render..." -ForegroundColor Green
        Write-Host "Ouvrez https://dashboard.render.com/ pour finaliser le déploiement"
        Start-Process "https://dashboard.render.com/"
    }
    "2" {
        Write-Host "Déploiement sur Heroku..." -ForegroundColor Green
        Write-Host "Vérifiez que l'outil Heroku CLI est installé"
        heroku login
        try {
            heroku create mathakine
        } catch {
            Write-Host "Le projet existe déjà" -ForegroundColor Yellow
        }
        git push heroku master
    }
    "3" {
        Write-Host "Déploiement sur Fly.io..." -ForegroundColor Green
        Write-Host "Vérifiez que l'outil flyctl est installé"
        fly auth login
        try {
            fly launch --name mathakine
        } catch {
            Write-Host "Le projet existe déjà" -ForegroundColor Yellow
        }
        fly deploy
    }
    default {
        Write-Host "Déploiement annulé." -ForegroundColor Red
    }
}

Write-Host
Write-Host "Déploiement terminé !" -ForegroundColor Green
Write-Host 