# README_TECH.md - Mathakine

> Living technical reference
> Updated: 15/03/2026
> Visible product release: `3.1.0-alpha.8`

## 1. Overview

Mathakine is a gamified education platform composed of:
- a Next.js 16 frontend in `frontend/`
- a Starlette HTTP layer in `server/`
- a business/domain layer in `app/`
- a PostgreSQL database managed through SQLAlchemy and Alembic

Verified current state:
- iterations `exercise/auth/user` and `challenge/admin/badge` are closed
- iteration `Runtime Truth` is closed
- iteration `Contracts / Hardening` is closed on its intended scope
- iteration `Production Hardening` is closed
- local reference baseline:
  - full suite excluding the false gate: `868 passed, 2 skipped`
  - `black app/ server/ tests/ --check`: green
  - `isort app/ server/ --check-only --diff`: green
  - backend coverage gate in CI: `63 %`

Versioning:
- visible product source of truth: `CHANGELOG.md` and `frontend/package.json`
- `pyproject.toml` keeps a historical Python package version and must not be read as the current visible release

## 2. Active Architecture

```text
Browser
  -> frontend/ (Next.js)
  -> server/routes + server/handlers (Starlette)
  -> app/services / app/repositories / app/models
  -> PostgreSQL
```

### Responsibility split

- `server/routes/`: active route declarations
- `server/handlers/`: HTTP parsing, transport validation, response mapping
- `app/services/`: business orchestration and application logic
- `app/repositories/`: isolated data access where the repository convention has already been introduced
- `app/models/`: SQLAlchemy ORM
- `app/schemas/`: Pydantic schemas
- `app/generators/`: backend source of truth for exercise generation

### Backend execution model

The runtime model retained on the refactored scope is:
- HTTP handlers are `async`
- services, facades and repositories are `sync`
- sync DB access uses `sync_db_session()`
- handlers call DB-bound work through `await run_db_bound(...)`
- SSE and LLM flows stay `async`, but any DB subcalls remain isolated in sync boundaries

This model was adopted to remove fake async without forcing a global `AsyncSession` migration.

## 3. Production Hardening Closed On 15/03/2026

### C1 - Diagnostic integrity

- the diagnostic flow now uses a signed `state_token`
- `/api/diagnostic/question` no longer exposes `correct_answer`
- answer validation is performed from backend-controlled state, not from a free client payload

### C2 - Distributed rate limiting

- production source of truth is Redis via `RedisRateLimitStore`
- `REDIS_URL` is mandatory in production
- Redis runtime failures are fail-closed on the protected scope
- memory fallback is dev/test only

### C3 - Coverage margin

- backend CI coverage gate moved from `62 %` to `63 %`
- targeted tests were added on `challenge_validation_analysis` and `chat_handlers`

### C4 - Legacy API truth

- `app/api/endpoints/*` and `app/api/deps.py` were archived to `_ARCHIVE_2026/app/api/`
- they are not mounted and not imported by the live Starlette runtime

### C5 - Hygiene / DRY

- the duplicated OpenAI import block in `server/handlers/chat_handlers.py` was removed

## 4. Legacy Still Active

Legacy still present by design:
- `app/services/enhanced_server_adapter.py`
- `app/utils/db_utils.py::db_session()` for compatibility

Generator compatibility re-exports still exist:
- `server/exercise_generator.py`
- `server/exercise_generator_helpers.py`
- `server/exercise_generator_validators.py`

Their source of truth remains `app/generators/` and `app/utils/`.

## 5. Quality And Gates

Active backend gates:

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

Coverage and typing:
- CI coverage gate: `--cov-fail-under=63`
- global mypy remains permissive
- stricter mypy islands are enabled module by module in `pyproject.toml`

Windows note:
- repeated coverage reruns should use a dedicated `COVERAGE_FILE` per run to avoid false lock errors on `.coverage`

## 6. What Remains Intentionally Out Of Scope

- global strict mypy on all `app/` and `server/`
- raising coverage to `65 %` then `68 %+`
- distributed migration of `app/utils/rate_limiter.py` outside the protected C2 scope
- dense historical modules such as `auth_service`, `exercise_service`, `challenge_service`, `challenge_validator`, `admin_content_service`, `badge_requirement_engine`

## 7. Canonical References

- [docs/00-REFERENCE/ARCHITECTURE.md](docs/00-REFERENCE/ARCHITECTURE.md)
- [docs/INDEX.md](docs/INDEX.md)
- [docs/02-FEATURES/API_QUICK_REFERENCE.md](docs/02-FEATURES/API_QUICK_REFERENCE.md)
- [docs/02-FEATURES/AUTH_FLOW.md](docs/02-FEATURES/AUTH_FLOW.md)
- [docs/02-FEATURES/F03_DIAGNOSTIC_INITIAL.md](docs/02-FEATURES/F03_DIAGNOSTIC_INITIAL.md)
- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md)
- [docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
