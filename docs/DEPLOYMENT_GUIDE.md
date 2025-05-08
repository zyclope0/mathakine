# Guide de Déploiement - Mathakine (API Rebelle)

Ce guide vous explique comment déployer l'application Mathakine pour la rendre disponible en ligne.

## Prérequis

1. Un compte GitHub
2. Un compte sur la plateforme de déploiement choisie (Render, Heroku ou Fly.io)
3. Git installé sur votre machine locale

## Options de Déploiement

### Option 1: Render (Recommandé pour démarrer)

Render offre un niveau gratuit généreux et une configuration simple, idéale pour les projets en phase alpha.

#### Configuration de la base de données PostgreSQL

1. **Création de la base de données**
   - Dans le tableau de bord Render, cliquez sur "New" et sélectionnez "PostgreSQL"
   - Configurez la base de données :
     - Nom : "Mathakine" (ou autre nom descriptif)
     - Base de données : "mathakine_test"
     - Utilisateur : laissez le nom proposé par défaut
     - Région : choisissez la plus proche de vos utilisateurs
     - Plan : "Free" est suffisant pour débuter

2. **Migration des données**
   - Notez les informations de connexion fournies
   - Utilisez le script de migration pour transférer vos données :
     ```
     python scripts/migrate_to_render.py
     ```
   - En cas de problème de permissions, utilisez pgAdmin pour exécuter :
     ```sql
     DROP SCHEMA public CASCADE;
     CREATE SCHEMA public;
     ```

#### Configuration du service Web

1. **Création du service**
   - Créez un compte sur [Render](https://render.com)
   - Connectez votre compte GitHub
   - Cliquez sur "New Web Service"
   - Sélectionnez votre dépôt "mathakine"
   - Donnez un nom au service (ex: "mathakine")
   - Laissez le Runtime sur "Python"
   - Définissez la commande de démarrage: `bash scripts/start_render.sh`
   - Laissez le plan sur "Free"

2. **Variables d'environnement**
   - Allez dans "Environment"
   - Ajoutez les variables suivantes:
     - `MATH_TRAINER_PROFILE`: prod
     - `DATABASE_URL`: [External Database URL fournie par Render]
     - `OPENAI_API_KEY`: votre-clé-api-openai (si vous utilisez les fonctionnalités IA)

3. **Déploiement**
   - Cliquez sur "Create Web Service"
   - Le déploiement se lance automatiquement

### Option 2: Heroku

1. **Installation de Heroku CLI**
   ```
   # Windows
   winget install -e --id Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login et création de l'application**
   ```
   heroku login
   heroku create mathakine
   ```

3. **Configuration de PostgreSQL**
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Configuration**
   ```
   heroku config:set MATH_TRAINER_PROFILE=prod
   heroku config:set OPENAI_API_KEY=votre-clé-api-openai
   ```

5. **Déploiement**
   ```
   git push heroku master
   ```

6. **Migration des données**
   ```
   heroku pg:psql < scripts/schema.sql
   ```

### Option 3: Fly.io (Docker)

1. **Installation de flyctl**
   ```
   # Windows PowerShell (exécuter en administrateur)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS ou Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Authentification et déploiement**
   ```
   fly auth login
   fly launch --name mathakine
   ```

3. **Configuration**
   - Répondez aux questions interactives 
   - Ajoutez les secrets:
     ```
     fly secrets set MATH_TRAINER_PROFILE=prod OPENAI_API_KEY=votre-clé-api-openai
     ```

4. **Déploiement**
   ```
   fly deploy
   ```

## Utilisation des Scripts de Déploiement

Nous avons créé des scripts pour automatiser le processus:

### Windows (Batch)
```batch
scripts/deploy.bat
```

### Windows (PowerShell)
```powershell
./scripts/Deploy-Mathakine.ps1
```

Ces scripts:
1. Vérifient les changements Git
2. Vous demandent un message de commit
3. Poussent les changements vers GitHub
4. Vous guident dans le déploiement sur la plateforme de votre choix

## Mises à Jour et CI/CD

Pour les mises à jour, il suffit de:

1. Faire des commits de vos changements
2. Pousser vers GitHub (`git push`)

Pour Render et Heroku, le déploiement se fera automatiquement après le push.

## Vérification de la base de données

Pour vérifier la connexion à votre base de données et l'état des tables :

```
python check_db_connection.py
```

Ce script affichera le type de base de données, la version, et listera toutes les tables avec leur nombre d'enregistrements.

## Problèmes Courants

### Erreur de déploiement sur Render
- Vérifiez les logs dans le tableau de bord Render
- Assurez-vous que les dépendances sont correctement listées dans `requirements.txt`
- Vérifiez que `email-validator` est bien installé (requis pour Pydantic)

### Erreur de connexion à la base de données PostgreSQL
- Vérifiez que la variable `DATABASE_URL` est correctement configurée
- Assurez-vous que la base de données est accessible depuis le service web
- Utilisez le script `check_db_connection.py` pour diagnostiquer les problèmes

### Erreur H10 sur Heroku
- Vérifiez que le Procfile est correctement configuré
- Vérifiez les logs avec `heroku logs --tail`

### Problèmes avec Fly.io
- Vérifiez que le Dockerfile est correctement configuré
- Consultez les logs avec `fly logs`

## Migration vers la Production

Une fois que vous êtes prêt à passer en production:

1. Envisagez de migrer vers un plan payant pour de meilleures performances
2. Configurez un nom de domaine personnalisé
3. Mettez en place des sauvegardes de base de données
4. Configurez la surveillance et les alertes

Pour des questions ou problèmes, consultez la documentation de la plateforme choisie ou ouvrez une issue sur GitHub. 