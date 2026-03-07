# README_TECH.md - Mathakine

> Documentation technique de référence — Mise à jour le 06/03/2026

---

## 1. Vue d'ensemble

**Mathakine** est une plateforme educative de mathematiques gamifiee avec un theme aventure spatiale.
Elle propose des exercices, des defis logiques, des badges, un chatbot IA et un systeme de recommandations adaptatives.

| Composant | Technologie | Version |
|---|---|---|
| Frontend | Next.js (App Router) + React + TypeScript | 16.1.6 / React 19 |
| Backend | **Starlette** (FastAPI archive) | Starlette 0.x |
| ORM | SQLAlchemy 2.0 | 2.x |
| Base de donnees | PostgreSQL | 15+ |
| Migrations | Alembic | via `migrations/` |
| IA/LLM | OpenAI (GPT-5.1, GPT-5-mini, GPT-5.2) | API |
| CSS | Tailwind CSS | 4.x |
| State (client) | Zustand | 5.x |
| Data fetching | TanStack React Query | 5.x |
| i18n | next-intl | 4.x |
| Animations | Framer Motion | 12.x |

---

## 2. Architecture du projet

```
Mathakine/
├── app/                    # Backend - Couche logique metier
│   ├── api/                #   [Archive] Anciens routers FastAPI
│   │   ├── deps.py         #   Dependencies injection (DB session, auth)
│   │   └── endpoints/      #   Logique metier reutilisable (reference)
│   ├── core/               #   Configuration, sécurité, logging, constantes, types
│   │   ├── types.py        #   TypedDict centralisés (DashboardStats, TokenResponse, AuditLogPageDict…)
│   │   ├── constants.py    #   Hub de re-export constantes (domaines exercise, user, config)
│   │   └── constants_challenge.py  #   Constantes domaine challenges (types, aliases, normalize)
│   ├── db/                 #   Base SQLAlchemy, adapter, queries
│   ├── exceptions.py      #   Exceptions métier (ExerciseNotFoundError, ChallengeNotFoundError, UserNotFoundError, DatabaseOperationError)
│   ├── models/             #   Modeles SQLAlchemy (User, Exercise, Attempt, LogicChallenge, etc.)
│   ├── schemas/            #   Schemas Pydantic (validation API)
│   ├── services/           #   Logique metier (exercise_service, challenge_service, challenge_ai_service, etc.)
│   └── utils/              #   Utilitaires (sse_utils, json_utils, rate_limiter, prompt_sanitizer, error_handler)
│
├── server/                 # Backend - Couche HTTP Starlette (ACTIF)
│   ├── handlers/           #   Handlers HTTP (exercise, challenge, user, auth, chat, badge)
│   ├── app.py              #   Factory de l'app Starlette
│   ├── auth.py             #   Authentification JWT
│   ├── routes/             #   Routes par domaine (core, auth, users, exercises, challenges, badges, admin, misc)
│   ├── middleware.py       #   CORS, logging, securite
│   ├── exercise_generator.py           # Generateur d'exercices IA (streaming SSE)
│   ├── exercise_generator_validators.py  # Validation/normalisation (type, age_group, difficulty)
│   └── exercise_generator_helpers.py     # Choix MCQ, questions contextualisees (generate_smart_choices)
│
├── frontend/               # Frontend Next.js 16
│   ├── app/                #   Pages (App Router) : /, exercises, challenges, dashboard, etc.
│   │   └── api/            #   API Routes Next.js (proxy SSE vers backend)
│   ├── components/         #   Composants React organises par domaine
│   │   ├── challenges/     #     Defis : ChallengeCard, ChallengeSolver, AIGenerator, visualizations/
│   │   ├── exercises/      #     Exercices : ExerciseCard, ExerciseModal, ExerciseSolver, AIGenerator
│   │   ├── dashboard/      #     Tableau de bord : StatsCard, ProgressChart, Recommendations
│   │   ├── layout/         #     Layout : Header, Footer, PageLayout, PageTransition
│   │   ├── ui/             #     Composants UI generiques (shadcn/ui)
│   │   └── spatial/        #     Fond anime (Starfield, Planet, Particles, DinoFloating)
│   ├── hooks/              #   Hooks custom (useAuth, useExercises, useChallenges, etc.)
│   ├── lib/                #   API client, constantes, stores Zustand, utils
│   ├── messages/           #   Fichiers de traduction (fr.json, en.json)
│   └── types/              #   Types TypeScript (api.ts)
│
├── migrations/             # Migrations Alembic
│   └── env.py              #   Configuration Alembic
│
├── tests/                  # Tests (pytest + vitest + playwright)
├── docs/                   # Documentation technique restante
├── _ARCHIVE_2026/          # Fichiers archives (Phase 2 - 231 fichiers)
└── enhanced_server.py      # Point d'entree du serveur
```

---

## 3. Demarrage rapide

### Backend
```bash
# Installer les dependances Python
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec DATABASE_URL, OPENAI_API_KEY, SECRET_KEY

# Lancer le serveur backend (port 8000 par défaut)
python enhanced_server.py
```

### Frontend
```bash
cd frontend

# Installer les dependances Node
npm install

# Configurer l'environnement
cp .env.example .env.local
# Editer .env.local avec NEXT_PUBLIC_API_URL=http://localhost:8000

# Lancer le dev server (port 3000)
npm run dev
```

### Base de donnees
```bash
# Appliquer les migrations Alembic
alembic upgrade head
```

---

## 4. Architecture backend - Starlette pur

Le backend est unifie sur **Starlette** (FastAPI archive le 06/02/2026).

### Couche HTTP - Starlette (`server/`)
- **Point d'entree** : `enhanced_server.py` (port `8000` par defaut via `PORT`)
- **Handlers** : `server/handlers/` (admin, admin_handlers_utils, auth, badge, challenge, chat, exercise, recommendation, user)
- **Gestion DB** : context manager `db_session()` dans les handlers, puis delegation au service d'orchestration
- **Responses** : `JSONResponse` (Starlette)
- **Authentification** : `server/auth.py` (Cookie + Bearer token)
- **Streaming** : SSE pour generation IA (exercices + challenges)
- **Exercise generator** : `exercise_generator.py` + `exercise_generator_validators.py` + `exercise_generator_helpers.py` (choix MCQ, questions contextualisees)
- **Routes** : ~85 routes dans `server/routes/` — agrégées via `get_routes()` (dont bloc admin)
- **Convention B1/B2** : handler = adaptateur HTTP (parse, validation transport, appel service, format response) ; commit final porte par le service proprietaire du flux critique

### Couche logique metier (`app/`)
Couche independante du framework HTTP :
- **Models** : SQLAlchemy ORM (`app/models/`)
- **Schemas** : Pydantic validation (`app/schemas/`)
- **Services** : Logique métier (`app/services/`)
  - `exercise_service.py` — CRUD exercices
  - `exercise_stats_service.py` — Statistiques (extrait 28/02)
  - `challenge_service.py` — CRUD défis (quiz)
  - `challenge_answer_service.py` — 7 algorithmes de comparaison réponses (Phase 3.1)
  - `logic_challenge_service.py` — Défis logiques
  - `user_service.py` — Gestion utilisateurs
  - `auth_service.py` — Authentification, JWT
  - `badge_service.py` — Système de badges
  - `recommendation_service.py` — Recommandations adaptatives
  - `adaptive_difficulty_service.py` — F05 : cascade IRT → progression → profil → fallback (voir [F05_ADAPTATION_DYNAMIQUE](docs/02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md))
  - `diagnostic_service.py` — F03 : test IRT adaptatif, `get_latest_score()` pour recommandations et F05
  - `chat_service.py` — Config et helpers chatbot IA (Phase 3.2)
  - `admin_service.py` — Façade re-exportant les 4 services admin spécialisés
  - `admin_config_service.py` — Config, maintenance, paramètres globaux (Phase 3.3)
  - `admin_stats_service.py` — Dashboard, audit logs, modération, rapports (Phase 3.3)
  - `admin_user_service.py` — Gestion utilisateurs admin (Phase 3.3)
  - `admin_content_service.py` — Exercices, défis, export CSV (Phase 3.3)
  - `enhanced_server_adapter.py` — Adaptateur couche HTTP → services
- **Utils** : Utilitaires (`app/utils/`)
  - `rate_limiter.py` - Limitation taux API
  - `prompt_sanitizer.py` - Securite prompts IA
  - `error_handler.py` - Gestion erreurs
  - `token_tracker.py` - Tracking usage OpenAI
  - `generation_metrics.py` - Metriques generation IA

### FastAPI archive
- **Archive** : `_ARCHIVE_2026/app/main.py` + `_ARCHIVE_2026/app/api/api.py`
- **Raison** : Double architecture Starlette + FastAPI creait confusion
- **Decision** : Starlette pur pour simplicite et coherence
- **Note** : `app/api/endpoints/` conserve (reference logique metier)

---

## 5. Modeles de donnees

| Modele | Table | Description |
|---|---|---|
| `User` | `users` | Utilisateurs (jedi_rank, total_points, avatar) |
| `Exercise` | `exercises` | Exercices mathematiques |
| `Attempt` | `attempts` | Tentatives de reponse |
| `Progress` | `progress` | Progression par type d'exercice |
| `LogicChallenge` | `logic_challenges` | Defis logiques (sequence, deduction, etc.) |
| `Achievement` | `achievements` | Definitions de badges |
| `UserAchievement` | `user_achievements` | Badges debloques par utilisateur |
| `Notification` | `notifications` | Notifications utilisateur |
| `UserSession` | `user_sessions` | Sessions actives |
| `Recommendation` | `recommendations` | Recommandations IA |
| `Setting` | `settings` | Paramètres globaux (admin config) |
| `AdminAuditLog` | `admin_audit_logs` | Log des actions admin |

**Tables legacy** (dans `legacy_tables.py`, conservees en DB) :
- `results`, `statistics`, `user_stats`, `schema_version`

---

## 6. API - Endpoints actifs (~85 routes Starlette)

| Methode | Route | Handler | Description |
|---|---|---|---|
| POST | `/api/auth/login` | auth_handlers | Connexion utilisateur |
| POST | `/api/auth/refresh` | auth_handlers | Rotation access token / refresh token |
| GET | `/api/auth/verify-email` | auth_handlers | Verification email par token |
| POST | `/api/auth/logout` | auth_handlers | Deconnexion |
| POST | `/api/users/` | user_handlers | Inscription utilisateur + token de verification |
| GET | `/api/users/me` | user_handlers | Profil utilisateur actuel |
| PUT | `/api/users/me` | user_handlers | Modifier profil (email, full_name, preferences) |
| PUT | `/api/users/me/password` | user_handlers | Changer mot de passe (CSRF) |
| GET | `/api/users/leaderboard` | user_handlers | Classement par total_points (15/02/2026) |
| GET | `/api/users/stats` | user_handlers | Statistiques utilisateur |
| GET | `/api/users/me/progress` | user_handlers | ✨ Progression exercices (streaks, accuracy) |
| GET | `/api/users/me/challenges/progress` | user_handlers | ✨ Progression defis |
| GET | `/api/daily-challenges` | daily_challenge_handlers | F02 Défis quotidiens (06/03) |
| GET | `/api/users/me/sessions` | user_handlers | ✨ Sessions actives (RGPD) |
| DELETE | `/api/users/me/sessions/{id}` | user_handlers | ✨ Revoquer session |
| GET | `/api/exercises` | exercise_handlers | Liste exercices (filtres, pagination, `order=random`, `hide_completed`) |
| GET | `/api/exercises/stats` | exercise_handlers | ✨ Statistiques Académie (thème gamifié) |
| GET | `/api/exercises/{id}` | exercise_handlers | Detail exercice |
| POST | `/api/exercises/{id}/attempt` | exercise_handlers | Soumettre reponse |
| GET | `/api/challenges` | challenge_handlers | Liste défis (filtres, `order=random`, `hide_completed`) |
| GET | `/api/challenges/{id}` | challenge_handlers | Detail defi |
| POST | `/api/challenges/{id}/attempt` | challenge_handlers | Tenter defi |
| GET | `/api/challenges/{id}/hint` | challenge_handlers | Demander indice |
| GET | `/api/challenges/completed-ids` | challenge_handlers | IDs defis completes |
| GET | `/api/challenges/badges/progress` | badge_handlers | Progression vers badges (16/02) |
| GET | `/api/badges/user` | badge_handlers | Badges utilisateur |
| GET | `/api/badges/available` | badge_handlers | Liste badges disponibles |
| GET | `/api/recommendations` | recommendation_handlers | Recommandations IA |
| POST | `/api/recommendations/complete` | recommendation_handlers | Marquer recommandation faite (16/02) |
| POST | `/api/chat` | chat_handlers | Chatbot IA |
| POST | `/api/chat/stream` | chat_handlers | Chatbot streaming |

### Admin (rôle archiviste) — 25 routes

| Domaine | Routes |
|---------|--------|
| Overview | `GET /api/admin/overview`, `health` |
| Users | `GET/PATCH /api/admin/users`, `send-reset-password`, `resend-verification` |
| Exercises | `GET/POST/PUT/PATCH /api/admin/exercises`, `duplicate` |
| Challenges | `GET/POST/PUT/PATCH /api/admin/challenges`, `duplicate` |
| Modération | `GET /api/admin/moderation` |
| Audit | `GET /api/admin/audit-log` |
| Config | `GET/PUT /api/admin/config` |
| Export | `GET /api/admin/export` |
| Reports | `GET /api/admin/reports` |

→ Voir `docs/02-FEATURES/API_QUICK_REFERENCE.md` pour la liste complète.

**Note** : Les routes de generation IA (SSE) sont dans `frontend/app/api/` (proxy Next.js vers backend). Routes auth frontend : `POST /api/auth/sync-cookie`, `GET /api/auth/check-cookie` (diagnostic).

**Legende** :
- ✨ = Nouveaux endpoints ajoutes le 06/02/2026
- 15/02 = Leaderboard, modification profil/mot de passe

---

## 7. Frontend - Patterns et conventions

### API Client
Toutes les requetes passent par `frontend/lib/api/client.ts` qui gere :
- Token Bearer automatique
- Refresh token
- Header `Accept-Language`
- Gestion d'erreurs centralisee

**Exception** : Les endpoints SSE (streaming IA, chat) utilisent `fetch()` direct ou `EventSource` car le client ne supporte pas le streaming.

**Prod cross-domain** : Frontend et backend sur domaines differents (ex. Render) → le cookie backend n'est pas envoye aux routes Next.js. Le flux `sync-cookie` copie le token sur le domaine frontend (login, refresh, `ensureFrontendAuthCookie()` avant generation IA). Voir `docs/01-GUIDES/TROUBLESHOOTING.md` si erreur « Cookie manquant ».

### Hooks (~30 hooks custom)
Chaque domaine a son hook dedie base sur React Query :
- `useAuth` - login/register/logout + gestion token
- `useExercises` / `useExercise` - CRUD exercices + pagination
- `useChallenges` / `useChallenge` - CRUD defis + pagination
- `useBadges` - Liste et verification de badges
- `useBadgesProgress` - Progression vers badges (16/02)
- `useProfile` / `useUserStats` - Donnees utilisateur
- `useProgressStats` - ✨ Progression exercices (streaks, accuracy)
- `useChallengesProgress` - ✨ Progression defis
- `useDailyChallenges` - F02 Défis quotidiens (06/03)
- `useSettings` - ✨ Sessions utilisateur (RGPD)
- `useRecommendations` - Recommandations adaptatives (avec mutation `complete`)
- `useSubmitAnswer` - Soumission de reponses
- `useChat` - Chatbot IA
- `useChallengeTranslations` - Traductions types challenges
- `useCompletedItems` - IDs exercices/challenges completes

**Note** : ✨ = Ajoutes le 06/02/2026 ; 16/02 = badges progress, recommendations complete, sessions

### State management
- **Zustand** : theme, locale, accessibilite (persistence localStorage)
- **React Query** : toutes les donnees serveur (cache, revalidation)
- **useState** : etat local de composant

### i18n
- `next-intl` avec fichiers `messages/fr.json` et `messages/en.json`
- Hook `useTranslations('namespace')` dans chaque composant

---

## 8. Generation IA

Le systeme utilise l'API OpenAI pour generer des exercices et defis :

| Fonctionnalite | Modele | Endpoint |
|---|---|---|
| Exercices simples | GPT-5-mini | `/api/exercises/generate-ai-stream` |
| Defis logiques | GPT-5.1 | `/api/challenges/generate-ai-stream` |
| Chatbot educatif | GPT-5.2 | `/api/chat` |

**Securite IA** :
- Sanitisation des prompts (`app/utils/prompt_sanitizer.py`)
- Rate limiting par utilisateur (`app/utils/rate_limiter.py`)
- Suivi des tokens consommes (`app/utils/token_tracker.py`)
- Authentification requise sur tous les endpoints IA

---

## 9. Incoherences connues et dette technique

### Resolues (06/02/2026 soir)
| ID | Description | Resolution |
|---|---|---|
| ~~FIX-1~~ | ~~Dark mode ne bascule pas~~ | Selecteurs CSS corriges (`.dark[data-theme]` vs `.dark [data-theme]`) |
| ~~FIX-2~~ | ~~Bouton accessibilite invisible~~ | React Portal dedie + z-index 99999 |
| ~~FIX-3~~ | ~~Generation IA "non authentifie"~~ | Cookies via `request.cookies.getAll()` + sync-cookie cross-domain (prod) |
| ~~FIX-4~~ | ~~Erreur `max_completion_tokens`~~ | Dependance `openai>=1.40.0` |
| ~~FIX-5~~ | ~~Index DB manquants~~ | 4 migrations Alembic (13 index) |

### Resolues (06/02/2026 matin)
| ID | Description | Resolution |
|---|---|---|
| ~~INC-B5~~ | ~~3 patterns de logging~~ | Unifie sur `get_logger(__name__)` (35 fichiers corriges) |
| ~~INC-B4~~ | ~~3 implementations de `get_current_user`~~ | Consolidee dans `server/auth.py`, copies supprimees |
| ~~INC-B3~~ | ~~Cle erreur `detail` vs `error`~~ | Standardisee sur `"error"` cote Starlette |
| ~~INC-F3~~ | ~~Toasts non traduits dans les hooks~~ | Branches sur `next-intl` (4 hooks corriges) |
| ~~INC-B1~~ | ~~Double architecture Starlette + FastAPI~~ | **FastAPI archive** (`app/main.py`, `app/api/api.py` -> `_ARCHIVE_2026/`) - Architecture unifiee sur **Starlette pur** |
| ~~INC-F1~~ | ~~Strings FR en dur dans composants~~ | **~80 strings extraites** vers i18n (14 composants + visualizations) |
| ~~QW-B1~~ | ~~`print()` en backend~~ | Convertis en `logger.*` (27 occurrences, 8 fichiers) |
| ~~QW-F1~~ | ~~`console.log` non proteges~~ | Supprimes (4 instances dans `generate-ai-stream`) |
| ~~TODO-A~~ | ~~Endpoints sessions manquants~~ | **Implementes** : `GET/DELETE /api/users/me/sessions` (securite RGPD) |
| ~~TODO-B~~ | ~~Donnees progression en dur~~ | **Remplacees** par vraies stats depuis DB (`attempts`, `logic_challenge_attempts`) |

### Restantes
| Priorite | ID | Description | Fichiers concernes |
|---|---|---|---|
| Basse | INC-B6 | Imports lazy dans les handlers Starlette (~50 occurrences) | `server/handlers/` |
| Info | INC-F2 | Streaming hors client API (normal pour SSE, documente) | `AIGenerator.tsx`, `chat.ts` |
| Info | PLACEHOLDERS | 13 endpoints placeholders (non-bloquants, doc disponible) | Voir `docs/PLACEHOLDERS_ET_TODO.md` |

### Endpoints progression integres (06/02/2026, MAJ 06/03)
| Endpoint | Description | Utilisation frontend |
|---|---|---|
| `GET /api/daily-challenges` | F02 Défis quotidiens (3 par jour) | ✅ `useDailyChallenges` → DailyChallengesWidget |
| `GET /api/users/me/progress` | Stats exercices : streaks, accuracy, par categorie | ✅ `useProgressStats` → StreakWidget, CategoryAccuracyChart |
| `GET /api/users/me/challenges/progress` | Stats defis : completes, temps, liste detaillee | ✅ `useChallengesProgress` → ChallengesProgressWidget |
| `GET /api/users/me/sessions` | Sessions actives (is_current sur session courante) | ✅ `useSettings` → page /settings |
| `GET /api/challenges/badges/progress` | Progression vers badges verrouilles | ✅ `useBadgesProgress` → page /badges |
| `POST /api/recommendations/complete` | Marquer recommandation comme faite | ✅ `useRecommendations` → dashboard Recommandations |

**Plateforme** : `maintenance_mode` (overlay frontend + 503 sauf /login, /admin, health), `registration_enabled` (403 sur POST /api/users/ si false). UserSession creee a chaque login.

**Doc complete** : `docs/06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md`, `docs/02-FEATURES/F02_DEFIS_QUOTIDIENS.md`, `docs/03-PROJECT/REFACTOR_DASHBOARD_2026-03.md`

### Plan d'alignement futur
1. **P1** : Remonter les imports lazy en haut des fichiers `server/handlers/` (amelioration perfs)
2. **P2** : Fixture defis pour tests (8 skips « No challenges »), delete_user admin (RGPD) - voir `docs/PLACEHOLDERS_ET_TODO.md`

---

## 10. Archive

Le dossier `_ARCHIVE_2026/` contient les fichiers archives :

| Categorie | Contenu | Date archivage |
|---|---|---|
| `root/` | Fichiers racine obsoletes (output.txt, coverage.xml, Dockerfile) | Phase 2 (2025-11) |
| `static/` | Ancien frontend Jinja2 (26 fichiers HTML/CSS/JS) | Phase 2 (2025-11) |
| `server/` | Handlers ghost (simple_views, api_routes, api_challenges) | Phase 2 (2025-11) |
| `app/` | Code backend mort (enum_helpers, queries_translations, user_extended) | Phase 2 (2025-11) |
| `app/main.py` + `app/api/api.py` | ✨ **FastAPI archive** (double architecture) | 06/02/2026 |
| `frontend/` | Composants morts (PatternSolver, LogicGrid, ThemeSelector) | Phase 2 (2025-11) |

**Note archivage FastAPI** : Voir `_ARCHIVE_2026/FASTAPI_ARCHIVE_NOTE.md` pour details et procedure de restauration.
| `migrations-orphan/` | Ancien dossier alembic/ + SQL orphelins |
| `scripts/` | ~153 scripts utilitaires non utilises |
| `docs/` | Documentation obsolete (ARCHITECTURE, API, CHANGELOG, etc.) |

**Regle** : aucun fichier n'a ete supprime, tout est deplacable si besoin.

---

## 11. Commandes utiles

```bash
# Backend
python enhanced_server.py                    # Demarrer le serveur (port 8000 par defaut)
alembic upgrade head                         # Appliquer les migrations
alembic revision --autogenerate -m "desc"    # Generer une migration

# Frontend
cd frontend && npm run dev                   # Dev server (port 3000)
cd frontend && npx next build                # Build de production
cd frontend && npm test                      # Tests unitaires (vitest)
cd frontend && npx playwright test           # Tests E2E

# Tests et qualite Python
pytest tests/                                # Lancer les tests pytest
mypy app/ server/ --ignore-missing-imports   # Typage statique (CI)
black app/ server/ && isort app/ server/    # Formatage (pre-commit)
```

---

*Derniere mise a jour : 06/03/2026 - Stabilisation B1/B2 backend, auth/session, daily challenges, handlers critiques alleges*
