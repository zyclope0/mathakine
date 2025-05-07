@echo off
setlocal enabledelayedexpansion

echo ===== DEPLOIEMENT MATHAKINE =====
echo.

:: Vérifier les changements Git
echo [1/5] Vérification des changements Git...
git status

:: Demander confirmation pour commit
set /p COMMIT_MSG="Message de commit (ou 'skip' pour passer): "
if not "%COMMIT_MSG%"=="skip" (
    echo [2/5] Ajout des fichiers modifiés...
    git add .
    
    echo [3/5] Création du commit...
    git commit -m "%COMMIT_MSG%"
    
    echo [4/5] Push vers GitHub...
    git push
) else (
    echo Commit ignoré.
)

:: Choix de la plateforme de déploiement
echo.
echo [5/5] Déploiement...
echo Sélectionnez la plateforme de déploiement:
echo 1. Render (recommandé)
echo 2. Heroku
echo 3. Fly.io (Docker)
echo 4. Annuler le déploiement

set /p CHOICE="Votre choix (1-4): "

if "%CHOICE%"=="1" (
    echo Déploiement sur Render...
    echo Ouvrez https://dashboard.render.com/ pour finaliser le déploiement
    start https://dashboard.render.com/
) else if "%CHOICE%"=="2" (
    echo Déploiement sur Heroku...
    echo Vérifiez que l'outil Heroku CLI est installé
    heroku login
    heroku create mathakine || echo Le projet existe déjà
    git push heroku master
) else if "%CHOICE%"=="3" (
    echo Déploiement sur Fly.io...
    echo Vérifiez que l'outil flyctl est installé
    fly auth login
    fly launch --name mathakine || echo Le projet existe déjà
    fly deploy
) else (
    echo Déploiement annulé.
)

echo.
echo Déploiement terminé !
echo. 