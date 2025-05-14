# Architecture technique complète de Mathakine

Ce document décrit l'architecture technique du projet Mathakine, une application d'apprentissage des mathématiques avec thème Star Wars pour les enfants autistes.

## 1. Vue d'ensemble

Mathakine est structuré comme une application web moderne avec une séparation claire entre le backend (API REST) et le frontend. Deux architectures backend coexistent :

1. **API REST FastAPI** (app/main.py) - API pure, sans interface utilisateur
2. **Serveur Starlette** (enhanced_server.py) - Serveur avec interface web intégrée

### Structure du projet

```
mathakine-backend/
├── app/                     # Code principal de l'application
│   ├── api/                 # API REST
│   ├── core/                # Configuration et utilitaires
│   ├── db/                  # Accès à la base de données
│   ├── models/              # Modèles de données SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   └── services/            # Services métier
├── docs/                    # Documentation
├── migrations/              # Migrations Alembic
├── scripts/                 # Scripts utilitaires
├── static/                  # Fichiers statiques
├── templates/               # Templates Jinja2
├── tests/                   # Tests automatisés
├── enhanced_server.py       # Serveur Starlette avec interface UI
├── mathakine_cli.py         # Interface en ligne de commande
├── alembic.ini              # Configuration Alembic
├── Dockerfile               # Configuration Docker
├── requirements.txt         # Dépendances Python
└── Procfile                 # Configuration pour Render/Heroku
```

## 2. Architecture Backend

### 2.1 API REST (app/api/)

L'API REST est organisée selon les principes RESTful avec une séparation claire des endpoints par domaine fonctionnel :

```
app/api/
├── __init__.py
├── api.py                   # Routeur API principal
├── deps.py                  # Dépendances FastAPI (dont l'authentification)
├── endpoints/               # Endpoints API groupés par fonctionnalité
│   ├── __init__.py
│   ├── auth.py              # Authentification (login, logout)
│   ├── exercises.py         # Gestion des exercices
│   ├── users.py             # Gestion des utilisateurs
│   ├── attempts.py          # Tentatives et résultats
│   ├── challenges.py        # Défis logiques
│   └── settings.py          # Configuration
└── router.py                # Enregistrement des routeurs
```

Chaque module d'endpoints contient :
- Des routes CRUD pour la ressource concernée
- Des validations des entrées
- Des opérations spécifiques au domaine

### 2.2 Modèles de données (app/models/)

Les modèles de données sont implémentés avec SQLAlchemy et représentent la structure de la base de données :

```
app/models/
├── __init__.py
├── all_models.py            # Import de tous les modèles
├── attempt.py               # Tentatives d'exercices
├── exercise.py              # Exercices mathématiques
├── logic_challenge.py       # Défis logiques
├── progress.py              # Progression des utilisateurs
├── settings.py              # Paramètres système
└── user.py                  # Utilisateurs
```

### 2.3 Schémas Pydantic (app/schemas/)

Les schémas Pydantic servent à la validation des données et à la sérialisation :

```
app/schemas/
├── __init__.py
├── all_schemas.py           # Import de tous les schémas
├── common.py                # Schémas communs (pagination, réponses)
├── exercise.py              # Schémas d'exercices
├── logic_challenge.py       # Schémas de défis logiques
└── user.py                  # Schémas d'utilisateurs
```

### 2.4 Services (app/services/)

Les services contiennent la logique métier de l'application :

```
app/services/
├── __init__.py
├── auth_service.py          # Service d'authentification
├── db_init_service.py       # Service d'initialisation de la base de données
├── exercise_service.py      # Service de gestion des exercices
├── enhanced_server_adapter.py # Adaptateur pour le serveur enhanced_server.py
└── user_service.py          # Service de gestion des utilisateurs
```

### 2.5 Configuration et Base de Données (app/core/ et app/db/)

La configuration et l'accès à la base de données sont gérés par ces modules :

```
app/core/
├── __init__.py
├── config.py                # Configuration de l'application
├── constants.py             # Constantes centralisées
├── messages.py              # Messages centralisés
├── security.py              # Sécurité (hachage, JWT)
└── logging_config.py        # Configuration du système de journalisation

app/db/
├── __init__.py
├── base.py                  # Configuration SQLAlchemy
├── queries.py               # Requêtes SQL centralisées
└── init_db.py               # Initialisation de la base de données
```

## 3. Schéma de la base de données

### 3.1 Tables principales

#### users
Table des utilisateurs de l'application.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| username | VARCHAR | NOT NULL | Nom d'utilisateur |
| email | VARCHAR | NOT NULL | Email de l'utilisateur |
| hashed_password | VARCHAR | NOT NULL | Mot de passe hashé |
| full_name | VARCHAR | NULL | Nom complet |
| role | VARCHAR(10) | NULL | Rôle utilisateur (PADAWAN, MAÎTRE, GARDIEN, ARCHIVISTE) |
| is_active | BOOLEAN | NULL | Indique si le compte est actif |
| created_at | TIMESTAMP | NULL | Date de création du compte |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |
| grade_level | INTEGER | NULL | Niveau scolaire |
| learning_style | VARCHAR | NULL | Style d'apprentissage préféré |
| preferred_difficulty | VARCHAR | NULL | Niveau de difficulté préféré |
| preferred_theme | VARCHAR | NULL | Thème préféré |
| accessibility_settings | VARCHAR | NULL | Paramètres d'accessibilité |

#### exercises
Table des exercices mathématiques.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| title | VARCHAR | NOT NULL | Titre de l'exercice |
| creator_id | INTEGER | NULL | ID de l'utilisateur créateur, clé étrangère vers users.id |
| exercise_type | VARCHAR | NOT NULL | Type d'exercice |
| difficulty | VARCHAR | NOT NULL | Niveau de difficulté |
| tags | VARCHAR | NULL | Tags pour la catégorisation |
| question | TEXT | NOT NULL | Énoncé de la question |
| correct_answer | VARCHAR | NOT NULL | Réponse correcte |
| choices | JSON | NULL | Choix possibles (pour QCM) |
| explanation | TEXT | NULL | Explication de la solution |
| hint | TEXT | NULL | Indice |
| image_url | VARCHAR | NULL | URL d'une image associée |
| audio_url | VARCHAR | NULL | URL d'un fichier audio associé |
| is_active | BOOLEAN | NULL | Indique si l'exercice est actif |
| is_archived | BOOLEAN | NULL | Indique si l'exercice est archivé |
| view_count | INTEGER | NULL | Nombre de vues |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

#### attempts
Table des tentatives de résolution d'exercices.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| exercise_id | INTEGER | NOT NULL | ID de l'exercice tenté, clé étrangère vers exercises.id |
| user_answer | VARCHAR | NOT NULL | Réponse donnée par l'utilisateur |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| time_spent | DOUBLE PRECISION | NULL | Temps passé en secondes |
| attempt_number | INTEGER | NULL | Numéro de la tentative |
| hints_used | INTEGER | NULL | Nombre d'indices utilisés |
| device_info | VARCHAR | NULL | Informations sur l'appareil utilisé |
| created_at | TIMESTAMP | NULL | Date de la tentative |

#### progress
Table de progression des utilisateurs.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| exercise_type | VARCHAR | NOT NULL | Type d'exercice |
| difficulty | VARCHAR | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NULL | Nombre total de tentatives |
| correct_attempts | INTEGER | NULL | Nombre de tentatives correctes |
| average_time | DOUBLE PRECISION | NULL | Temps moyen de résolution |
| completion_rate | DOUBLE PRECISION | NULL | Taux de complétion |
| streak | INTEGER | NULL | Série actuelle |
| highest_streak | INTEGER | NULL | Meilleure série |
| mastery_level | INTEGER | NULL | Niveau de maîtrise |
| awards | JSON | NULL | Récompenses obtenues |
| strengths | VARCHAR | NULL | Points forts identifiés |
| areas_to_improve | VARCHAR | NULL | Domaines à améliorer |
| recommendations | VARCHAR | NULL | Recommandations |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour |

### 3.2 Défis logiques

#### logic_challenges
Table des défis de logique.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| title | VARCHAR | NOT NULL | Titre du défi |
| creator_id | INTEGER | NULL | ID de l'utilisateur créateur, clé étrangère vers users.id |
| challenge_type | VARCHAR(11) | NOT NULL | Type de défi logique |
| age_group | VARCHAR(11) | NOT NULL | Tranche d'âge cible |
| description | TEXT | NOT NULL | Description du défi |
| visual_data | JSON | NULL | Données visuelles (diagrammes, images) |
| correct_answer | VARCHAR | NOT NULL | Réponse correcte |
| solution_explanation | TEXT | NOT NULL | Explication de la solution |
| hint_level1 | TEXT | NULL | Indice de niveau 1 |
| hint_level2 | TEXT | NULL | Indice de niveau 2 |
| hint_level3 | TEXT | NULL | Indice de niveau 3 |
| difficulty_rating | DOUBLE PRECISION | NULL | Niveau de difficulté |
| estimated_time_minutes | INTEGER | NULL | Temps estimé en minutes |
| success_rate | DOUBLE PRECISION | NULL | Taux de réussite |
| image_url | VARCHAR | NULL | URL d'une image associée |
| source_reference | VARCHAR | NULL | Référence à la source |
| tags | VARCHAR | NULL | Tags pour la catégorisation |
| is_template | BOOLEAN | NULL | Indique si c'est un modèle |
| generation_parameters | JSON | NULL | Paramètres de génération |
| is_active | BOOLEAN | NULL | Indique si le défi est actif |
| is_archived | BOOLEAN | NULL | Indique si le défi est archivé |
| view_count | INTEGER | NULL | Nombre de vues |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

#### logic_challenge_attempts
Table des tentatives de résolution des défis logiques.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NOT NULL | ID de l'utilisateur, clé étrangère vers users.id |
| challenge_id | INTEGER | NOT NULL | ID du défi, clé étrangère vers logic_challenges.id |
| user_answer | VARCHAR | NOT NULL | Réponse donnée par l'utilisateur |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| time_spent | DOUBLE PRECISION | NULL | Temps passé en secondes |
| hint_level1_used | BOOLEAN | NULL | Indique si l'indice niveau 1 a été utilisé |
| hint_level2_used | BOOLEAN | NULL | Indique si l'indice niveau 2 a été utilisé |
| hint_level3_used | BOOLEAN | NULL | Indique si l'indice niveau 3 a été utilisé |
| attempt_number | INTEGER | NULL | Numéro de la tentative |
| notes | TEXT | NULL | Notes sur la tentative |
| created_at | TIMESTAMP | NULL | Date de la tentative |

### 3.3 Tables de configuration

#### settings
Table des paramètres de l'application.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| key | VARCHAR | NOT NULL | Clé du paramètre |
| value | VARCHAR | NULL | Valeur du paramètre |
| value_json | JSON | NULL | Valeur JSON du paramètre |
| description | VARCHAR | NULL | Description du paramètre |
| category | VARCHAR | NULL | Catégorie du paramètre |
| is_system | BOOLEAN | NULL | Indique si c'est un paramètre système |
| is_public | BOOLEAN | NULL | Indique si le paramètre est public |
| created_at | TIMESTAMP | NULL | Date de création |
| updated_at | TIMESTAMP | NULL | Date de dernière mise à jour |

### 3.4 Tables héritées (historiques)

Ce sont des tables qui existaient dans les versions précédentes et qui sont conservées pour la compatibilité :

#### results
Table historique des résultats d'exercices.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| exercise_id | INTEGER | NOT NULL | ID de l'exercice |
| is_correct | BOOLEAN | NOT NULL | Indique si la réponse est correcte |
| attempt_count | INTEGER | NULL | Nombre de tentatives, par défaut 1 |
| time_spent | REAL | NULL | Temps passé |
| created_at | TIMESTAMP | NULL | Date de création, par défaut CURRENT_TIMESTAMP |

#### statistics
Table historique des statistiques par session.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| user_id | INTEGER | NULL | ID de l'utilisateur |
| session_id | VARCHAR(255) | NOT NULL | ID de la session |
| exercise_type | VARCHAR(50) | NOT NULL | Type d'exercice |
| difficulty | VARCHAR(50) | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NOT NULL | Nombre total de tentatives, par défaut 0 |
| correct_attempts | INTEGER | NOT NULL | Nombre de tentatives correctes, par défaut 0 |
| avg_time | REAL | NOT NULL | Temps moyen de résolution, par défaut 0 |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour, par défaut CURRENT_TIMESTAMP |

#### user_stats
Table historique des statistiques des utilisateurs.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | INTEGER | NOT NULL | Identifiant unique, clé primaire |
| exercise_type | VARCHAR(50) | NOT NULL | Type d'exercice |
| difficulty | VARCHAR(50) | NOT NULL | Niveau de difficulté |
| total_attempts | INTEGER | NULL | Nombre total de tentatives, par défaut 0 |
| correct_attempts | INTEGER | NULL | Nombre de tentatives correctes, par défaut 0 |
| last_updated | TIMESTAMP | NULL | Date de dernière mise à jour, par défaut CURRENT_TIMESTAMP |

#### schema_version
Table de version du schéma.

| Colonne | Type | Nullable | Description |
|---------|------|----------|-------------|
| version | INTEGER | NOT NULL | Numéro de version du schéma |

### 3.5 Relations entre les tables

#### Clés étrangères
- `exercises.creator_id` → `users.id`
- `attempts.user_id` → `users.id`
- `attempts.exercise_id` → `exercises.id`
- `progress.user_id` → `users.id`
- `logic_challenges.creator_id` → `users.id`
- `logic_challenge_attempts.user_id` → `users.id`
- `logic_challenge_attempts.challenge_id` → `logic_challenges.id`

#### Relations avec cascade
Toutes les relations sont configurées avec `cascade="all, delete-orphan"` pour assurer l'intégrité des données lors des suppressions.

## 4. Interface en Ligne de Commande (CLI)

Le fichier `mathakine_cli.py` fournit une interface en ligne de commande complète pour gérer l'application :

```
mathakine_cli.py             # Interface CLI principale
```

Commandes disponibles :
- `run` : Démarrer l'application (avec/sans interface graphique)
- `init` : Initialiser la base de données
- `test` : Exécuter les tests
- `validate` : Valider l'application
- `shell` : Démarrer un shell Python interactif
- `setup` : Configurer l'environnement de développement

## 5. Enhanced Server (Interface web)

Le fichier `enhanced_server.py` implémente un serveur Starlette qui fournit une interface web pour l'application :

### Fonctionnalités principales
- Interface web complète avec templates HTML et CSS
- API REST simple avec endpoints JSON
- Génération d'exercices (simple et IA)
- Soumission de réponses et feedback
- Tableau de bord avec statistiques
- Gestion des exercices (liste, détails, suppression)

### Routes principales :
- Pages HTML: "/", "/exercises", "/dashboard", "/exercise/{id}"
- API: "/api/exercises/", "/api/exercises/{id}", "/api/exercises/generate", "/api/exercises/{id}/submit", "/api/users/stats"

### Adaptateur EnhancedServerAdapter
Un adaptateur a été développé pour intégrer progressivement le serveur enhanced_server.py avec le nouveau système de transaction :
- Conversion des opérations SQL directes en appels aux services métier
- Gestion cohérente des sessions SQLAlchemy
- Support des endpoints clés (delete_exercise, submit_answer, get_exercises_list)

## 6. Déploiement

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation des dépendances spécifiques à Python 3.13
RUN pip install --no-cache-dir sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port utilisé par l'application
EXPOSE 8081

# Définir les variables d'environnement pour la production
ENV MATH_TRAINER_DEBUG=false
ENV MATH_TRAINER_PROFILE=prod
ENV MATH_TRAINER_PORT=8081

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

### Render

Le projet est configuré pour le déploiement sur Render avec un script de démarrage qui initialise la base de données et démarre le serveur.

## 7. Système de sécurité et authentification

Le système de sécurité, surnommé "Les Cristaux d'Identité", comporte :

- JSON Web Tokens (JWT) pour l'authentification sans état
- Bcrypt pour le hachage sécurisé des mots de passe
- Système de rôles hiérarchique (Padawan, Maître, Gardien, Archiviste)
- Middleware de vérification des tokens et autorisations

### Architecture de sécurité
```
app/
├── core/
│   ├── security.py          # Utilitaires de sécurité (création de tokens, hachage)
│   └── config.py            # Configuration de sécurité (clés, durée de vie des tokens)
├── services/
│   └── auth_service.py      # Service d'authentification
├── api/
│   ├── deps.py              # Middleware d'authentification et vérification des rôles
│   └── endpoints/
│       ├── auth.py          # Endpoints d'authentification
│       └── users.py         # Gestion des utilisateurs
└── schemas/
    └── user.py              # Schémas de validation pour l'authentification
```

## 8. Normalisation et intégrité des données

Une attention particulière a été portée à la normalisation des données :

### Problèmes résolus
1. **Incohérence des formats** : Normalisation des types d'exercices et niveaux de difficulté
2. **Doublons dans les statistiques** : Mécanisme de fusion des statistiques

### Mécanismes de normalisation
1. **Normalisation à la source** : Fonctions `normalize_exercise_type()` et `normalize_difficulty()`
2. **Correction des données existantes** : Script `fix_database.py`
3. **Validation continue** : Tests automatisés et fonction `check_data_normalization()`

## 9. Compatibilité Python 3.13

Des efforts significatifs ont été faits pour assurer la compatibilité avec Python 3.13 :

1. **Mise à jour des dépendances** :
   - SQLAlchemy 2.0.40
   - FastAPI 0.115.12
   - Pydantic 2.11.4
   - pydantic-settings pour la gestion des configurations

2. **Corrections de code** :
   - Utilisation des new-style asynccontextmanager pour FastAPI
   - Correction des changements d'API dans SQLAlchemy
   - Adaptation aux nouvelles conventions de Pydantic

3. **Améliorations de sécurité** :
   - Utilisation des meilleures pratiques pour la validation des entrées
   - Mise en œuvre de middleware de sécurité

## 10. Évolution future

L'architecture est conçue pour permettre les évolutions suivantes :

1. **Migration complète vers PostgreSQL**
   - Utilisation cohérente dans tous les environnements
   - Optimisation des performances avec indexation avancée

2. **Microservices**
   - Décomposition potentielle en services spécialisés
   - API Gateway pour la gestion des requêtes

3. **Intégration d'IA**
   - Génération d'exercices par IA
   - Analyse prédictive des performances des utilisateurs

4. **Interface utilisateur avancée**
   - Interface holographique pour les exercices
   - Retours sonores adaptés au thème Star Wars

---

*Ce document consolide les informations de ARCHITECTURE.md et SCHEMA.md. Dernière mise à jour: 14/05/2025* 