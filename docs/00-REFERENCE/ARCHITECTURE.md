# Architecture - Mathakine

> Global architecture reference
> Updated: 22/03/2026

## 1. System Overview

Mathakine is structured around three active zones:

1. `frontend/`: Next.js 16, React 19, TypeScript, React Query, Zustand
2. `server/`: Starlette routes, handlers, auth and middleware
3. `app/`: business logic, services, repositories, generators, models and schemas

Main flow:

```text
Browser -> frontend/ -> server/routes + server/handlers -> app/services -> (repositories where used | ORM/Session direct) -> PostgreSQL
```

## 2. Architecture Principles

- thin HTTP handlers: transport parsing, validation, response mapping
- business orchestration in `app/services/`
- DB access: sync_db_session() for lifecycle; data access is **selective** (repositories where introduced) and **direct ORM** in many services — no global repository isolation yet
- stable public HTTP contracts
- the active code wins over historical documentation

## 3. Real Backend Execution Model

> ⚠️ OBSOLÈTE — la baseline locale "post-iteration I" ci-dessous est un snapshot historique du 19/03/2026.
> Elle ne doit plus être utilisée comme vérité des lots IA10b, IA11, IA12 et IA13.
> Pour la gouvernance des modèles IA et l'observabilité runtime actuelles, utiliser [AI_MODEL_GOVERNANCE.md](AI_MODEL_GOVERNANCE.md).

The retained backend runtime model is:
- HTTP handlers are `async`
- services, facades and repositories are `sync`
- sync DB access uses `sync_db_session()` (app.core.db_boundary)
- handlers call DB-bound work through `await run_db_bound(...)` (app.core.db_boundary)
- SSE and LLM flows remain `async`, with sync DB boundaries when needed

Boundary contract (F5): see `app.core.db_boundary` for the formal runtime/data boundary.

### Data-Layer Doctrine (I1 — 2026-03-19)

**What is true today:**
- Handlers are `async`; services and facades are `sync`
- Runtime/data boundary: handlers call DB-bound work via `run_db_bound(...)`; sync code uses `sync_db_session()`
- `sync_db_session` is imported from `app.core.db_boundary` (G4)
- Repositories exist **selectively**: `exercise_repository.py`, `exercise_attempt_repository.py` — used for exercise generation and submit validation
- Many services import `Session` and use ORM directly (25+ modules; per maturity audit: 40 of 64 service modules)

**What is not true globally:**
- DB access is **not** fully isolated behind repositories
- There is no global repository layer; ORM direct use remains the dominant pattern in services
- Repository rollout is out of scope for I1; it may be addressed in later bounded lots

Verified local reference on 19/03/2026 (post-iteration I closure):
- gate standard backend: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `962 passed, 3 skipped`
- `test_admin_auth_stability.py` : test spécial, exclu du gate standard (non-bloquant)
- OpenAI live tests remain opt-in and are not part of the standard gate
- `black app/ server/ tests/ --check`: green
- `isort app/ server/ tests/ --check-only --diff`: green
- backend coverage gate in CI: `63 %`

## 4. Backend Layers

### `server/`

- `routes/`: source of truth for active routes
- `handlers/`: HTTP layer
- `auth.py`: runtime auth and decorators
- `middleware.py`: application middleware
- `app.py`: Starlette app factory via `get_routes()`

### `app/`

- `models/`: SQLAlchemy ORM (explicit modules, `__init__.py` re-exports)
- `schemas/`: Pydantic schemas (explicit modules, `__init__.py` re-exports)
- `services/`: business logic and application boundaries, **organised by DDD domains** (Cible B)
- `repositories/`: **selective** data access (2 modules: exercise_repository, exercise_attempt_repository); most services still use ORM/Session directly
- `generators/`: exercise generation source of truth
- `db/`: engine, sessions, transactions, adapter
- `utils/`: shared helpers

#### `app/services/` — Domains (Vertical Slicing, Cible B)

Services are grouped by bounded context. No business logic file remains at root (only `__init__.py`).

| Domain | Path | Content |
|--------|------|---------|
| **auth** | `app/services/auth/` | auth_service, auth_session_service, auth_recovery_service |
| **users** | `app/services/users/` | user_service, user_application_service |
| **badges** | `app/services/badges/` | badge_service, badge_application_service, badge_* (14 files) |
| **exercises** | `app/services/exercises/` | exercise_service, exercise_attempt_service, exercise_* (9 files) |
| **challenges** | `app/services/challenges/` | challenge_service, logic_challenge_service, maze_validator, etc. (11 files) |
| **progress** | `app/services/progress/` | progress_timeline_service, streak_service, daily_challenge_service |
| **admin** | `app/services/admin/` | admin_service, admin_read_service, admin_content_service, etc. (14 files) |
| **analytics** | `app/services/analytics/` | analytics_service |
| **communication** | `app/services/communication/` | email_service, chat_service |
| **core** | `app/services/core/` | db_init_service, enhanced_server_adapter |
| **diagnostic** | `app/services/diagnostic/` | diagnostic_service |
| **feedback** | `app/services/feedback/` | feedback_service |
| **recommendation** | `app/services/recommendation/` | recommendation_service |

## 5. Production Hardening Decisions Now Active

### AI runtime governance

- la gouvernance des modèles IA est maintenant explicitement séparée par workload (`assistant_chat`, `exercises_ai`, `challenges_ai`)
- les métriques runtime IA et les runs persistés du harness sont des lectures distinctes
- la référence détaillée n'est plus portée par ce document d'architecture généraliste, mais par [AI_MODEL_GOVERNANCE.md](AI_MODEL_GOVERNANCE.md)

### Diagnostic flow

- diagnostic mutation endpoints now rely on a signed `state_token`
- `correct_answer` is no longer exposed by `/api/diagnostic/question`
- backend-side checked state is the source of truth for answer validation
- pending diagnostic answer truth is resolved server-side through an opaque `pending_ref`

### Runtime boundaries

- `MATH_TRAINER_DEBUG` defaults to `false`
- external JSON error payloads do not expose traceback details
- `MAX_CONTENT_LENGTH` is enforced before JSON/body parsing on the hardened request paths

### Rate limiting

- production source of truth is Redis
- `REDIS_URL` is mandatory in production
- Redis runtime failures are fail-closed on the protected scope
- memory fallback is allowed only in dev/test

### Legacy API truth

- `app/api/endpoints/*` and `app/api/deps.py` are archived in `_ARCHIVE_2026/app/api/`
- they are not mounted and not imported by the live runtime

## 6. Legacy And Compatibility

Legacy still active:
- `app/services/core/enhanced_server_adapter.py` — seul `create_generated_exercise` est utilisé (exercise_ai_service). Les autres méthodes sont inactives ou compatibilité.

Generator compatibility re-exports:
- `server/exercise_generator.py`
- `server/exercise_generator_helpers.py`
- `server/exercise_generator_validators.py`

These files are compatibility shims. Their source of truth remains `app/generators/` and `app/utils/`.

## 7. Canonical References

- [../../README_TECH.md](../../README_TECH.md)
- [../INDEX.md](../INDEX.md)
- [AI_MODEL_GOVERNANCE.md](AI_MODEL_GOVERNANCE.md)
- [../02-FEATURES/API_QUICK_REFERENCE.md](../02-FEATURES/API_QUICK_REFERENCE.md)
- [../02-FEATURES/AUTH_FLOW.md](../02-FEATURES/AUTH_FLOW.md)
- [../02-FEATURES/F03_DIAGNOSTIC_INITIAL.md](../02-FEATURES/F03_DIAGNOSTIC_INITIAL.md)
- [../03-PROJECT/README.md](../03-PROJECT/README.md)
- [../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
