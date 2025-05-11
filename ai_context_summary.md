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
- **Outils de gestion**:
  - Interface CLI complète (mathakine_cli.py) avec 6 commandes principales
  - Scripts de migration et de gestion de base de données
  - Outils de validation automatisée
- **Déploiement**:
  - Support Docker avec Dockerfile optimisé
  - Configuration pour déploiement sur Render
  - Compatibilité avec Python 3.13

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
- **core/**: Configuration et utilitaires (config.py, logging_config.py)
- **db/**: Accès et initialisation de base de données (init_db.py, base.py)

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
- **exercise.html**: Interface pour résoudre un exercice spécifique
- **exercises.html**: Liste et gestion des exercices avec filtres
- **dashboard.html**: Interface du tableau de bord avec statistiques et graphiques
- **home.html**: Page d'accueil
- **error.html**: Page d'erreur standardisée
- **exercise_detail.html**: Détails d'un exercice spécifique

**CSS et assets**:
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
- **CLEANUP_SUMMARY.md**: Résumé des opérations de nettoyage
- **DASHBOARD_FIX_REPORT.md**: Rapport sur la correction du tableau de bord

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

### Relations entre les tables
- **results.exercise_id** → **exercises.id**: Chaque résultat est lié à un exercice
- **attempts.exercise_id** → **exercises.id**: Chaque tentative est liée à un exercice
- **attempts.user_id** → **users.id**: Chaque tentative est liée à un utilisateur
- **progress.user_id** → **users.id**: Le suivi de progression est lié à un utilisateur
- **exercises.creator_id** → **users.id**: Chaque exercice peut être lié à un créateur
- **user_stats**: Agrège les statistiques par type et niveau

## Interface utilisateur

### Design et thème
- **Thème Star Wars**: Esthétique spatiale avec couleurs bleues/dorées
- **Palette de couleurs**: Variables CSS pour les couleurs thématiques (--sw-blue, --sw-accent, --sw-gold)
- **Typographie**: Optimisée pour l'affichage numérique et le thème spatial
- **Icônes**: Font Awesome 6.4.0 pour les éléments d'interface
- **Animations**: Transitions et effets subtils pour une expérience immersive

### Composants principaux
- **En-tête**: Logo Mathakine avec navigation principale
- **Interface exercices**: Affichage clair avec question et choix de réponses
- **Liste des exercices**: Grille de cartes filtrables par type et difficulté
- **Tableau de bord**: Statistiques et graphiques de performances
- **Modals**: Fenêtres dialog pour détails sans quitter la page

### Interface des exercices
- **Layout optimisé**: Question en haut, choix en grille de boutons
- **Boutons de choix**: Grands (min-height 100px) avec texte agrandi (2rem)
- **Feedback**: Message clair de succès/échec avec détails
- **Navigation fluide**: Boutons pour exercice suivant et retour à la liste

### Tableau de bord
- **Statistiques globales**: Exercices résolus, taux, points d'expérience
- **Graphique de progression**: Visualisation des performances sur 7 jours
- **Performance par type**: Barres de progression pour chaque opération
- **Niveau**: Affichage du niveau actuel et progression

### Fonctionnalités JavaScript
- **Mise à jour dynamique**: Actualisation sans rechargement de page
- **Graphiques interactifs**: Visualisation avec Chart.js
- **Gestion des erreurs**: Messages d'erreur informatifs
- **Modals interactifs**: Affichage des détails sans navigation

## Compatibilité et déploiement

### Compatibilité Python 3.13
- **Dépendances récentes**: SQLAlchemy 2.0+, FastAPI 0.100.0+, Pydantic 2.0+
- **Adaptations**: Modifications pour les changements d'API dans les librairies
- **Tests de compatibilité**: Validation automatisée pour Python 3.13

### Déploiement sur Render
- **PostgreSQL**: Base de données managée sur Render
- **Procfile**: Configuration pour démarrage automatisé
- **Variables d'environnement**: Configuration via interface Render

### Docker
- **Dockerfile**: Configuration pour conteneurisation
- **Multi-stage build**: Optimisation de l'image
- **Environnement paramétrable**: Variables configurables

## État actuel du projet (Mai 2025)

### Vue d'ensemble des fonctionnalités
| Fonctionnalité | État | 
|----------------|------|
| **Backend API REST** | ⚠️ PARTIELLEMENT TERMINÉ |
| **Interface graphique Starlette** | ✅ TERMINÉ |
| **Interface CLI** | ✅ TERMINÉ |
| **Génération d'exercices** | ✅ TERMINÉ |
| **Défis logiques** | ⚠️ EN COURS |
| **Système de progression** | ⚠️ PARTIELLEMENT |
| **Mode adaptatif** | ⚠️ EN COURS |
| **Migration PostgreSQL** | ✅ TERMINÉ |
| **Authentification** | ⚠️ NON IMPLÉMENTÉ |
| **Tableau de bord** | ✅ TERMINÉ |

### Améliorations récentes
1. **Migration vers PostgreSQL**: Support complet pour environnements de production et développement
2. **Normalisation des données**: Correction des incohérences et uniformisation des formats
3. **Amélioration de l'interface**: Corrections UI et meilleure expérience utilisateur
4. **Génération d'exercices par IA**: Implémentation de contextes Star Wars
5. **Ajout des défis logiques**: Modèles et endpoints pour enfants 10-15 ans
6. **Correction du tableau de bord**: Implémentation de la fonction `get_user_stats` et affichage de données réelles
7. **Améliorations de qualité du code**: 
   - Correction d'erreurs de syntaxe dans les templates (balise `{% endblock %}` manquante)
   - Résolution du problème de chevauchement UI entre l'icône de corbeille et le badge IA
   - Scripts de vérification et correction automatique du style de code (fix_style.py, fix_advanced_style.py)
   - Configuration d'outils de lint et qualité (.flake8, setup.cfg)

## Problèmes résolus récemment

### Tableau de bord fonctionnel
- **Problème**: Le tableau de bord ne chargeait pas de données car l'endpoint `/api/users/stats` était manquant
- **Solution**: Implémentation de la fonction `get_user_stats` dans enhanced_server.py qui:
  - Récupère les statistiques globales des exercices (total, corrects, taux de réussite)
  - Calcule les performances par type d'exercice
  - Affiche l'activité des 7 derniers jours dans un graphique
  - Retourne les données au format JSON attendu par le frontend

### Structure des données
- **Problème**: Incohérence entre le schéma défini dans le code et la structure réelle de la base de données
- **Solution**: Mise à jour du schéma pour se conformer à la structure réelle des tables (notamment `results` avec suppression du champ `time_taken` non utilisé)

### Configuration du Déploiement
- **Problème**: Configuration incomplète pour déploiement sur Render
- **Solution**: Optimisation du Procfile et des variables d'environnement pour assurer un déploiement sans erreur

## Itérations futures planifiées

### Complétion de l'API REST
- Implémentation réelle du système d'authentification
- Finalisation des endpoints pour défis logiques
- Développement du système de progression adaptative

### "L'Interface Nouvelle"
- Refonte complète de l'interface utilisateur
- Gamification avancée (médailles, récompenses, niveaux)
- Expérience utilisateur adaptée aux besoins spécifiques

### "Le Grand Archiviste"
- Système avancé d'analyse et de suivi
- Recommandations personnalisées
- Rapports détaillés pour enseignants/parents

### "L'Alliance Galactique"
- Internationalisation et localisation
- Support multilingue
- Adaptation culturelle des exercices

## Glossaire des termes Star Wars

| Terme | Description |
|-------|-------------|
| **Mathakine** | Nom du projet, anciennement Math Trainer |
| **Padawan** | Niveau intermédiaire de difficulté |
| **Initié** | Niveau facile de difficulté |
| **Chevalier** | Niveau difficile de difficulté |
| **Maître** | Niveau expert de difficulté |
| **La Force des nombres** | Compétences mathématiques |
| **API Rebelle** | API REST du projet |
| **Les Archives** | Base de données |
| **Épreuves d'Initié** | Tests unitaires |
| **Épreuves de Chevalier** | Tests d'intégration |
| **Holocrons** | Documentation API (Swagger) |

## Environnement technique

- **Système d'exploitation**: Windows/Linux
- **Langages principaux**: Python 3.13+, JavaScript, HTML/CSS
- **Frameworks**: FastAPI, Starlette, SQLAlchemy 2.0
- **Base de données**: PostgreSQL (prod), SQLite (dev)
- **Interface**: Templates Jinja2, CSS personnalisé
- **Déploiement**: Docker, Render

## Remarques spéciales pour le développement

- La normalisation des types d'exercice et difficultés est cruciale pour la cohérence des données
- L'architecture dual-backend (FastAPI/Starlette) permet flexibilité et compatibilité
- La migration vers PostgreSQL nécessite attention aux différences de types entre SQLite
- Les changements UI doivent respecter le thème Star Wars établi
- La compatibilité Python 3.13 est une priorité pour la maintenabilité future

Cette architecture est conçue pour être extensible, maintenable et évolutive, permettant l'ajout futur de nouvelles fonctionnalités comme l'authenticité, la personnalisation avancée et la gamification. 