# README_TECH.md - Mathakine

> Documentation technique de reference - Mise a jour le 11/03/2026 (iterations backend exercise/auth/user et challenge/admin/badge cloturees, release 3.1.0-alpha.8)

---

## 1. Vue d'ensemble

**Mathakine** est une plateforme educative de mathematiques gamifiee avec un theme aventure spatiale.
Elle propose des exercices, des defis logiques, des badges, un chatbot IA et un systeme de recommandations adaptatives.

Mises a jour recentes:
- F07: timeline progression 7j/30j (`/api/users/me/progress/timeline`)
- F32: session entrelacee (interleaving) via plan dedie (`/api/exercises/interleaved-plan`)
- F35: redaction des secrets URL DB au demarrage (`redact_database_url_for_log`)
- 09/03: iteration backend `exercise/auth/user` cloturee - handlers amincis, services applicatifs isoles, repos `exercise`, auth session/recovery et boundary user stabilises
- 11/03: iteration backend `challenge/admin/badge` cloturee - boundaries query/attempt/stream challenge, read/write admin et facade badge isolees, preuves API ciblees ajoutees
- 09/03: reset password ET changement de mot de passe invalident desormais les anciens tokens et sessions via `password_changed_at` + `iat`

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
|-- app/                    # Backend - logique metier et acces data
|   |-- api/                #   [Archive] anciens endpoints FastAPI
|   |-- core/               #   config, securite, logging, constantes, types
|   |-- db/                 #   base SQLAlchemy, adapter, transactions
|   |-- exceptions.py       #   exceptions metier
|   |-- generators/         #   generateurs d'exercices (source de verite backend)
|   |-- models/             #   modeles SQLAlchemy
|   |-- repositories/       #   acces data isole (exercise, attempts)
|   |-- schemas/            #   schemas Pydantic
|   |-- services/           #   services applicatifs et metier
|   `-- utils/              #   helpers transverses
|
|-- server/                 # Backend - couche HTTP Starlette (actif)
|   |-- handlers/           #   controllers HTTP anemiques
|   |-- routes/             #   routes par domaine
|   |-- app.py              #   factory Starlette
|   |-- auth.py             #   auth runtime / decorators
|   |-- middleware.py       #   CORS, securite, auth middleware
|   |-- exercise_generator.py            # compat re-export -> app/generators
|   |-- exercise_generator_validators.py # compat re-export -> app/utils
|   `-- exercise_generator_helpers.py    # compat re-export -> app/utils
|
|-- frontend/               # Frontend Next.js 16
|   |-- app/                #   pages App Router + API routes Next.js
|   |-- components/         #   composants React par domaine
|   |-- hooks/              #   hooks custom
|   |-- lib/                #   client API, stores, analytics, utils
|   |-- messages/           #   traductions fr/en
|   `-- types/              #   types TypeScript
|
|-- migrations/             # Migrations Alembic
|-- tests/                  # Tests pytest / vitest
|-- docs/                   # Documentation projet
|-- _ARCHIVE_2026/          # Archives historiques
`-- enhanced_server.py      # Point d'entree du serveur
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

# Lancer le serveur backend (port 8000 par dÃ©faut)
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
- **Handlers** : `server/handlers/` (admin, auth, badge, challenge, chat, exercise, recommendation, user)
- **DB ownership** : sur les boundaries refactorees `exercise`, `auth`, `user`, `challenge`, `admin` et `badge`, les handlers n'ouvrent plus la DB sur le scope traite ; les services applicatifs portent `db_session()` et l'orchestration.
- **Responses** : `JSONResponse`, `TemplateResponse`, `StreamingResponse` selon le flux
- **Authentification** : `server/auth.py` (cookie + bearer) avec rejet des tokens revoques
- **Streaming** : SSE pour generation IA (exercices + defis)
- **Compat generateur** : `server/exercise_generator*.py` sont des couches de compatibilite re-exportant vers `app/generators` et `app/utils`
- **Routes** : ~95 routes dans `server/routes/` agregees via `get_routes()`
- **Convention B1/B2** : handler = adaptateur HTTP (parse, validation transport, appel service, format response) ; le service proprietaire porte la transaction du flux critique

### Couche logique metier (`app/`)
Couche independante du framework HTTP :
- **Models** : SQLAlchemy ORM (`app/models/`)
- **Schemas** : Pydantic validation (`app/schemas/`)
- **Repositories** : acces data isole (`app/repositories/exercise_repository.py`, `app/repositories/exercise_attempt_repository.py`)
- **Generators** : source de verite pour la generation d'exercices (`app/generators/exercise_generator.py`)
- **Services application/metier** :
  - `exercise_generation_service.py`, `exercise_attempt_service.py`, `exercise_query_service.py`, `exercise_stream_service.py`
  - `exercise_service.py`, `exercise_stats_service.py`, `interleaved_practice_service.py`
  - `auth_service.py`, `auth_session_service.py`, `auth_recovery_service.py`
  - `user_service.py`, `user_application_service.py`
  - `challenge_query_service.py`, `challenge_attempt_service.py`, `challenge_stream_service.py`, `challenge_service.py`, `challenge_answer_service.py`, `challenge_validator.py`, `challenge_ai_service.py
  - `badge_service.py`, `badge_application_service.py`, `recommendation_service.py`, `diagnostic_service.py`, `adaptive_difficulty_service.py`, `progress_timeline_service.py
  - `admin_service.py`, `admin_read_service.py`, `admin_application_service.py` et services specialises `admin_*`
  - `enhanced_server_adapter.py` reste une facade legacy de transition, plus la source de verite des boundaries refactorees
- **Utils** : `prompt_sanitizer.py`, `rate_limiter.py`, `token_tracker.py`, `exercise_generator_validators.py`, `exercise_generator_helpers.py`, etc.
- **Securite auth** : `users.password_changed_at` invalide les anciens access/refresh tokens via le claim JWT `iat` apres reset password ou changement de mot de passe

### FastAPI archive
- **Archive** : `_ARCHIVE_2026/app/main.py` + `_ARCHIVE_2026/app/api/api.py`
- **Raison** : Double architecture Starlette + FastAPI creait confusion
- **Decision** : Starlette pur pour simplicite et coherence
- **Note** : `app/api/endpoints/` conserve (reference logique metier)

---

## 5. Modeles de donnees

| Modele | Table | Description |
|---|---|---|
| `User` | `users` | Utilisateurs (profil, gamification, `password_changed_at` pour la revocation auth) |
| `Exercise` | `exercises` | Exercices mathematiques |
| `Attempt` | `attempts` | Tentatives de reponse |
| `Progress` | `progress` | Progression par type d'exercice |
| `LogicChallenge` | `logic_challenges` | Defis logiques (sequence, deduction, etc.) |
| `Achievement` | `achievements` | Definitions de badges |
| `UserAchievement` | `user_achievements` | Badges debloques par utilisateur |
| `Notification` | `notifications` | Notifications utilisateur |
| `UserSession` | `user_sessions` | Sessions actives (revoquees sur reset/changement de mot de passe) |
| `Recommendation` | `recommendations` | Recommandations IA |
| `Setting` | `settings` | ParamÃ¨tres globaux (admin config) |
| `AdminAuditLog` | `admin_audit_logs` | Log des actions admin |

**Tables legacy** (dans `legacy_tables.py`, conservees en DB) :
- `results`, `statistics`, `user_stats`, `schema_version`

---

## 6. API - Endpoints actifs (~95 routes Starlette)

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
| GET | `/api/users/me/progress` | user_handlers | âœ¨ Progression exercices (streaks, accuracy) |
| GET | `/api/users/me/progress/timeline` | user_handlers | F07 Evolution temporelle (7d/30d) |
| GET | `/api/users/me/challenges/progress` | user_handlers | âœ¨ Progression defis |
| GET | `/api/daily-challenges` | daily_challenge_handlers | F02 DÃ©fis quotidiens (06/03) |
| GET | `/api/users/me/sessions` | user_handlers | âœ¨ Sessions actives (RGPD) |
| DELETE | `/api/users/me/sessions/{id}` | user_handlers | âœ¨ Revoquer session |
| GET | `/api/exercises` | exercise_handlers | Liste exercices (filtres, pagination, `order=random`, `hide_completed`) |
| GET | `/api/exercises/stats` | exercise_handlers | âœ¨ Statistiques AcadÃ©mie (thÃ¨me gamifiÃ©) |
| GET | `/api/exercises/interleaved-plan` | exercise_handlers | F32 Plan session entrelacee (`409 not_enough_variety`) |
| GET | `/api/exercises/{id}` | exercise_handlers | Detail exercice |
| POST | `/api/exercises/{id}/attempt` | exercise_handlers | Soumettre reponse |
| POST | `/api/exercises/generate` | exercise_handlers | Generation exercice (auth optionnelle, `age_group?`, `adaptive?`, `save?`) ; si `save=true`, reponse avec `id` persiste ou erreur `500` |
| GET | `/api/challenges` | challenge_handlers | Liste dÃ©fis (filtres, `order=random`, `hide_completed`) |
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

### Admin (rÃ´le archiviste) â€” 34 routes

| Domaine | Routes |
|---------|--------|
| Overview | `GET /api/admin/overview`, `health` |
| Users | `GET/PATCH /api/admin/users`, `send-reset-password`, `resend-verification` |
| Exercises | `GET/POST/PUT/PATCH /api/admin/exercises`, `duplicate` |
| Challenges | `GET/POST/PUT/PATCH /api/admin/challenges`, `duplicate` |
| ModÃ©ration | `GET /api/admin/moderation` |
| Audit | `GET /api/admin/audit-log` |
| Config | `GET/PUT /api/admin/config` |
| Export | `GET /api/admin/export` |
| Reports | `GET /api/admin/reports` |

â†’ Voir `docs/02-FEATURES/API_QUICK_REFERENCE.md` pour la liste complÃ¨te.

**Note** : Les routes de generation IA (SSE) sont dans `frontend/app/api/` (proxy Next.js vers backend). Routes auth frontend : `POST /api/auth/sync-cookie`, `GET /api/auth/check-cookie` (diagnostic).

**Legende** :
- âœ¨ = Nouveaux endpoints ajoutes le 06/02/2026
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

**Prod cross-domain** : Frontend et backend sur domaines differents (ex. Render) â†’ le cookie backend n'est pas envoye aux routes Next.js. Le flux `sync-cookie` copie le token sur le domaine frontend (login, refresh, `ensureFrontendAuthCookie()` avant generation IA). Voir `docs/01-GUIDES/TROUBLESHOOTING.md` si erreur Â« Cookie manquant Â».

### Hooks (~30 hooks custom)
Chaque domaine a son hook dedie base sur React Query :
- `useAuth` - login/register/logout + gestion token
- `useExercises` / `useExercise` - CRUD exercices + pagination
- `useChallenges` / `useChallenge` - CRUD defis + pagination
- `useBadges` - Liste et verification de badges
- `useBadgesProgress` - Progression vers badges (16/02)
- `useProfile` / `useUserStats` - Donnees utilisateur
- `useProgressStats` - âœ¨ Progression exercices (streaks, accuracy)
- `useChallengesProgress` - âœ¨ Progression defis
- `useDailyChallenges` - F02 DÃ©fis quotidiens (06/03)
- `useProgressTimeline` - F07 Timeline progression (7j/30j)
- `useSettings` - âœ¨ Sessions utilisateur (RGPD)
- `useRecommendations` - Recommandations adaptatives (avec mutation `complete`)
- `useSubmitAnswer` - Soumission de reponses
- `useChat` - Chatbot IA
- `useChallengeTranslations` - Traductions types challenges
- `useCompletedItems` - IDs exercices/challenges completes

**Note** : âœ¨ = Ajoutes le 06/02/2026 ; 16/02 = badges progress, recommendations complete, sessions

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

### Resolues (07/03/2026)
| ID | Description | Resolution |
|---|---|---|
| ~~F32~~ | ~~Pas de mode session entrelacee guidee~~ | Endpoint `GET /api/exercises/interleaved-plan`, CTA Quick Start, flux `session=interleaved` cote frontend |
| ~~F35~~ | ~~URL DB complete loggee au demarrage~~ | Redaction via `redact_database_url_for_log()` + tests unitaires dedies |

### Resolues (08/03/2026)
| ID | Description | Resolution |
|---|---|---|
| ~~INC-A1~~ | ~~Les analytics `interleaved` surcomptent les `first_attempt`~~ | Etat `sessionStorage` enrichi avec `analytics.firstAttemptTracked`, emission unique par session et test unitaire frontend dedie |
| ~~INC-B7~~ | ~~`POST /api/exercises/generate` peut repondre `200` sans `id` quand `save=true`~~ | Contrat durci : erreur `500` si la sauvegarde echoue ou ne retourne pas d'identifiant persiste |
| ~~INC-B8~~ | ~~Resolution adaptive `age_group` dupliquee dans deux handlers~~ | Helper prive `_resolve_adaptive_age_group_if_needed()` partage entre `generate_exercise` et `generate_exercise_api` |
| ~~INC-Q2~~ | ~~Quality gate Python et hygiene repo non fiables~~ | `black app/ server/ tests/ --check` remis au vert, test UTF-8 nettoye, `frontend/junit.xml` retire de l'index git et `.gitignore` assaini |

### Endpoints progression integres (06/02/2026, MAJ 06/03)
| Endpoint | Description | Utilisation frontend |
|---|---|---|
| `GET /api/daily-challenges` | F02 DÃ©fis quotidiens (3 par jour) | âœ… `useDailyChallenges` â†’ DailyChallengesWidget |
| `GET /api/users/me/progress` | Stats exercices : streaks, accuracy, par categorie | âœ… `useProgressStats` â†’ StreakWidget, CategoryAccuracyChart |
| `GET /api/users/me/challenges/progress` | Stats defis : completes, temps, liste detaillee | âœ… `useChallengesProgress` â†’ ChallengesProgressWidget |
| `GET /api/users/me/sessions` | Sessions actives (is_current sur session courante) | âœ… `useSettings` â†’ page /settings |
| `GET /api/challenges/badges/progress` | Progression vers badges verrouilles | âœ… `useBadgesProgress` â†’ page /badges |
| `POST /api/recommendations/complete` | Marquer recommandation comme faite | âœ… `useRecommendations` â†’ dashboard Recommandations |

**Plateforme** : `maintenance_mode` (overlay frontend + 503 sauf /login, /admin, health), `registration_enabled` (403 sur POST /api/users/ si false). UserSession creee a chaque login.

**Doc complete** : `docs/06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md`, `docs/02-FEATURES/F02_DEFIS_QUOTIDIENS.md`, `docs/03-PROJECT/REFACTOR_DASHBOARD_2026-03.md`

### Plan d'alignement futur
1. **P1** : Remonter les imports lazy en haut des fichiers `server/handlers/` (amelioration perfs)
2. **P2** : Fixture defis pour tests (8 skips Â« No challenges Â»), delete_user admin (RGPD) - voir `docs/PLACEHOLDERS_ET_TODO.md`

---

## 10. Archive

Le dossier `_ARCHIVE_2026/` contient les fichiers archives :

| Categorie | Contenu | Date archivage |
|---|---|---|
| `root/` | Fichiers racine obsoletes (output.txt, coverage.xml, Dockerfile) | Phase 2 (2025-11) |
| `static/` | Ancien frontend Jinja2 (26 fichiers HTML/CSS/JS) | Phase 2 (2025-11) |
| `server/` | Handlers ghost (simple_views, api_routes, api_challenges) | Phase 2 (2025-11) |
| `app/` | Code backend mort (enum_helpers, queries_translations, user_extended) | Phase 2 (2025-11) |
| `app/main.py` + `app/api/api.py` | âœ¨ **FastAPI archive** (double architecture) | 06/02/2026 |
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
black app/ server/ tests/                   # Formatage Python
isort app/ server/                         # Tri imports backend
```

---

*Derniere mise a jour : 11/03/2026 - iterations backend exercise/auth/user et challenge/admin/badge cloturees, release 3.1.0-alpha.8*

