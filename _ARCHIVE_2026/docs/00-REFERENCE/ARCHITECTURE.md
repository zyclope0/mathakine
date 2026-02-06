# 🏗️ ARCHITECTURE MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025  
**Statut** : ✅ Production Ready

---

## 📊 VUE D'ENSEMBLE

### Architecture globale

```
┌──────────────────────────────────────────────┐
│     Frontend Next.js (localhost:3000)        │
│  • React 19 + TypeScript 5                   │
│  • Tailwind CSS 4 + shadcn/ui                │
│  • TanStack Query + Zustand                  │
│  • next-intl (i18n FR/EN)                    │
│  • PWA avec service worker                   │
└──────────────────┬───────────────────────────┘
                   │ HTTP/REST API
                   │ CORS configuré
                   ↓
┌──────────────────────────────────────────────┐
│   Backend Starlette API (localhost:8000)     │
│  • 37 routes API JSON pures                  │
│  • Handlers + Services (ORM SQLAlchemy)      │
│  • Auth centralisé (server/auth.py)          │
│  • Constants centralisées (app/core/)        │
│  • Streaming SSE pour génération IA          │
└──────────────────┬───────────────────────────┘
                   │ SQLAlchemy 2.0 ORM
                   │ Alembic migrations
                   ↓
┌──────────────────────────────────────────────┐
│        PostgreSQL 15 Database                │
│  • Users, Exercises, Challenges              │
│  • Badges, Recommendations                   │
│  • Logic Challenge Attempts                  │
│  • User Progress tracking                    │
└──────────────────────────────────────────────┘
```

---

## 🎯 PRINCIPES ARCHITECTURAUX

### 1. Séparation Frontend/Backend (Phase 2)
- **Frontend** : 100% Next.js (localhost:3000)
- **Backend** : 100% API JSON (localhost:8000)
- **Communication** : REST API + SSE pour streaming

### 2. Backend API pur
- ✅ **Suppression complète** du frontend du backend Starlette
- ✅ **23 routes HTML supprimées**
- ✅ **37 routes API JSON** uniquement
- ✅ **Templates/** supprimé du backend

### 3. Services ORM unifiés (Phase 4)
- ✅ **SQLAlchemy 2.0** exclusivement
- ✅ **6 services obsolètes** archivés (*_translations, *_adapter)
- ✅ **1 source de vérité** par entité

### 4. Constantes centralisées (Phase 3)
- ✅ **app/core/constants.py** unique
- ✅ **Normalisation** : `normalize_challenge_type()`, `normalize_age_group()`
- ✅ **17 fichiers** refactorisés

---

## 📁 STRUCTURE DU CODE

### Frontend (`frontend/`)
```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Routes authentification
│   ├── challenges/        # Page défis
│   ├── exercises/         # Page exercices
│   ├── dashboard/         # Tableau de bord
│   └── api/               # API routes (proxy backend)
├── components/            # Composants React
│   ├── ui/               # shadcn/ui
│   ├── challenges/       # Composants défis
│   ├── exercises/        # Composants exercices
│   └── layout/           # Layout components
├── hooks/                # Custom hooks
│   ├── useAuth.ts
│   ├── useChallenges.ts
│   └── useExercises.ts
├── lib/                  # Utilities
│   ├── api/             # Client API
│   ├── constants/       # Frontend constants
│   └── utils/           # Helpers
├── types/               # TypeScript types
└── public/              # Assets statiques
```

### Backend (`app/` + `server/`)
```
app/                       # FastAPI (docs OpenAPI)
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── exercise.py
│   ├── logic_challenge.py
│   └── all_models.py
├── schemas/              # Pydantic schemas
│   ├── user.py
│   ├── exercise.py
│   └── all_schemas.py
├── services/             # Business logic (ORM)
│   ├── auth_service.py
│   ├── badge_service.py
│   ├── challenge_service.py
│   ├── exercise_service.py
│   ├── logic_challenge_service.py
│   ├── user_service.py
│   ├── recommendation_service.py
│   └── archives/         # Services obsolètes
├── api/
│   ├── deps.py          # Dependencies
│   └── endpoints/        # FastAPI endpoints
├── core/                 # Configuration
│   ├── config.py
│   ├── security.py
│   └── constants.py      # ⭐ Constantes centralisées
└── db/                   # Database
    ├── base.py
    └── transaction.py

server/                    # Starlette (API JSON pure)
├── app.py                # Application Starlette
├── routes.py             # Routes API (37 routes)
├── auth.py               # Auth centralisé
├── handlers/             # Request handlers
│   ├── exercise_handlers.py
│   ├── challenge_handlers.py
│   ├── auth_handlers.py
│   ├── user_handlers.py
│   ├── badge_handlers.py
│   ├── chat_handlers.py
│   └── ...
├── exercise_generator.py # Génération exercices
└── api_challenges.py     # API challenges
```

---

## 🔌 API BACKEND

### Authentification
```
POST   /api/auth/login          # Connexion
POST   /api/auth/refresh        # Rafraîchir token
GET    /api/users/me            # Utilisateur actuel
POST   /api/auth/register       # Inscription
```

### Challenges
```
GET    /api/challenges                    # Liste challenges
GET    /api/challenges/{id}               # Challenge par ID
POST   /api/challenges/{id}/attempt       # Soumettre tentative
GET    /api/challenges/{id}/hint          # Obtenir indice
GET    /api/challenges/generate-ai-stream # Génération IA (SSE)
```

### Exercises
```
GET    /api/exercises                   # Liste exercices
POST   /api/exercises                   # Créer exercice
GET    /api/exercises/{id}              # Exercice par ID
POST   /api/exercises/{id}/attempt      # Soumettre tentative
GET    /api/exercises/generate-ai-stream # Génération IA (SSE)
```

### Badges & Gamification
```
GET    /api/badges/user               # Badges utilisateur
GET    /api/badges/available          # Badges disponibles
POST   /api/badges/check              # Vérifier nouveaux badges
GET    /api/gamification/stats        # Statistiques gamification
```

### User & Stats
```
GET    /api/users/stats               # Statistiques utilisateur
GET    /api/users/progress            # Progression utilisateur
PUT    /api/users/me                  # Mettre à jour profil
```

**Total : 37 routes API JSON**

Voir documentation complète : [`docs/00-REFERENCE/API.md`](API.md)

---

## 💾 BASE DE DONNÉES

### Modèles principaux

#### User
```python
class User(Base):
    id: int
    username: str
    email: str
    hashed_password: str
    role: str  # student, teacher, admin
    is_active: bool
    created_at: datetime
```

#### Exercise
```python
class Exercise(Base):
    id: int
    title: str
    exercise_type: str  # CALCULATION, SEQUENCE, PATTERN, etc.
    difficulty: str     # EASY, MEDIUM, HARD
    question: str
    correct_answer: str
    choices: list[str]  # JSON
    explanation: str
    hint: str
    creator_id: int
```

#### LogicChallenge
```python
class LogicChallenge(Base):
    id: int
    title: str
    description: str
    challenge_type: str  # SEQUENCE, PATTERN, PUZZLE, etc.
    age_group: str       # GROUP_6_8, GROUP_10_12, GROUP_13_15
    correct_answer: str
    solution_explanation: str
    difficulty_rating: float
    hints: dict  # JSON avec niveaux d'indices
```

#### Badge
```python
class Badge(Base):
    id: int
    code: str  # FIRST_EXERCISE, CHALLENGE_MASTER, etc.
    name: str
    description: str
    icon_url: str
    points: int
    criteria: dict  # JSON avec conditions
```

### Relations
```
User 1──N Exercises (creator)
User 1──N ExerciseAttempts
User 1──N LogicChallengeAttempts
User M──N Badges (user_badges)
User 1──1 UserProgress
User 1──N Recommendations
```

---

## 🔐 AUTHENTIFICATION

### Flow
```
1. POST /api/auth/login
   → Retourne access_token (JWT)
   → Stocké dans cookie HTTP-only

2. Requêtes authentifiées
   → Cookie access_token envoyé automatiquement
   → Backend vérifie JWT
   → Retourne données utilisateur

3. Refresh token
   → POST /api/auth/refresh
   → Nouveau access_token généré
```

### Sécurité
- ✅ **Cookies HTTP-only** (protection XSS)
- ✅ **CORS configuré** (frontend autorisé)
- ✅ **JWT avec expiration** (30 min)
- ✅ **Passwords hashed** (bcrypt)
- ✅ **HTTPS en production**

---

## 🚀 DEPLOYMENT

### Production (Render)
```
Frontend: mathakine-frontend.onrender.com
Backend:  mathakine-backend.onrender.com
Database: PostgreSQL 15 (managed)
```

### Environnements
```yaml
Development:
  Frontend: localhost:3000
  Backend:  localhost:8000
  Database: SQLite (local)

Production:
  Frontend: Render (Static Site)
  Backend:  Render (Web Service)
  Database: Render (PostgreSQL)
```

### Variables d'environnement

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Backend (.env)**
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALLOWED_ORIGINS=http://localhost:3000,https://mathakine-frontend.onrender.com
```

---

## 📊 CONSTANTES CENTRALISÉES

### app/core/constants.py

```python
# Challenge Types
CHALLENGE_TYPES_DB = {
    "SEQUENCE": "Séquences numériques",
    "PATTERN": "Reconnaissance de motifs",
    "PUZZLE": "Énigmes logiques",
    "CALCULATION": "Calcul mental",
    "CHESS": "Stratégie échecs"
}

# Age Groups
AGE_GROUPS_DB = {
    "GROUP_6_8": "6-8 ans",
    "GROUP_10_12": "10-12 ans",
    "GROUP_13_15": "13-15 ans"
}

# Exercise Types
class ExerciseTypes(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

# Difficulty Levels
class DifficultyLevels(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Normalization functions
def normalize_challenge_type(type_str: str) -> str:
    """Normalise challenge type (sequence → SEQUENCE)"""
    # ...

def normalize_age_group(age_str: str) -> str:
    """Normalise age group (age_6_8 → GROUP_6_8)"""
    # ...
```

---

## 🧪 TESTS

### Structure
```
tests/
├── api/                  # Tests API
│   ├── test_auth_flow.py
│   ├── test_challenges_flow.py
│   └── test_exercises_flow.py
├── unit/                 # Tests unitaires
│   ├── test_constants.py
│   └── test_services.py
├── integration/          # Tests intégration
└── conftest.py           # Fixtures pytest
```

### CI/CD
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: ...
    steps:
      - pytest tests/ --cov --cov-report=xml
      - codecov upload
```

---

## 🎯 PHASES COMPLÉTÉES

| Phase | Objectif | Impact Architecture |
|-------|----------|---------------------|
| **Phase 1** | Code mort | -130 lignes, fonctions renommées |
| **Phase 2** | Séparation Frontend/Backend | Backend 100% API |
| **Phase 3** | Refactoring DRY | Constants centralisées |
| **Phase 4** | Services ORM | Unified SQLAlchemy |
| **Phase 5** | Tests automatisés | CI/CD opérationnel |
| **Phase 6** | Nommage & lisibilité | Variables explicites |

**Résultat** : Architecture propre, maintenable, production-ready

---

## 📚 RÉFÉRENCES

- **API complète** : [`API.md`](API.md)
- **Getting Started** : [`../01-GUIDES/GETTING_STARTED.md`](../01-GUIDES/GETTING_STARTED.md)
- **Développement** : [`../01-GUIDES/DEVELOPMENT.md`](../01-GUIDES/DEVELOPMENT.md)
- **Tests** : [`../01-GUIDES/TESTING.md`](../01-GUIDES/TESTING.md)

---

**Document maintenu à jour après chaque changement architectural majeur.**

