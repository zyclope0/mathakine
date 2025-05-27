# Guide des Opérations - Mathakine

Ce guide unifié regroupe les informations essentielles pour l'administration, la maintenance, et le déploiement de l'application Mathakine.

## Administration

### Commandes essentielles

#### Lancement de l'application
```bash
# Lancement standard avec interface graphique
python enhanced_server.py

# Lancement via CLI (recommandé)
python mathakine_cli.py run

# Lancement en mode API uniquement (sans interface graphique)
python mathakine_cli.py run --api-only
```

#### Gestion de la base de données
```bash
# Initialiser/réinitialiser la base de données
python mathakine_cli.py init

# Vérifier la connexion à la base de données
python check_db_connection.py
```

#### Tests et validation
```bash
# Exécuter les tests complets
python -m tests.run_tests --all

# Exécuter des tests spécifiques
python -m tests.run_tests --unit     # Tests unitaires
python -m tests.run_tests --api      # Tests d'API
python -m tests.run_tests --integration  # Tests d'intégration
```

#### Système CI/CD et Qualité

```bash
# Installation du système CI/CD
python scripts/setup_git_hooks.py

# Vérification pre-commit manuelle
python scripts/pre_commit_check.py

# Tests par niveau de criticité
python -m pytest tests/functional/ -v      # Tests critiques (bloquants)
python -m pytest tests/integration/ -v     # Tests importants (non-bloquants)
python -m pytest tests/unit/test_cli.py -v # Tests complémentaires (informatifs)

# Mise à jour automatique des tests après modifications
python scripts/update_tests_after_changes.py --auto-create

# Vérifications de qualité du code
black --check .                    # Formatage
isort --check-only .               # Imports
flake8 .                          # Linting
bandit -r app/                    # Sécurité
safety check                      # Vulnérabilités dépendances
```

### Classification des Tests CI/CD

Le système utilise 3 niveaux de criticité :

#### 🔴 Tests Critiques (BLOQUANTS)
- **Impact** : Bloquent le déploiement
- **Timeout** : 3 minutes
- **Contenu** : Fonctionnels, services core, authentification
- **Commande** : `python -m pytest tests/functional/ -v`

#### 🟡 Tests Importants (NON-BLOQUANTS)
- **Impact** : Avertissement seulement
- **Timeout** : 2 minutes
- **Contenu** : Intégration, modèles, adaptateurs
- **Commande** : `python -m pytest tests/integration/ -v`

#### 🟢 Tests Complémentaires (INFORMATIFS)
- **Impact** : Information seulement
- **Timeout** : 1 minute
- **Contenu** : CLI, initialisation, fonctionnalités secondaires
- **Commande** : `python -m pytest tests/unit/test_cli.py -v`

### Workflow de Développement

1. **Modification du code**
2. **Tests automatiques** (hook pre-commit)
3. **Commit** (si tests critiques passent)
4. **Push** → Pipeline GitHub Actions
5. **Déploiement** (si tous les tests critiques passent)

### Monitoring et Métriques

```bash
# Génération de rapports de couverture
python -m pytest tests/unit/ --cov=app --cov-report=html

# Analyse des métriques de qualité
python scripts/generate_quality_report.py

# Vérification de l'état du système
python scripts/health_check.py
```

### Tester les composants centralisés

```bash
# Tester les constantes
python -c "from app.core.constants import ExerciseTypes, DifficultyLevels; print(f'Types d\'exercices: {ExerciseTypes.ALL_TYPES}\\nNiveaux de difficulté: {DifficultyLevels.ALL_LEVELS}')"

# Tester les messages
python -c "from app.core.messages import SystemMessages; print(f'Message d\'erreur: {SystemMessages.ERROR_EXERCISE_NOT_FOUND}')"

# Tester les requêtes SQL
python -c "from app.db.queries import ExerciseQueries; print(f'Requête de création de table: {ExerciseQueries.CREATE_TABLE}')"
```

### Génération d'exercices

```bash
# Générer un exercice standard via l'API
curl "http://localhost:8000/api/exercises/generate?exercise_type=addition&difficulty=padawan"

# Générer un exercice IA
curl "http://localhost:8000/api/exercises/generate?ai=true&exercise_type=multiplication&difficulty=chevalier"
```

### Vérification de la base de données

```bash
# Examiner la structure de la base de données
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv(); conn = psycopg2.connect(os.environ.get('DATABASE_URL')); cursor = conn.cursor(); cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name;'); [print(row[0]) for row in cursor.fetchall()]; conn.close()"

# Lister les derniers exercices
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv(); conn = psycopg2.connect(os.environ.get('DATABASE_URL')); cursor = conn.cursor(); cursor.execute('SELECT id, title, exercise_type, difficulty FROM exercises ORDER BY id DESC LIMIT 10;'); [print(row) for row in cursor.fetchall()]; conn.close()"
```

## Déploiement

### Prérequis

1. Un compte GitHub
2. Un compte sur la plateforme de déploiement choisie (Render, Heroku ou Fly.io)
3. Git installé sur votre machine locale

### Options de déploiement

#### Option 1: Render (Recommandé)

##### Configuration de la base de données PostgreSQL

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

##### Configuration du service Web

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

#### Option 2: Heroku

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

#### Option 3: Fly.io (Docker)

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

### Vérification du déploiement

Pour vérifier que tout fonctionne correctement :

1. Ouvrez l'URL de votre service déployé
2. Vérifiez que la page d'accueil s'affiche correctement
3. Testez la génération d'exercices
4. Vérifiez que le tableau de bord fonctionne

### Configuration avancée

#### Configuration de l'interface graphique

L'application inclut une interface graphique avec un thème spatial. Pour la personnaliser :

1. **Templates HTML**
   - Les templates se trouvent dans le dossier `/templates`
   - Modifiez `base.html` pour changer la structure commune
   - Personnalisez `home.html`, `exercises.html` et `dashboard.html` selon vos besoins

2. **Styles CSS**
   - Les fichiers CSS sont dans le dossier `/static`
   - `style.css` contient les styles de base
   - `space-theme.css` définit le thème spatial
   - `home-styles.css` est spécifique à la page d'accueil

## Maintenance

### Résolution des problèmes courants

#### Problèmes de base de données

##### Erreur "Unknown PG numeric type: 25"

**Symptôme:** Erreur 500 lors de la suppression d'un exercice avec le message "Unknown PG numeric type: 25".

**Cause:** Incompatibilité entre le driver PostgreSQL et les types de données TEXT/VARCHAR (type 25) lors de l'utilisation de SQLAlchemy ORM pour des opérations complexes.

**Solution:**
1. Utiliser des requêtes SQL directes au lieu de l'ORM pour les opérations critiques
2. Implémenter avec des requêtes paramétrées pour éviter les injections SQL:

```python
from sqlalchemy import text

# Supprimer les tentatives associées
db.execute(text("DELETE FROM attempts WHERE exercise_id = :exercise_id"), 
           {"exercise_id": exercise_id})

# Supprimer l'exercice
db.execute(text("DELETE FROM exercises WHERE id = :exercise_id"), 
           {"exercise_id": exercise_id})

# Valider la transaction
db.commit()
```

##### Erreur "A transaction is already begun on this Session"

**Symptôme:** Erreur 500 avec le message "A transaction is already begun on this Session".

**Cause:** Tentative de démarrer une transaction explicite alors qu'une transaction implicite est déjà en cours.

**Solution:**
1. Ne pas appeler `db.begin()` si vous utilisez un contexte de requête où SQLAlchemy démarre déjà une transaction implicite
2. Comprendre le cycle de vie des transactions dans SQLAlchemy:
   - Les opérations de lecture démarrent implicitement une transaction
   - Les transactions explicites ne sont nécessaires que dans des cas spécifiques

##### Erreur de violation de contrainte de clé étrangère

**Symptôme:** Erreur 500 lors de la suppression d'un exercice avec un message concernant une violation de contrainte de clé étrangère.

**Cause:** Tentative de supprimer un exercice qui a des tentatives associées sans supprimer d'abord ces tentatives.

**Solution:**
1. Définir la relation avec l'option `cascade="all, delete-orphan"`:
```python
attempts = relationship("Attempt", back_populates="exercise", cascade="all, delete-orphan")
```

2. Ou supprimer explicitement les entités liées avant l'entité principale:
```python
# Supprimer d'abord les tentatives
db.query(AttemptModel).filter(AttemptModel.exercise_id == exercise_id).delete()
# Puis supprimer l'exercice
db.delete(exercise)
db.commit()
```

#### Problèmes d'API

##### Redirection en boucle lors de la génération d'exercices

**Symptôme:** Redirection en boucle infinie lors de l'accès à `/api/exercises/generate`.

**Cause:** Redirection incorrecte qui renvoie vers le même endpoint.

**Solution:**
1. Vérifier que les redirections pointent vers les bons endpoints
2. S'assurer que les endpoints de génération redirigent vers des pages différentes
3. Utiliser des codes de statut appropriés (303 See Other pour les redirections POST → GET)

#### Problèmes liés à l'interface utilisateur

##### Boutons de suppression ne fonctionnant pas

**Symptôme:** Cliquer sur le bouton de suppression d'un exercice n'a aucun effet ou provoque des erreurs.

**Cause:** Problèmes dans le gestionnaire d'événements JavaScript ou mauvaise configuration de l'endpoint API.

**Solution:**
1. Vérifier les écouteurs d'événements dans le JavaScript
2. S'assurer que l'URL de l'API est correcte
3. Ajouter des logs dans la console pour déboguer:
```javascript
console.log(`Tentative de suppression de l'exercice ${exerciseId}`);
```

##### Erreurs non affichées à l'utilisateur

**Symptôme:** Les opérations échouent silencieusement sans feedback pour l'utilisateur.

**Cause:** Manque de gestion des erreurs côté client.

**Solution:**
1. Implémenter des gestionnaires d'erreurs pour les appels d'API:
```javascript
.catch(error => {
    console.error('Erreur détaillée:', error);
    alert(`Erreur: ${error.message}`);
});
```

2. Ajouter des alertes ou notifications pour les opérations réussies/échouées

#### Problèmes de déploiement

##### Échec de déploiement sur Render

**Symptôme:** Échec du déploiement avec des erreurs liées à la base de données.

**Cause:** Différences entre l'environnement de développement et de production.

**Solution:**
1. Vérifier les variables d'environnement sur Render
2. S'assurer que la chaîne de connexion PostgreSQL est correcte
3. Exécuter les migrations de base de données avant le déploiement

### Maintenance proactive

#### Surveillance de l'application

1. **Vérification des logs**
   - Les logs sont stockés dans le dossier `logs/`
   - Vérifiez régulièrement `logs/error.log` et `logs/app.log`
   - En production, utilisez la commande `heroku logs --tail` ou l'interface de logs de Render

2. **Validation de la base de données**
   - Exécutez `python check_db_connection.py` pour vérifier la santé de la base de données
   - Utilisez `python scripts/check_db_integrity.py` pour vérifier l'intégrité référentielle

#### Maintenance régulière

1. **Nettoyage des données**
   - Supprimez les exercices inactifs ou archivés après une période prolongée
   - Consolidez les statistiques anciennes
   - Utilisez `python scripts/cleanup_old_data.py --threshold=180` pour nettoyer les données de plus de 180 jours

2. **Mise à jour des dépendances**
   - Vérifiez régulièrement les mises à jour de sécurité
   - Utilisez `pip list --outdated` pour voir les packages qui ont besoin d'être mis à jour
   - Mettez à jour avec `pip install --upgrade package-name`
   - Après mise à jour, exécutez tous les tests pour vérifier la compatibilité

3. **Sauvegardes**
   - Sauvegardez régulièrement la base de données
   - Pour PostgreSQL: `pg_dump -Fc mathakine > backup-$(date +%Y%m%d).dump`
   - Stockez les sauvegardes dans un emplacement sécurisé

## Historique des opérations de maintenance

### Mai 2025

#### Correction du problème d'insertion des données (11/05/2025)

**Problème identifié :** Les données n'étaient pas insérées dans la table `results` lors de la validation des exercices.

**Actions réalisées :**
- Correction de la fonction `submit_answer` dans `enhanced_server.py`
- Ajout de gestion de transactions robuste
- Implémentation de journalisation détaillée
- Documentation complète du problème et de sa solution

**Bénéfices obtenus :**
- Enregistrement correct des réponses aux exercices
- Mise à jour correcte des statistiques utilisateur
- Tableau de bord fonctionnel avec données à jour

#### Correction du tableau de bord (10/05/2025)

**Problème identifié :** Le tableau de bord ne fonctionnait pas correctement car l'endpoint `/api/users/stats` était manquant.

**Actions réalisées :**
- Ajout de l'endpoint manquant dans `enhanced_server.py`
- Implémentation de la fonction `get_user_stats()` pour fournir les données au frontend
- Documentation dans `DASHBOARD_FIX_REPORT.md`

**Bénéfices obtenus :**
- Tableau de bord fonctionnel
- Affichage des statistiques utilisateur
- Visualisation des performances par type d'exercice

#### Nettoyage de la structure du projet (09/05/2025)

**Actions réalisées :**
- Déplacement des fichiers obsolètes et doublons vers des dossiers d'archives dédiés
- Nettoyage du répertoire racine du projet

**Fichiers déplacés vers archives/obsolete :**

| Fichier | Raison | Remplacé par |
|---------|--------|--------------|
| `handle_exercise.py` | Fonctionnalité obsolète | Modules dans `app/services/` |
| `temp_function.py` | Code temporaire non utilisé | Fonctionnalités intégrées dans autres modules |

**Bénéfices obtenus :**
- Réduction de l'encombrement
- Structure de projet plus propre et plus compréhensible
- Maintenance simplifiée
- Préservation de l'historique (archivage vs suppression)

## Actions de maintenance recommandées

1. **Renommage du dossier principal** :
   - Renommer `math-trainer-backend` en `mathakine` pour refléter le nouveau nom du projet
   - Mettre à jour toutes les références au chemin du projet

2. **Consolidation des configurations** :
   - Fusionner les configurations similaires dans les différents environnements
   - Standardiser les noms des variables d'environnement

3. **Nettoyage des tests** :
   - Supprimer les tests redondants dans les différentes suites
   - Améliorer l'organisation des fixtures partagées

4. **Optimisation du code** :
   - Corriger les lignes trop longues dans enhanced_server.py et app/main.py
   - Résoudre les problèmes d'espacement entre fonctions dans divers fichiers
   - Corriger les problèmes d'indentation des lignes de continuation

## Ressources supplémentaires

- [Tech/TRANSACTION_SYSTEM.md](TRANSACTION_SYSTEM.md) - Documentation détaillée du système de transaction
- [Tech/DATABASE_GUIDE.md](DATABASE_GUIDE.md) - Guide complet de la base de données
- [Tech/TESTING_GUIDE.md](TESTING_GUIDE.md) - Guide des tests et validation
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Tutoriel sur les transactions SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [Documentation Render](https://render.com/docs)
- [Documentation Heroku](https://devcenter.heroku.com/)
- [Documentation Fly.io](https://fly.io/docs/)

---

*Ce document consolidé remplace CORRECTIONS_ET_MAINTENANCE.md, MAINTENANCE_ET_NETTOYAGE.md, DEPLOYMENT_GUIDE.md et ADMIN_COMMANDS.md*  
*Dernière mise à jour : 12 juin 2025* 