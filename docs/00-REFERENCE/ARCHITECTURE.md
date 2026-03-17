# Architecture - Mathakine

> Global architecture reference
> Updated: 17/03/2026

## 1. System Overview

Mathakine is structured around three active zones:

1. `frontend/`: Next.js 16, React 19, TypeScript, React Query, Zustand
2. `server/`: Starlette routes, handlers, auth and middleware
3. `app/`: business logic, services, repositories, generators, models and schemas

Main flow:

```text
Browser -> frontend/ -> server/routes + server/handlers -> app/services -> app/repositories -> PostgreSQL
```

## 2. Architecture Principles

- thin HTTP handlers: transport parsing, validation, response mapping
- business orchestration in `app/services/`
- DB access isolated behind sync services and repositories
- stable public HTTP contracts
- the active code wins over historical documentation

## 3. Real Backend Execution Model

The retained backend runtime model is:
- HTTP handlers are `async`
- services, facades and repositories are `sync`
- sync DB access uses `sync_db_session()` (app.core.db_boundary)
- handlers call DB-bound work through `await run_db_bound(...)` (app.core.db_boundary)
- SSE and LLM flows remain `async`, with sync DB boundaries when needed

Boundary contract (F5): see `app.core.db_boundary` for the formal runtime/data boundary.

Verified local reference on 17/03/2026 (post-F):
- full suite excluding the false gate: `936 passed, 2 skipped`
- `black app/ server/ tests/ --check`: green
- `isort app/ server/ --check-only --diff`: green
- backend coverage gate in CI: `63 %`

## 4. Backend Layers

### `server/`

- `routes/`: source of truth for active routes
- `handlers/`: HTTP layer
- `auth.py`: runtime auth and decorators
- `middleware.py`: application middleware
- `app.py`: Starlette app factory via `get_routes()`

### `app/`

- `models/`: SQLAlchemy ORM
- `schemas/`: Pydantic schemas
- `services/`: business logic and application boundaries
- `repositories/`: isolated data access where introduced
- `generators/`: exercise generation source of truth
- `db/`: engine, sessions, transactions, adapter
- `utils/`: shared helpers

## 5. Production Hardening Decisions Now Active

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
- `app/services/enhanced_server_adapter.py` — seul `create_generated_exercise` est utilisé (exercise_ai_service). Les autres méthodes sont inactives ou compatibilité.

Generator compatibility re-exports:
- `server/exercise_generator.py`
- `server/exercise_generator_helpers.py`
- `server/exercise_generator_validators.py`

These files are compatibility shims. Their source of truth remains `app/generators/` and `app/utils/`.

## 7. Canonical References

- [../../README_TECH.md](../../README_TECH.md)
- [../INDEX.md](../INDEX.md)
- [../02-FEATURES/API_QUICK_REFERENCE.md](../02-FEATURES/API_QUICK_REFERENCE.md)
- [../02-FEATURES/AUTH_FLOW.md](../02-FEATURES/AUTH_FLOW.md)
- [../02-FEATURES/F03_DIAGNOSTIC_INITIAL.md](../02-FEATURES/F03_DIAGNOSTIC_INITIAL.md)
- [../03-PROJECT/README.md](../03-PROJECT/README.md)
- [../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
