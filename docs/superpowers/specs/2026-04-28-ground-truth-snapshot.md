# Ground Truth Snapshot — Mathakine v3.6.0-beta.5
**Date :** 2026-04-28 | **Commit :** da794f4

## Version & Runtime
- Version : 3.6.0-beta.5 (settings.PROJECT_VERSION confirmé dans app/core/config.py)
- Entrypoint ASGI : `enhanced_server:app`
- Serveur : `gunicorn enhanced_server:app --worker-class uvicorn.workers.UvicornWorker`
- Framework : Starlette (FastAPI archivé 06/02/2026 — confirmé dans enhanced_server.py docstring)
- Port dev/prod : 10000 (variable PORT, défaut 10000)
- Host : 0.0.0.0 (variable MATH_TRAINER_HOST)

## Architecture couches
- `enhanced_server.py` — entrypoint ASGI, charge .env hors prod
- `server/routes/*.py` — déclaration des Route Starlette par domaine
- `server/handlers/*.py` — handlers HTTP minces (auth, exercise, challenge, user, badge, admin, analytics, feedback, recommendation, chat, diagnostic, daily_challenge)
- `app/services/` — logique métier
- `app/core/` — config, ai_config, logging, monitoring, policy modèles IA
- Monitoring : `/metrics` → Prometheus via `app.core.monitoring.metrics_endpoint`
- Readiness : `/ready` → `app.utils.readiness_probe.run_readiness_checks` (DB + Redis prod)

## Routes actives complètes

### Core (server/routes/core.py)
| Méthode | Path |
|---------|------|
| GET, HEAD | `/` |
| GET | `/live` |
| GET | `/ready` |
| GET | `/health` (alias readiness) |
| GET | `/robots.txt` |
| GET | `/metrics` |

### Auth (server/routes/auth.py)
| Méthode | Path |
|---------|------|
| POST | `/api/auth/login` |
| GET  | `/api/auth/csrf` |
| POST | `/api/auth/validate-token` |
| POST | `/api/auth/refresh` |
| POST | `/api/auth/logout` |
| POST | `/api/auth/forgot-password` |
| POST | `/api/auth/reset-password` |
| GET  | `/api/auth/verify-email` |
| POST | `/api/auth/resend-verification` |

### Exercises (server/routes/exercises.py)
| Méthode | Path |
|---------|------|
| GET  | `/api/exercises` |
| GET  | `/api/exercises/stats` |
| GET  | `/api/exercises/interleaved-plan` |
| GET  | `/api/exercises/{exercise_id:int}` |
| POST | `/api/exercises/generate` |
| POST | `/api/exercises/generate-ai-stream` |
| GET  | `/api/exercises/completed-ids` |
| POST | `/api/exercises/{exercise_id:int}/attempt` |

### Challenges (server/routes/challenges.py)
| Méthode | Path |
|---------|------|
| GET  | `/api/challenges` |
| GET  | `/api/challenges/stats` |
| GET  | `/api/challenges/{challenge_id:int}` |
| POST | `/api/challenges/{challenge_id:int}/attempt` |
| GET  | `/api/challenges/{challenge_id:int}/hint` |
| GET  | `/api/challenges/completed-ids` |
| POST | `/api/challenges/generate-ai-stream` |

### Users (server/routes/users.py)
| Méthode | Path |
|---------|------|
| GET    | `/api/users/` |
| POST   | `/api/users/` |
| GET    | `/api/users/me` |
| PUT    | `/api/users/me` |
| PUT    | `/api/users/me/password` |
| DELETE | `/api/users/me` |
| GET    | `/api/users/me/export` |
| GET    | `/api/users/me/sessions` |
| DELETE | `/api/users/me/sessions/{session_id:int}` |
| GET    | `/api/users/me/progress/timeline` |
| GET    | `/api/users/me/progress` |
| GET    | `/api/users/me/challenges/progress` |
| GET    | `/api/users/me/challenges/detailed-progress` |
| GET    | `/api/users/me/rank` |
| GET    | `/api/users/me/reviews/next` |
| GET    | `/api/daily-challenges` |
| GET    | `/api/users/stats` |
| GET    | `/api/users/leaderboard` |
| DELETE | `/api/users/{user_id:int}` |

### Badges (server/routes/badges.py)
| Méthode | Path |
|---------|------|
| GET   | `/api/badges/user` |
| GET   | `/api/badges/available` |
| POST  | `/api/badges/check` |
| GET   | `/api/badges/stats` |
| GET   | `/api/badges/rarity` |
| PATCH | `/api/badges/pin` |
| GET   | `/api/challenges/badges/progress` |

### Diagnostic (server/routes/diagnostic.py)
| Méthode | Path |
|---------|------|
| GET  | `/api/diagnostic/status` |
| POST | `/api/diagnostic/start` |
| POST | `/api/diagnostic/question` |
| POST | `/api/diagnostic/answer` |
| POST | `/api/diagnostic/complete` |

### Misc — analytics, feedback, recommendations, chat (server/routes/misc.py)
| Méthode | Path |
|---------|------|
| POST | `/api/analytics/event` |
| POST | `/api/feedback` |
| GET  | `/api/recommendations` |
| POST | `/api/recommendations/generate` |
| POST | `/api/recommendations/open` |
| POST | `/api/recommendations/clicked` (alias stable de /open) |
| POST | `/api/recommendations/complete` |
| POST | `/api/chat` |
| POST | `/api/chat/stream` |

### Admin — Mount `/api/admin` (server/routes/admin.py)
| Méthode | Path |
|---------|------|
| GET    | `/api/admin/health` |
| GET    | `/api/admin/overview` |
| GET    | `/api/admin/observability/f43-account-progression` |
| GET    | `/api/admin/users` |
| PATCH  | `/api/admin/users/{user_id:int}` |
| POST   | `/api/admin/users/{user_id:int}/send-reset-password` |
| POST   | `/api/admin/users/{user_id:int}/resend-verification` |
| DELETE | `/api/admin/users/{user_id:int}` |
| GET    | `/api/admin/exercises` |
| POST   | `/api/admin/exercises` |
| POST   | `/api/admin/exercises/{exercise_id:int}/duplicate` |
| GET    | `/api/admin/exercises/{exercise_id:int}` |
| PUT    | `/api/admin/exercises/{exercise_id:int}` |
| PATCH  | `/api/admin/exercises/{exercise_id:int}` |
| GET    | `/api/admin/challenges` |
| POST   | `/api/admin/challenges` |
| POST   | `/api/admin/challenges/{challenge_id:int}/duplicate` |
| GET    | `/api/admin/challenges/{challenge_id:int}` |
| PUT    | `/api/admin/challenges/{challenge_id:int}` |
| PATCH  | `/api/admin/challenges/{challenge_id:int}` |
| GET    | `/api/admin/reports` |
| GET    | `/api/admin/feedback` |
| PATCH  | `/api/admin/feedback/{feedback_id:int}` |
| DELETE | `/api/admin/feedback/{feedback_id:int}` |
| GET    | `/api/admin/audit-log` |
| GET    | `/api/admin/moderation` |
| GET    | `/api/admin/config` |
| PUT    | `/api/admin/config` |
| GET    | `/api/admin/export` |
| GET    | `/api/admin/badges` |
| POST   | `/api/admin/badges` |
| GET    | `/api/admin/badges/{badge_id:int}` |
| PUT    | `/api/admin/badges/{badge_id:int}` |
| DELETE | `/api/admin/badges/{badge_id:int}` |
| GET    | `/api/admin/analytics/edtech` |
| GET    | `/api/admin/ai-stats` |
| GET    | `/api/admin/generation-metrics` |
| GET    | `/api/admin/ai-eval-harness-runs` |

## IA — Défis

### Modèle par défaut
- `DEFAULT_CHALLENGES_AI_MODEL = "o4-mini"` (challenge_ai_model_policy.py)
- `DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL = "gpt-4o-mini"` (secours si stream o-series vide)

### Carte par type (CHALLENGE_MODEL_BY_TYPE)
Tous les types utilisent `o4-mini` : pattern, sequence, puzzle, graph, visual, riddle, deduction, coding, chess, probability.

### Hiérarchie de résolution (du plus prioritaire au moins prioritaire)
1. `OPENAI_MODEL_CHALLENGES_OVERRIDE` — override ops explicite pipeline défis
2. `OPENAI_MODEL_REASONING` — legacy, conservé pour compatibilité déploiements existants
3. `CHALLENGE_MODEL_BY_TYPE` — carte par type (actuellement uniforme o4-mini)
4. `DEFAULT_CHALLENGES_AI_MODEL` — si type inconnu

### Fallback stream
- Déclenché uniquement si le stream principal est o-series ET renvoie contenu vide
- Override : `OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE` > `DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL`

### Paramètres IA (AIConfig)
- Deux matrices reasoning effort : `REASONING_EFFORT_MAP` (GPT-5.x) et `O_SERIES_REASONING_EFFORT_BY_TYPE` (o-series)
- o-series : effort medium pour pattern/graph/visual/deduction/coding, low pour le reste
- GPT-5.x : effort high pour pattern/visual/deduction, medium pour graph/coding, low pour le reste
- `O_SERIES_MAX_TOKENS_MULTIPLIER = 1.4` (compense reasoning tokens cachés)
- Timeout par défaut : 90s ; max : 180s ; chess : 90s
- Max retries : 3 (chess : 1)
- response_format JSON : mode `json_object` (structured outputs `json_schema` non démarrés)
- temperature uniquement si reasoning.effort = none (GPT-5.x)

### VarietySeed (lot Qualité — commits 74ffb14→33bb325)
- Dataclass `VarietySeed(narrative_context, resolution_mechanism, cognitive_skill="", min_level="")`
- `cognitive_skill` et `min_level` : réservés, non actifs
- Types sans contexte narratif : `chess`, `visual`, `pattern` (`_TYPES_IGNORE_NARRATIVE`)
- Mécanismes riddle séparés : all-ages vs advanced (groupes 12-14, 15-17, adulte)
- Seed = suggestion faible ; type, âge et contrat visual_data restent absolus

## Phases défis IA (état au 2026-04-28)
- Phase 0 (o4-mini migration) : LIVRÉE (beta.4, 2026-04-24)
- Phase 1A (pipeline statuses) : LIVRÉE
- Phase 1B (error codes) : LIVRÉE
- Phase 2A (metrics observabilité) : LIVRÉE
- Phase 2B (generation_confidence) : LIVRÉE
- Phase 3A (golden tests) : LIVRÉE
- Phase 3B (renderer contracts) : LIVRÉE
- Phase 3D (deduction solver perf) : LIVRÉE
- Phase 3C (shadow mode) : NON DÉMARRÉE
- Structured outputs json_schema : NON DÉMARRÉS (encore json_object)
- VarietySeed (lot Qualité) : LIVRÉ (commits 74ffb14→33bb325, intégré post-beta.5)

## Auth
- JWT access token : 15 min (`ACCESS_TOKEN_EXPIRE_MINUTES = 15` dans config.py)
- JWT refresh token : 7 jours (confirmé CLAUDE.md)
- Cookies HTTP-only
- Endpoints : login, logout, refresh, validate-token, csrf, forgot-password, reset-password, verify-email, resend-verification

## Frontend
- Framework : Next.js 16.2.3
- i18n : next-intl (fr/en)
- Vitest gates CI : 46 / 38 / 42 / 48
- ACTIF-03 : FERMÉ (co-localisation tests, 2026-04-14)
- ACTIF-04 : OUVERT (couverture < 55%)

## Conventions de code actives
- Config : `settings.X` (jamais `os.getenv()` directement — sauf exceptions documentées : email SMTP/SendGrid dans email_service.py, Sentry dans monitoring.py)
- SQLAlchemy booleans : `.is_(True)` / `.is_(False)`
- Logging : `logger.error("msg {}", var)` — loguru, `{}` placeholders, jamais f-string ni `%s`
- Star Wars/Jedi : INTERDIT dans nouveau code — spatial neutre uniquement
- `VALID_CHALLENGE_TYPES` : dans `challenge_prompt_sections.py` (depuis commit 33bb325)
- Pydantic-settings : `BaseSettings` avec `model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")`

## Fichiers archivés (ne plus référencer comme actifs)
- `app/api/endpoints/` — archivé, remplacé par `server/routes/` + `server/handlers/`
- Toute référence FastAPI comme framework actif (archivé 06/02/2026)
- `o3` comme modèle par défaut (remplacé par `o4-mini` depuis beta.4)
