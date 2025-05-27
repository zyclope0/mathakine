# 🏗️ Architecture Mathakine

**Vue d'ensemble de l'architecture technique de Mathakine**, application éducative mathématique pour enfants autistes avec thème Star Wars.

## 🎯 Vision Architecturale

### Principes Fondamentaux
- **Dual-Backend** : FastAPI (API pure) + Starlette (interface web)
- **Compatibilité Multi-DB** : PostgreSQL (production) + SQLite (développement)
- **Modularité** : Séparation claire des responsabilités
- **Évolutivité** : Architecture extensible pour futures fonctionnalités
- **Accessibilité** : Support complet des technologies d'assistance

### Objectifs Techniques
- **Performance** : Temps de réponse < 200ms
- **Fiabilité** : Disponibilité 99.9%
- **Sécurité** : Protection des données utilisateur
- **Maintenabilité** : Code modulaire et documenté

## 🏛️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                    │
├─────────────────────────────────────────────────────────────┤
│  Templates Jinja2  │  CSS/JS  │  Thème Star Wars  │  A11y  │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE SERVEUR                          │
├─────────────────────────────────────────────────────────────┤
│           Starlette Server (enhanced_server.py)            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Handlers      │  │     Views       │  │   Routes    │ │
│  │  - Exercices    │  │  - Templates    │  │  - Web      │ │
│  │  - Utilisateurs │  │  - Contexte     │  │  - API      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE API                              │
├─────────────────────────────────────────────────────────────┤
│              FastAPI Application (app/main.py)             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Endpoints     │  │    Schemas      │  │  Services   │ │
│  │  - Auth         │  │  - Pydantic     │  │  - Business │ │
│  │  - Exercises    │  │  - Validation   │  │  - Logic    │ │
│  │  - Users        │  │  - Serialization│  │  - Rules    │ │
│  │  - Challenges   │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE DONNÉES                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    Modèles      │  │   Adaptateurs   │  │  Migrations │ │
│  │  - SQLAlchemy   │  │  - PostgreSQL   │  │  - Alembic  │ │
│  │  - Relations    │  │  - SQLite       │  │  - Versions │ │
│  │  - Contraintes  │  │  - Mapping      │  │  - Schema   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DONNÉES                         │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (Production)  │  SQLite (Développement)        │
│  - Performances           │  - Simplicité                  │
│  - Concurrence           │  - Tests                       │
│  - JSON natif            │  - Développement local         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Composants Principaux

### 1. Enhanced Server (Starlette)
**Fichier** : `enhanced_server.py`

**Responsabilités** :
- Interface web complète avec templates HTML
- Gestion des sessions utilisateur
- Rendu des pages dynamiques
- Intégration avec l'API FastAPI

**Structure** :
```
server/
├── handlers/           # Logique métier par domaine
│   ├── exercise_handlers.py
│   └── user_handlers.py
├── views/             # Gestion des pages HTML
├── routes.py          # Configuration des routes
└── api_routes.py      # Routes API restantes
```

### 2. FastAPI Application
**Fichier** : `app/main.py`

**Responsabilités** :
- API REST pure pour applications externes
- Documentation automatique (Swagger/OpenAPI)
- Validation des données avec Pydantic
- Authentification JWT

**Structure** :
```
app/
├── api/endpoints/     # Endpoints REST
├── models/           # Modèles SQLAlchemy
├── schemas/          # Schémas Pydantic
├── services/         # Logique métier
└── core/            # Configuration et utilitaires
```

### 3. Système de Base de Données
**Compatibilité Dual-DB** :

#### PostgreSQL (Production)
- **Avantages** : Performance, concurrence, JSON natif
- **Usage** : Déploiement, tests d'intégration
- **Configuration** : Variables d'environnement

#### SQLite (Développement)
- **Avantages** : Simplicité, pas de serveur requis
- **Usage** : Développement local, tests unitaires
- **Configuration** : Fichier local

## 🔄 Flux de Données

### 1. Requête Utilisateur
```
Navigateur → Starlette → Templates → Réponse HTML
```

### 2. Appel API
```
Frontend → FastAPI → Services → Modèles → Base de Données
```

### 3. Génération d'Exercices
```
Interface → Handler → Service → Algorithme → Stockage
```

### 4. Authentification
```
Login → JWT Token → Session → Cookies HTTP-only
```

## 🛡️ Sécurité

### Authentification
- **JWT Tokens** avec refresh tokens
- **Cookies HTTP-only** pour la session web
- **Hachage bcrypt** pour les mots de passe
- **Protection CSRF** native

### Validation
- **Pydantic** pour la validation des entrées
- **SQLAlchemy** pour la protection contre l'injection SQL
- **CORS** configuré de manière restrictive

### Données Sensibles
- **Variables d'environnement** pour les secrets
- **Chiffrement** des données sensibles
- **Logs** sans informations personnelles

## 📊 Modèle de Données

### Entités Principales

#### Users (Utilisateurs)
```sql
- id (PK)
- username (UNIQUE)
- email (UNIQUE)
- hashed_password
- role (ENUM: user, admin, teacher)
- created_at, updated_at
```

#### Exercises (Exercices)
```sql
- id (PK)
- title
- exercise_type (ENUM: addition, subtraction, etc.)
- difficulty (ENUM: initie, padawan, chevalier, maitre)
- question, correct_answer
- choices (JSON)
- created_at, updated_at
```

#### Attempts (Tentatives)
```sql
- id (PK)
- user_id (FK)
- exercise_id (FK)
- user_answer
- is_correct
- time_spent
- created_at
```

#### Logic Challenges (Défis Logiques)
```sql
- id (PK)
- title
- challenge_type (ENUM: visual, abstract, pattern, word)
- age_group (ENUM: 10-11, 12-13, 14-15)
- description
- hints (JSON)
- correct_answer
- created_at, updated_at
```

### Relations
- **User** → **Exercises** (1:N, créateur)
- **User** → **Attempts** (1:N)
- **Exercise** → **Attempts** (1:N)
- **User** → **Progress** (1:N)

## 🔧 Système de Migrations

### Alembic
- **Gestion professionnelle** des migrations de schéma
- **Protection des tables héritées** (results, statistics, user_stats)
- **Migrations sécurisées** avec vérification automatique

### Scripts Utilitaires
- `init_alembic.py` : Initialisation
- `generate_migration.py` : Création sécurisée
- `safe_migrate.py` : Migration avec sauvegarde

## 🧪 Architecture de Tests

### Structure en 4 Niveaux
```
tests/
├── unit/              # Tests unitaires
├── api/               # Tests d'API REST
├── integration/       # Tests d'intégration
└── functional/        # Tests fonctionnels
```

### Stratégies
- **Isolation** : Tests indépendants
- **Fixtures** : Données de test réutilisables
- **Mocks** : Simulation des dépendances externes
- **Coverage** : Objectif 75%+

## 🚀 Déploiement

### Environnements

#### Développement
- **SQLite** pour la base de données
- **Debug mode** activé
- **Hot reload** pour les modifications

#### Production
- **PostgreSQL** sur Render
- **Variables d'environnement** sécurisées
- **Logs** centralisés avec loguru
- **Monitoring** des performances

### Docker
```dockerfile
FROM python:3.13-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "enhanced_server.py"]
```

## 📈 Performance

### Optimisations
- **Cache** pour les données fréquentes
- **Pagination** pour les listes longues
- **Lazy loading** des relations
- **Compression gzip** des réponses

### Métriques
- **Temps de réponse** : < 200ms
- **Throughput** : 1000+ req/s
- **Mémoire** : < 512MB
- **CPU** : < 50% en charge normale

## 🔮 Évolutivité

### Extensions Prévues
- **Microservices** : Séparation par domaine
- **Cache Redis** : Performance améliorée
- **CDN** : Distribution des assets
- **API GraphQL** : Requêtes flexibles

### Patterns Architecturaux
- **CQRS** : Séparation lecture/écriture
- **Event Sourcing** : Historique des événements
- **Domain-Driven Design** : Modélisation métier

---

**Architecture conçue pour la croissance et la maintenabilité** 🏗️⭐ 