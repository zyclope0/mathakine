# Structure du Projet Mathakine

## Vue d'ensemble

Mathakine est une application web éducative pour l'apprentissage des mathématiques, conçue spécifiquement pour les enfants autistes avec une interface thématique Star Wars. L'architecture suit une approche modulaire avec séparation claire entre frontend, backend et base de données.

```
mathakine/
├── app/                    # Application principale FastAPI
├── server/                 # Serveur Starlette avec interface web
├── templates/              # Templates Jinja2 (Frontend)
├── static/                 # Ressources statiques (CSS, JS, images)
├── migrations/             # Migrations Alembic
├── docs/                   # Documentation complète
├── tests/                  # Suite de tests
├── scripts/                # Scripts utilitaires
├── archives/               # Fichiers archivés
├── logs/                   # Fichiers de journalisation
└── backups/                # Sauvegardes
```

## Architecture Technique

### 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (UI)                         │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Templates HTML   │  │   CSS/JS     │  │    Assets    │ │
│  │    (Jinja2)      │  │ (Thème SW)   │  │   (Images)   │ │
│  └──────────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Serveurs)                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │ Enhanced Server  │  │      FastAPI Server        │   │
│  │   (Starlette)    │  │    (API REST Pure)         │   │
│  │   - UI Web       │  │    - Endpoints API         │   │
│  │   - Routes HTML  │  │    - Documentation         │   │
│  └──────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Couche de Données                         │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │   SQLAlchemy     │  │      PostgreSQL/SQLite      │   │
│  │   (ORM)          │  │     (Base de données)       │   │
│  └──────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 📱 Frontend - Interface Utilisateur

#### Templates HTML (`templates/`)
```
templates/
├── base.html               # Template de base avec layout commun
├── home.html               # Page d'accueil
├── login.html              # Page de connexion
├── register.html           # Page d'inscription
├── dashboard.html          # Tableau de bord utilisateur
├── exercises.html          # Liste des exercices
├── exercise.html           # Page de résolution d'exercice
├── exercise_detail.html    # Détails d'un exercice
├── exercise_simple.html    # Version simplifiée
├── error.html              # Page d'erreur
└── partials/               # Composants réutilisables
```

#### Ressources Statiques (`static/`)
```
static/
├── css/
│   ├── normalize.css       # Reset CSS
│   ├── variables.css       # Variables CSS centralisées
│   ├── utils.css           # Classes utilitaires
│   ├── style.css           # Styles globaux
│   ├── space-theme.css     # Thème Star Wars
│   └── home-styles.css     # Styles page d'accueil
├── js/
│   ├── main.js             # JavaScript principal
│   └── accessibility.js    # Fonctions d'accessibilité
└── images/
    └── star-wars/          # Assets thématiques
```

### 🖥️ Backend - Serveurs

#### Enhanced Server (`enhanced_server.py`)
- **Framework**: Starlette
- **Fonction**: Interface web complète avec rendu HTML
- **Routes principales**:
  - `/` - Page d'accueil
  - `/login` - Authentification
  - `/dashboard` - Tableau de bord
  - `/exercises` - Gestion des exercices
  - `/api/*` - Endpoints API intégrés

#### FastAPI Server (`app/main.py`)
- **Framework**: FastAPI
- **Fonction**: API REST pure pour intégrations externes
- **Documentation**: Swagger UI automatique (`/docs`)
- **Endpoints principaux**:
  - `/api/auth/*` - Authentification JWT
  - `/api/users/*` - Gestion utilisateurs
  - `/api/exercises/*` - CRUD exercices
  - `/api/challenges/*` - Défis logiques
  - `/api/progress/*` - Suivi progression

### 💾 Base de Données

#### Schéma de Base de Données

##### Table: users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('padawan', 'maitre', 'gardien', 'archiviste', 'admin'),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    grade_level INTEGER,
    learning_style VARCHAR(50),
    preferred_difficulty VARCHAR(50),
    preferred_theme VARCHAR(50),
    accessibility_settings JSON
);
```

##### Table: exercises
```sql
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    creator_id INTEGER REFERENCES users(id),
    exercise_type ENUM('addition', 'soustraction', 'multiplication', 
                      'division', 'fractions', 'geometrie', 'texte', 
                      'mixte', 'divers'),
    difficulty ENUM('initie', 'padawan', 'chevalier', 'maitre'),
    tags VARCHAR,
    age_group VARCHAR,
    context_theme VARCHAR,
    complexity INTEGER,
    ai_generated BOOLEAN DEFAULT FALSE,
    question TEXT NOT NULL,
    correct_answer VARCHAR NOT NULL,
    choices JSON,
    explanation TEXT,
    hint TEXT,
    image_url VARCHAR,
    audio_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

##### Table: attempts
```sql
CREATE TABLE attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exercise_id INTEGER REFERENCES exercises(id),
    user_answer VARCHAR NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent REAL,
    attempt_number INTEGER,
    hints_used INTEGER,
    device_info VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

##### Table: progress
```sql
CREATE TABLE progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exercise_type VARCHAR NOT NULL,
    difficulty VARCHAR NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    average_time REAL,
    completion_rate REAL,
    streak INTEGER DEFAULT 0,
    highest_streak INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 0,
    awards JSON,
    strengths VARCHAR,
    areas_to_improve VARCHAR,
    recommendations VARCHAR,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

##### Table: logic_challenges
```sql
CREATE TABLE logic_challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    creator_id INTEGER REFERENCES users(id),
    challenge_type ENUM('visual', 'abstract', 'pattern', 'word'),
    age_group ENUM('10-11', '12-13', '14-15'),
    description TEXT NOT NULL,
    visual_data JSON,
    correct_answer VARCHAR NOT NULL,
    solution_explanation TEXT NOT NULL,
    hints JSON,
    difficulty_rating REAL,
    estimated_time_minutes INTEGER,
    success_rate REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 📦 Dépendances Principales

#### Backend
```
# Serveurs Web
starlette==0.31.1          # Framework web léger
uvicorn==0.23.2            # Serveur ASGI
fastapi==0.115.12          # API REST moderne

# Base de données
sqlalchemy==2.0.40         # ORM Python
psycopg2-binary==2.9.9     # Driver PostgreSQL
alembic==1.13.1            # Migrations DB

# Authentification
python-jose[cryptography]==3.4.0  # JWT
passlib[bcrypt]==1.7.4           # Hachage passwords

# Validation
pydantic==2.11.0           # Validation de données
email-validator==2.1.0     # Validation emails

# Templates
jinja2==3.1.2              # Moteur de templates

# Utilitaires
python-dotenv==1.0.0       # Variables d'environnement
loguru==0.7.2              # Journalisation avancée
```

#### Tests
```
pytest==7.4.3              # Framework de tests
pytest-cov==4.1.0          # Couverture de code
pytest-asyncio==0.26.0     # Tests asynchrones
httpx==0.27.0              # Client HTTP pour tests
```

### 🧪 Structure des Tests

```
tests/
├── unit/                  # Tests unitaires (modèles, services)
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── api/                   # Tests des endpoints API
│   ├── test_auth_endpoints.py
│   ├── test_exercise_endpoints.py
│   └── test_user_endpoints.py
├── integration/           # Tests d'intégration
│   ├── test_db_operations.py
│   └── test_workflows.py
├── functional/            # Tests fonctionnels
│   ├── test_user_flows.py
│   └── test_exercise_flows.py
└── fixtures/              # Données de test partagées
```

### 🔧 Scripts Utilitaires

```
scripts/
├── check_compatibility.py      # Vérification compatibilité DB
├── generate_context.py         # Génération contexte projet
├── generate_migration.py       # Création migrations Alembic
├── init_alembic.py            # Initialisation Alembic
├── normalize_css.py           # Normalisation styles CSS
├── pre_commit_migration_check.py  # Vérification pré-commit
├── toggle_database.py         # Bascule SQLite/PostgreSQL
└── restore_deleted_tables.sql # Restauration tables
```

## Flux de Données

### Authentification
```
Client → Login Form → Enhanced Server → Auth Service → JWT Token → Session
```

### Création d'Exercice
```
Professeur → Form → Enhanced Server → Exercise Service → DB → Confirmation
```

### Résolution d'Exercice
```
Élève → Exercise Page → Submit Answer → Validation → Progress Update → Feedback
```

## Configuration et Déploiement

### Variables d'Environnement (.env)
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Docker
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "enhanced_server:app", "--host", "0.0.0.0"]
```

## Conventions de Code

### Python
- **Style**: PEP 8
- **Docstrings**: Google style
- **Type hints**: Utilisation systématique
- **Imports**: Organisés par stdlib → third-party → local

### SQL
- **Noms de tables**: snake_case, pluriel
- **Clés primaires**: `id`
- **Clés étrangères**: `<table>_id`
- **Timestamps**: `created_at`, `updated_at`

### API
- **Endpoints**: RESTful, kebab-case
- **Réponses**: JSON avec structure standardisée
- **Erreurs**: Codes HTTP appropriés avec détails

### Git
- **Branches**: feature/*, bugfix/*, hotfix/*
- **Commits**: Conventionnels (feat, fix, docs, etc.)
- **Pull Requests**: Review obligatoire

## Sécurité

- **Authentification**: JWT avec refresh tokens
- **Mots de passe**: Bcrypt avec salt
- **CORS**: Configuration stricte
- **Validation**: Pydantic sur toutes les entrées
- **SQL Injection**: Protection via SQLAlchemy ORM
- **XSS**: Échappement automatique Jinja2

---

*Dernière mise à jour : 26 mai 2025* 