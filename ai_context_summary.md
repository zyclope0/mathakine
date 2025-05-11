# Compréhension du projet Mathakine (anciennement Math Trainer)

## Vue d'ensemble
Mathakine est une application éducative backend pour un site d'entraînement mathématique interactif destiné aux enfants, spécialement adapté pour les enfants autistes, avec une thématique Star Wars. Anciennement nommée "Math Trainer", elle a été entièrement renommée et restructurée pour offrir une expérience cohérente et immersive où les enfants sont des "Padawans des mathématiques" apprenant à maîtriser la "Force des nombres".

## Historique et renommage
- Le projet était originellement nommé "Math Trainer"
- Un renommage complet vers "Mathakine" a été effectué
- La thématique Star Wars a été renforcée et profondément intégrée dans le code, les interfaces et la documentation
- Une restructuration complète a été réalisée pour améliorer la maintenabilité, avec réorganisation des tests et nettoyage des fichiers obsolètes

## Architecture technique
- **Double architecture backend**:
  - **FastAPI (app/main.py)** - API REST pure pour applications externes et futures frontends
  - **Starlette (enhanced_server.py)** - Version avec interface utilisateur web intégrée
- **Base de données**: 
  - PostgreSQL pour production (sur Render)
  - SQLite pour développement local (avec scripts de migration)
- **Structure du code**:
  - Architecture MVC moderne avec séparation claire entre modèles/schémas/services/API
  - API REST documentée via Swagger/OpenAPI (appelée "Les Holocrons" dans la terminologie du projet)
  - Tests répartis en 4 catégories: unitaires, API, intégration, fonctionnels
  - **Centralisation des constantes et messages** pour améliorer la maintenabilité
  - **Système de variables CSS** pour une apparence cohérente
  - **Requêtes SQL centralisées** pour faciliter la maintenance et éviter la duplication
- **Outils de gestion**:
  - Interface CLI complète (mathakine_cli.py) avec 6 commandes principales
  - Scripts de migration et de gestion de base de données
  - Outils de validation automatisée
- **Déploiement**:
  - Support Docker avec Dockerfile optimisé
  - Configuration pour déploiement sur Render
  - Compatibilité avec Python 3.13
  - Exemple de fichier .env pour la configuration des environnements

## Composants clés

### 1. enhanced_server.py
Le serveur principal combinant l'interface utilisateur web et l'API, construit avec Starlette pour une meilleure compatibilité Python 3.13.

**Fonctionnalités principales**:
- Interface web complète avec templates HTML et CSS
- API REST simple avec endpoints JSON
- Génération d'exercices (simple et IA)
- Soumission de réponses et feedback
- Tableau de bord avec statistiques
- Gestion des exercices (liste, détails, suppression)

**Routes principales**:
- Pages HTML: "/", "/exercises", "/dashboard", "/exercise/{id}"
- API: "/api/exercises/", "/api/exercises/{id}", "/api/exercises/generate", "/api/exercises/{id}/submit", "/api/users/stats"

**Mécanismes clés**:
- Normalisation des types d'exercices et difficultés
- Génération pseudo-IA d'exercices (avec tag TEST-ZAXXON)
- Gestion des choix en format JSON
- Statistiques par type d'exercice et niveau
- Suivi de progression via des graphiques de performance

### 2. app/ (Application FastAPI)
Contient l'implémentation API REST pure utilisant FastAPI, organisée selon les meilleures pratiques.

**Structure**:
- **api/endpoints/**: Endpoints REST (exercises.py, users.py, challenges.py, auth.py)
- **models/**: Modèles SQLAlchemy 2.0 (exercise.py, user.py, attempt.py, progress.py, logic_challenge.py)
- **schemas/**: Schémas Pydantic 2.0 pour validation (exercise.py, progress.py, etc.)
- **services/**: Logique métier (exercise_service.py, auth_service.py, etc.)
- **core/**: Configuration et utilitaires
  - **config.py**: Configuration principale de l'application
  - **constants.py**: Toutes les constantes centralisées (types, niveaux, limites)
  - **messages.py**: Messages et textes centralisés pour l'interface et les API
  - **logging_config.py**: Configuration du système de journalisation centralisée
    
    **Système de journalisation**:
    - **Architecture**: Système centralisé basé sur loguru avec rotation et compression automatiques
    - **Niveaux**: DEBUG, INFO, WARNING, ERROR, CRITICAL dans des fichiers séparés
    - **Utilisation**: Via `from app.core.logging_config import get_logger`
    - **Format standardisé**: Horodatage, niveau, module, ligne, message
    - **Rotation**: Fichiers divisés à 10-20 Mo et compressés en ZIP
    - **Conservation**: 30-60 jours selon l'importance des logs
    - **Contexte**: Support pour l'ajout de métadonnées via `logger.bind()`
    - **Capture d'exceptions**: Enregistrement automatique des stack traces
    - **Importance**: Essentiel pour le débogage, la surveillance et l'analyse des performances
  - **db/**: Accès et initialisation de base de données
  - **init_db.py**: Initialisation de la base de données
  - **base.py**: Configuration de base
  - **queries.py**: Requêtes SQL centralisées

**Fonctionnalités avancées**:
- Support complet CRUD pour toutes les entités
- Pagination, filtrage et tri avancés
- Gestion des erreurs standardisée
- Modèles pour défis logiques avancés (10-15 ans)
- Validation des données avec Pydantic 2.0

### 3. templates/ et static/
Dossiers contenant les templates HTML et les fichiers statiques (CSS, JS) pour l'interface utilisateur web.

**Templates principaux**:
- **base.html**: Template de base avec layout, navigation et thème Star Wars
- **home.html**: Page d'accueil avec hero section optimisée suivant les best practices UI:
  - Layout horizontal avec contenu à gauche et visuel à droite
  - Affichage de statistiques clés (nombre d'exercices, niveaux, possibilités)
  - Unique CTA principal pour réduire les redondances avec la navigation
  - Design responsive adaptatif pour desktop et mobile
  - Animation spatiale avec objet céleste animé par CSS
- **exercise.html**: Interface pour résoudre un exercice spécifique
- **exercises.html**: Liste et gestion des exercices avec filtres
- **dashboard.html**: Interface du tableau de bord avec statistiques et graphiques
- **error.html**: Page d'erreur standardisée
- **exercise_detail.html**: Détails d'un exercice spécifique

**CSS et assets**:
- **variables.css**: Variables CSS centralisées (couleurs, espacements, typographie)
- **style.css**: Styles globaux avec thème Star Wars
- **home-styles.css**: Styles spécifiques à la page d'accueil
- **space-theme.css**: Éléments de thème spatial Star Wars

### 4. mathakine_cli.py
Interface en ligne de commande complète pour administrer et gérer l'application.

**Commandes disponibles**:
- **run**: Démarrer l'application (avec/sans interface graphique)
- **init**: Initialiser/réinitialiser la base de données
- **test**: Exécuter différents types de tests
- **validate**: Valider l'application
- **shell**: Démarrer un shell Python avec contexte d'application
- **setup**: Configurer l'environnement de développement

### 5. Documentation
Ensemble complet de documents détaillant tous les aspects du projet.

**Documentation principale**:
- **README.md**: Documentation générale
- **STRUCTURE.md**: Structure détaillée du projet
- **ARCHITECTURE.md**: Architecture détaillée du système
- **PROJECT_STATUS.md**: État actuel et planification
- **IMPLEMENTATION_PLAN.md**: Plan d'implémentation détaillé
- **UI_GUIDE.md**: Guide de l'interface graphique
- **POSTGRESQL_MIGRATION.md**: Guide de migration vers PostgreSQL
- **CHANGELOG.md**: Historique des modifications
- **CORRECTIONS_ET_MAINTENANCE.md**: Documentation des corrections et problèmes résolus
- **MAINTENANCE_ET_NETTOYAGE.md**: Résumé des opérations de nettoyage
- **LOGGING.md**: Guide du système de journalisation centralisé
- **PYDANTIC_V2_MIGRATION.md**: Documentation de la migration vers Pydantic v2

**Rôle de la documentation de migration**:
- **Valeur historique**: Documentation des décisions techniques importantes
- **Référence pour les développeurs**: Aide les nouveaux développeurs à comprendre les choix d'architecture
- **Guide de maintenance**: Facilite la compréhension de patterns utilisés dans le code actuel
- **Résolution de problèmes**: Source d'information pour diagnostiquer les problèmes liés aux migrations
- **Configuration des environnements**: Instructions pour configurer différents environnements (développement/production)

La documentation complète est organisée dans la **TABLE_DES_MATIERES.md** qui sert de point d'entrée vers tous les documents.

### 6. Scripts d'utilitaires
Le dossier scripts/ contient des outils essentiels pour la maintenance et le développement du projet.

**Scripts principaux**:
- **check_project.py**: Vérification de la santé du projet (style, syntaxe, imports)
- **fix_style.py**: Correction automatique des problèmes de style courants
- **fix_advanced_style.py**: Correction des problèmes de style avancés
- **toggle_database.py**: Basculement entre SQLite et PostgreSQL
- **migrate_to_postgres.py**: Migration des données vers PostgreSQL
- **generate_context.py**: Génération du contexte du projet

### 7. Tests
Le dossier tests/ contient des tests organisés par catégories avec une structure optimisée.

**Structure des tests**:
- **unit/**: Tests unitaires des composants individuels
- **api/**: Tests des endpoints API
- **integration/**: Tests d'intégration entre les composants
- **functional/**: Tests fonctionnels de l'application complète
- **fixtures/**: Données de test partagées
- **conftest.py**: Configuration centralisée pour pytest
- **run_tests.py**: Script central d'exécution des tests
- **run_tests.bat**: Script Windows pour l'exécution facile des tests

## Niveaux de difficulté (Thème Star Wars)
- **Initié**: Niveau facile pour débutants (nombres 1-10)
- **Padawan**: Niveau intermédiaire (nombres 10-50)
- **Chevalier**: Niveau difficile (nombres 50-100)
- **Maître**: Niveau expert (nombres 100-500)

## Types d'exercices
- **Addition**: Opérations d'addition adaptées au niveau
- **Subtraction** (Soustraction): Opérations de soustraction avec valeurs positives
- **Multiplication**: Tables de multiplication adaptées au niveau
- **Division**: Divisions sans reste adaptées au niveau

## Fonctionnalités majeures

### Génération d'exercices
- **Génération algorithmique**: Exercices générés avec paramètres prédéfinis selon le niveau
- **Génération pseudo-IA**: Exercices avec thème Star Wars et libellés plus élaborés
- **Personnalisation**: Filtres par type d'exercice et niveau de difficulté
- **Interface utilisateur**: Boutons distincts pour génération standard et IA

### Résolution d'exercices
- **Présentation claire**: Question en haut, choix de réponses en grille 2x2
- **Feedback immédiat**: Message de succès/échec et explication en cas d'erreur
- **Navigation fluide**: Passage facile à l'exercice suivant
- **Validation et enregistrement**: Stockage des résultats pour analyse

### Suivi de progression
- **Tableau de bord**: Vue d'ensemble des performances et statistiques
- **Statistiques par type**: Répartition des résultats par opération mathématique
- **Graphiques visuels**: Représentation visuelle des performances
- **Activité récente**: Historique des dernières interactions
- **Évolution temporelle**: Graphique montrant la progression au fil du temps

### API REST complète
- **Documentation OpenAPI**: Interface Swagger pour explorer et tester l'API
- **Endpoints CRUD**: Accès complet à toutes les entités
- **Validation robuste**: Sécurisation des entrées avec Pydantic
- **Gestion des erreurs**: Réponses standardisées et informatives

### Migration et compatibilité base de données
- **PostgreSQL pour production**: Haute performance et scalabilité
- **SQLite pour développement**: Facilité de développement local
- **Scripts de migration**: Transfert fluide entre les deux systèmes
- **Normalisation des données**: Cohérence des types et formats

## Modèle de données

### Schéma détaillé de la base de données

#### Table: exercises
```
[PK] id - SERIAL
[ ] title - VARCHAR(255) (NOT NULL)
[ ] creator_id - INTEGER (NULL)
[ ] exercise_type - VARCHAR(50) (NOT NULL)
[ ] difficulty - VARCHAR(50) (NOT NULL)
[ ] tags - VARCHAR(255)
[ ] question - TEXT (NOT NULL)
[ ] correct_answer - VARCHAR(255) (NOT NULL)
[ ] choices - JSON
[ ] explanation - TEXT
[ ] hint - TEXT
[ ] image_url - VARCHAR(255)
[ ] audio_url - VARCHAR(255)
[ ] is_active - BOOLEAN
[ ] is_archived - BOOLEAN
[ ] ai_generated - BOOLEAN
[ ] view_count - INTEGER
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
```

#### Table: results
```
[PK] id - SERIAL
[ ] exercise_id - INTEGER (NOT NULL)
[ ] user_id - INTEGER
[ ] session_id - VARCHAR(255)
[ ] is_correct - BOOLEAN (NOT NULL)
[ ] created_at - TIMESTAMP WITH TIME ZONE
```

#### Table: user_stats
```
[PK] id - SERIAL
[ ] exercise_type - VARCHAR(50) (NOT NULL)
[ ] difficulty - VARCHAR(50) (NOT NULL)
[ ] total_attempts - INTEGER
[ ] correct_attempts - INTEGER
[ ] last_updated - TIMESTAMP WITH TIME ZONE
```

#### Table: users
```
[PK] id - SERIAL
[ ] username - VARCHAR(255) (NOT NULL)
[ ] email - VARCHAR(255) (NOT NULL)
[ ] hashed_password - VARCHAR(255) (NOT NULL)
[ ] full_name - VARCHAR(255)
[ ] role - ENUM (user, admin, teacher)
[ ] is_active - BOOLEAN
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
[ ] grade_level - INTEGER
[ ] learning_style - VARCHAR(255)
[ ] preferred_difficulty - VARCHAR(255)
[ ] preferred_theme - VARCHAR(255)
[ ] accessibility_settings - VARCHAR(255)
```

#### Table: attempts
```
[PK] id - SERIAL
[ ] user_id - INTEGER (NOT NULL)
[ ] exercise_id - INTEGER (NOT NULL)
[ ] user_answer - VARCHAR(255) (NOT NULL)
[ ] is_correct - BOOLEAN (NOT NULL)
[ ] time_spent - REAL
[ ] attempt_number - INTEGER
[ ] hints_used - INTEGER
[ ] device_info - VARCHAR(255)
[ ] created_at - TIMESTAMP WITH TIME ZONE
```

#### Table: progress
```
[PK] id - SERIAL
[ ] user_id - INTEGER (NOT NULL)
[ ] exercise_type - VARCHAR(255) (NOT NULL)
[ ] difficulty - VARCHAR(255) (NOT NULL)
[ ] total_attempts - INTEGER
[ ] correct_attempts - INTEGER
[ ] average_time - REAL
[ ] completion_rate - REAL
[ ] streak - INTEGER
[ ] highest_streak - INTEGER
[ ] mastery_level - INTEGER
[ ] awards - JSON
[ ] strengths - VARCHAR(255)
[ ] areas_to_improve - VARCHAR(255)
[ ] recommendations - VARCHAR(255)
[ ] last_updated - TIMESTAMP WITH TIME ZONE
```

#### Table: logic_challenges
```
[PK] id - SERIAL
[ ] title - VARCHAR(255) (NOT NULL)
[ ] creator_id - INTEGER
[ ] challenge_type - ENUM (visual, abstract, pattern, word)
[ ] age_group - ENUM (10-11, 12-13, 14-15)
[ ] description - TEXT (NOT NULL)
[ ] visual_data - JSON
[ ] correct_answer - VARCHAR(255) (NOT NULL)
[ ] solution_explanation - TEXT (NOT NULL)
[ ] hint_level1 - TEXT
[ ] hint_level2 - TEXT
[ ] hint_level3 - TEXT
[ ] difficulty_rating - REAL
[ ] estimated_time_minutes - INTEGER
[ ] success_rate - REAL
[ ] image_url - VARCHAR(255)
[ ] source_reference - VARCHAR(255)
[ ] tags - VARCHAR(255)
[ ] is_template - BOOLEAN
[ ] generation_parameters - JSON
[ ] is_active - BOOLEAN
[ ] is_archived - BOOLEAN
[ ] view_count - INTEGER
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
```

## Remarques spéciales pour le développement

- La normalisation des types d'exercice et difficultés est cruciale pour la cohérence des données
- L'architecture dual-backend (FastAPI/Starlette) permet flexibilité et compatibilité
- La migration vers PostgreSQL nécessite attention aux différences de types entre SQLite
- Les changements UI doivent respecter le thème Star Wars établi
- La compatibilité Python 3.13 est une priorité pour la maintenabilité future

### Système de journalisation et débogage

Le projet utilise un système de journalisation centralisé qui est essentiel au développement et à la maintenance :

- **Importance pour le débogage** : Le système de logs permet d'identifier rapidement l'origine des problèmes en production et développement
- **Structure standardisée** : Tous les logs suivent le même format permettant une analyse cohérente
- **Isolation par niveau** : La séparation des logs par niveaux (debug.log, error.log, etc.) facilite l'analyse ciblée
- **Rotation des fichiers** : Les fichiers logs sont automatiquement divisés et compressés pour éviter de saturer le disque
- **Conservation limitée** : Les anciens logs sont automatiquement supprimés après 30-60 jours selon leur importance
- **Test du système** : Le script `test_logging.py` permet de vérifier le bon fonctionnement du système de logs

#### Bonnes pratiques pour la journalisation

1. **Utiliser la fonction centralisée** : Toujours importer via `from app.core.logging_config import get_logger`
2. **Nommer correctement le logger** : Utiliser `logger = get_logger(__name__)` pour identifier la source
3. **Choisir le bon niveau** : 
   - DEBUG pour information détaillée utile en développement
   - INFO pour confirmer le déroulement normal
   - WARNING pour les situations anormales mais non critiques
   - ERROR pour les problèmes empêchant une fonctionnalité
   - CRITICAL pour les problèmes bloquants
4. **Enrichir avec le contexte** : Utiliser `logger.bind(user_id=123).info("Action")` pour ajouter des métadonnées
5. **Capturer les exceptions** : Utiliser `logger.exception()` dans les blocs `except` pour enregistrer la stack trace

Cette architecture est conçue pour être extensible, maintenable et évolutive, permettant l'ajout futur de nouvelles fonctionnalités comme l'authenticité, la personnalisation avancée et la gamification.