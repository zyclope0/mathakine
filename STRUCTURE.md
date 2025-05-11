# Structure du Projet Mathakine

## Arborescence du projet

```
./
├── app/                        # Code principal de l'application (API standard)
│   ├── api/                    # Définitions de l'API
│   │   ├── endpoints/          # Endpoints de l'API organisés par ressource
│   │   └── api.py              # Configuration des routes API
│   ├── core/                   # Composants fondamentaux
│   │   ├── config.py           # Configuration de l'application
│   │   ├── logging_config.py   # Configuration centralisée des logs
│   │   └── security.py         # Sécurité et authentification
│   ├── db/                     # Couche d'accès aux données
│   │   ├── base.py             # Configuration de la base de données
│   │   ├── crud/               # Opérations CRUD par modèle
│   │   ├── init_db.py          # Initialisation de la base de données
│   │   └── models/             # Modèles SQLAlchemy
│   ├── models/                 # Modèles de données
│   │   ├── exercise.py         # Modèle d'exercice
│   │   ├── user.py             # Modèle d'utilisateur
│   │   └── logic_challenge.py  # Modèle de défi logique
│   ├── schemas/                # Schémas Pydantic pour validation
│   │   ├── exercise.py         # Schéma d'exercice
│   │   ├── user.py             # Schéma d'utilisateur
│   │   └── logic_challenge.py  # Schéma de défi logique
│   ├── services/               # Services métier
│   │   ├── exercise_service.py # Service de gestion des exercices
│   │   ├── user_service.py     # Service de gestion des utilisateurs
│   │   └── stats_service.py    # Service de statistiques
│   └── main.py                 # Point d'entrée de l'application API standard
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Architecture du système
│   ├── CHANGELOG.md            # Historique des modifications
│   ├── CLEANUP_REPORT.md       # Rapport détaillé de nettoyage
│   ├── CLEANUP_SUMMARY.md      # Résumé des opérations de nettoyage
│   ├── CONTEXT.md              # Contexte actuel du projet
│   ├── DASHBOARD_FIX_REPORT.md # Rapport de correction du tableau de bord
│   ├── DEPLOYMENT_GUIDE.md     # Guide de déploiement
│   ├── GLOSSARY.md             # Glossaire de termes
│   ├── IMPLEMENTATION_PLAN.md  # Plan d'implémentation détaillé
│   ├── LOGGING.md              # Documentation du système de logs
│   ├── LOGIC_CHALLENGES_REQUIREMENTS.md # Exigences pour les défis logiques
│   ├── MAINTENANCE.md          # Procédures de maintenance
│   ├── POSTGRESQL_MIGRATION.md # Guide de migration PostgreSQL
│   ├── PROJECT_STATUS.md       # État actuel du projet
│   ├── PYDANTIC_V2_MIGRATION.md # Guide de migration Pydantic v2
│   ├── TROUBLESHOOTING.md      # Guide de résolution des problèmes
│   ├── UI_GUIDE.md             # Guide de l'interface utilisateur
│   ├── ARCHIVE/                # Ancienne documentation archivée
│   └── validation/             # Documentation de validation
├── logs/                       # Logs centralisés
│   ├── debug.log               # Logs de débogage
│   ├── info.log                # Logs d'information
│   ├── warning.log             # Logs de niveau WARNING
│   ├── error.log               # Logs d'erreurs
│   ├── critical.log            # Logs de niveau CRITICAL
│   ├── uncaught_exceptions.log # Exceptions non gérées
│   └── migration/              # Logs migrés des anciennes versions
├── migrations/                 # Scripts de migration de base de données
├── scripts/                    # Scripts utilitaires
│   ├── check_project.py        # Vérification de la santé du projet
│   ├── fix_style.py            # Correction automatique de problèmes de style courants
│   ├── fix_advanced_style.py   # Correction de problèmes de style avancés
│   ├── cleanup_logs.py         # Nettoyage des anciens logs
│   ├── check_pydantic_validators.py # Vérification des validateurs Pydantic
│   ├── detect_obsolete_files.py # Détection des fichiers obsolètes
│   ├── generate_context.py     # Génération du résumé du contexte du projet
│   ├── migrate_logs.py         # Migration des logs vers le dossier centralisé
│   ├── migrate_to_postgres.py  # Migration vers PostgreSQL
│   ├── migrate_to_render.py    # Migration vers le service Render
│   ├── toggle_database.py      # Basculement entre SQLite et PostgreSQL
│   └── ...                     # Autres scripts
├── services/                   # Services externes
├── static/                     # Fichiers statiques (CSS, JS, images)
├── templates/                  # Templates HTML Jinja2
│   ├── base.html               # Template de base pour toutes les pages
│   ├── home.html               # Page d'accueil
│   ├── exercises.html          # Liste des exercices
│   ├── exercise.html           # Page de résolution d'exercice
│   ├── exercise_detail.html    # Détail d'un exercice
│   ├── dashboard.html          # Tableau de bord
│   └── error.html              # Page d'erreur
├── tests/                      # Tests
│   ├── api/                    # Tests des endpoints API
│   ├── functional/             # Tests fonctionnels
│   ├── integration/            # Tests d'intégration
│   ├── unit/                   # Tests unitaires
│   ├── fixtures/               # Données de test partagées
│   ├── conftest.py             # Configuration centralisée pour pytest
│   ├── run_tests.py            # Script central d'exécution des tests
│   ├── run_tests.bat           # Script Windows pour l'exécution facile des tests
│   ├── TEST_PLAN.md            # Plan de test
│   └── README.md               # Documentation des tests
├── archive/                    # Anciens fichiers archivés (récents)
├── archives/                   # Fichiers obsolètes et archives historiques
│   ├── obsolete/               # Fichiers considérés comme obsolètes
│   ├── sqlite/                 # Anciennes sauvegardes SQLite
│   ├── debug_tools/            # Outils de débogage obsolètes
│   ├── logs/                   # Anciens fichiers de logs
│   └── temp_scripts/           # Scripts temporaires déplacés
├── .env                        # Variables d'environnement locales
├── .env.example                # Exemple de configuration
├── .flake8                     # Configuration de l'outil Flake8
├── .gitignore                  # Fichiers ignorés par Git
├── Dockerfile                  # Configuration Docker
├── Procfile                    # Configuration pour Render
├── README.md                   # Documentation principale
├── STRUCTURE.md                # Ce fichier
├── GETTING_STARTED.md          # Guide de démarrage rapide
├── ai_context_summary.md       # Résumé du contexte pour l'IA
├── enhanced_server.py          # Serveur amélioré avec interface graphique (Starlette)
├── mathakine_cli.py            # Interface en ligne de commande pour l'application
├── setup.cfg                   # Configuration des outils de développement
├── requirements.txt            # Dépendances Python
└── math-trainer-backend/       # Dossier hérité du nom original (en cours de migration)
    └── app/                    # Version secondaire d'app/ (en cours de consolidation)
```

## Composants Principaux

### Modules d'Application (`/app`)

- **API** (`/app/api`): Définit l'interface REST pour interagir avec l'application.
- **Core** (`/app/core`): Contient les composants fondamentaux comme la configuration, la journalisation et la sécurité.
- **DB** (`/app/db`): Assure la communication avec la base de données (SQLite en dev, PostgreSQL en prod).
- **Models** (`/app/models`): Définit les modèles SQLAlchemy pour la base de données.
- **Schemas** (`/app/schemas`): Définit les schémas Pydantic pour la validation des données.
- **Services** (`/app/services`): Implémente la logique métier et les fonctionnalités principales.

### Infrastructure

- **Logs** (`/logs`): Stockage centralisé pour tous les fichiers de journalisation.
- **Migrations** (`/migrations`): Scripts de migration pour la base de données.
- **Services** (`/services`): Configuration et intégration avec services externes.
- **Scripts** (`/scripts`): Outils d'automatisation, maintenance et configuration.
- **Archives** (`/archives` et `/archive`): Stockage des fichiers obsolètes et historiques.

### Interface Utilisateur

- **Static** (`/static`): Fichiers statiques (CSS, JS, images).
- **Templates** (`/templates`): Templates HTML Jinja2 pour le rendu des pages.

### Tests et Assurance Qualité

- **Tests** (`/tests`): Tests organisés par catégories (unitaires, API, intégration, fonctionnels).

## Organisation des Logs

Tous les logs sont désormais centralisés dans le dossier `/logs` avec la structure suivante :

```
logs/
├── debug.log                # Logs de niveau DEBUG
├── info.log                 # Logs de niveau INFO
├── warning.log              # Logs de niveau WARNING
├── error.log                # Logs de niveau ERROR
├── critical.log             # Logs de niveau CRITICAL
├── uncaught_exceptions.log  # Exceptions non gérées
└── migration/               # Logs migrés des anciennes versions
```

Pour plus de détails sur le système de journalisation, consultez [docs/LOGGING.md](docs/LOGGING.md).

## Services et Modules

L'application est organisée en modules fonctionnels suivant une architecture en couches :

1. **Couche API**: Les endpoints REST accessibles publiquement.
2. **Couche Services**: La logique métier et règles de l'application.
3. **Couche Modèles**: La représentation des données et validation.
4. **Couche Persistance**: L'accès et manipulation des données.

Cette structure facilite la maintenance, les tests et l'extension de l'application.

## Routes et Endpoints API

### Routes Web (enhanced_server.py)
- **"/"** : Page d'accueil
- **"/exercises"** : Liste des exercices disponibles
- **"/exercise/{id}"** : Affichage et résolution d'un exercice spécifique
- **"/dashboard"** : Tableau de bord avec statistiques et graphiques de progression

### Endpoints API (enhanced_server.py)
- **"/api/exercises/"** : Liste/création d'exercices
- **"/api/exercises/{id}"** : Détails/modification/suppression d'un exercice
- **"/api/exercises/generate"** : Génération d'exercices
- **"/api/exercises/{id}/submit"** : Soumission de réponses
- **"/api/users/stats"** : Statistiques utilisateur pour le tableau de bord

### API FastAPI (app/main.py)
- **"/api/docs"** : Documentation OpenAPI (Swagger UI)
- **"/api/exercises/"** : Endpoints CRUD pour les exercices
- **"/api/users/"** : Endpoints CRUD pour les utilisateurs
- **"/api/challenges/"** : Endpoints CRUD pour les défis logiques

## Nom du Projet

- **Nom original** : Math Trainer
- **Nom actuel** : Mathakine (avec thématique Star Wars)

### Note sur la double structure

Le projet est actuellement dans une phase de transition où le nom change de "Math Trainer" à "Mathakine". Cette transition est visible dans la structure du projet :
- Le dossier racine est toujours nommé `math-trainer-backend`
- Un sous-dossier `math-trainer-backend/` existe, contenant des éléments en cours de migration
- À terme, tout le contenu devrait être consolidé sous le nom "Mathakine"

## Points Importants

1. **Double structure temporaire** : Le projet est en transition entre l'ancien nom (Math Trainer) et le nouveau (Mathakine), ce qui explique certaines duplications.
2. **Terminologie Star Wars** : Le projet utilise la terminologie Star Wars dans tout le code et la documentation.
3. **Préfixe API** : Suite à une migration, tous les endpoints API utilisent désormais le préfixe `/api/` au lieu de `/api/v1/`.
4. **Système de logs centralisé** : Tous les logs sont stockés dans le dossier `/logs` et utilisent le module centralisé via `app/core/logging_config.py`.
5. **Interface graphique** : Le projet comporte désormais deux modes d'exécution :
   - **Mode API uniquement** : Utilise FastAPI via `app/main.py` 
   - **Mode avec interface graphique** : Utilise Starlette via `enhanced_server.py` (mode par défaut)
6. **Tests et Validation** : 
   - Les tests se trouvent dans le répertoire `tests/` et sont organisés en quatre catégories.
   - Le système d'auto-validation utilise le script central `run_tests.py` et `run_tests.bat`.
7. **Documentation** : 
   - La documentation détaillée se trouve dans `docs/`.
   - Le contexte global du projet est résumé dans `ai_context_summary.md`.
8. **Améliorations récentes**:
   - Correction du tableau de bord avec implémentation de la fonction `get_user_stats` et l'endpoint `/api/users/stats`
   - Scripts de correction de style (`fix_style.py` et `fix_advanced_style.py`)
   - Organisation améliorée des archives et fichiers temporaires
   - Renforcement de la compatibilité avec PostgreSQL pour le déploiement

## Interface Graphique

Le projet utilise une interface graphique basée sur Starlette (via enhanced_server.py) qui inclut :

1. **Pages principales** :
   - Page d'accueil (`/`)
   - Liste des exercices (`/exercises`)
   - Détail d'un exercice (`/exercise/{id}`)
   - Tableau de bord (`/dashboard`)
   - Page d'erreur (`/error`)

2. **Comment lancer l'application** :
   ```bash
   # Lancer avec l'interface graphique (par défaut)
   python mathakine_cli.py run
   
   # Lancer uniquement l'API sans interface graphique
   python mathakine_cli.py run --api-only
   ```

3. **Templates** : 
   - L'interface utilise des templates Jinja2 dans le dossier `/templates`
   - Les styles CSS et autres ressources statiques sont dans le dossier `/static`

Pour plus de détails sur l'interface, consultez [docs/UI_GUIDE.md](docs/UI_GUIDE.md).

## Système de Test Optimisé

Le système de test a été restructuré et optimisé :

1. **Script central** : `run_tests.py` comme point d'entrée principal
2. **Exécution facilitée** : Script `run_tests.bat` pour Windows
3. **Structure modulaire** : Tests organisés en catégories (unitaires, API, intégration, fonctionnels)
4. **Fixtures partagées** : Configuration de test centralisée dans `conftest.py`
5. **Rapports améliorés** : Génération de rapports dans plusieurs formats

## Scripts d'utilitaires

Le dossier `scripts/` contient de nombreux outils essentiels pour la maintenance et le développement :

1. **Vérification de qualité** : 
   - `check_project.py` - Analyse complète de la santé du projet
   - `fix_style.py` - Correction automatique des problèmes de style courants
   - `fix_advanced_style.py` - Correction des problèmes plus complexes

2. **Gestion de base de données** :
   - `toggle_database.py` - Basculement entre SQLite et PostgreSQL
   - `migrate_to_postgres.py` - Migration des données vers PostgreSQL
   - `migrate_to_render.py` - Migration vers le service Render

3. **Maintenance** :
   - `detect_obsolete_files.py` - Détection des fichiers obsolètes
   - `cleanup_logs.py` - Nettoyage des anciens logs
   - `move_obsolete_files.py` - Déplacement des fichiers obsolètes vers l'archive

4. **Documentation** :
   - `generate_context.py` - Génération du résumé du contexte du projet
   - `consolidate_docs.py` - Consolidation des documents qui se chevauchent
   - `cleanup_redundant_docs.py` - Nettoyage des documents redondants

## Évolution Future

Si le projet doit être restructuré à l'avenir, il est recommandé de :
1. Finaliser la transition vers le nom "Mathakine" en renommant le dossier racine
2. Consolider les éléments du dossier `math-trainer-backend/` dans la structure principale
3. Mettre à jour toutes les références pour utiliser exclusivement le nouveau nom
4. Continuer d'améliorer le style du code avec les scripts existants

## Documentation Principale

- **README.md** : Documentation générale du projet
- **GETTING_STARTED.md** : Guide de démarrage rapide
- **STRUCTURE.md** : Ce document (structure du projet)
- **ai_context_summary.md** : Résumé du contexte pour l'IA
- **docs/ARCHITECTURE.md** : Architecture détaillée du système
- **docs/PROJECT_STATUS.md** : État actuel du projet
- **docs/UI_GUIDE.md** : Guide de l'interface utilisateur 