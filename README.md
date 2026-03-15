# Mathakine

Gamified mathematics learning platform with a Next.js frontend and a Starlette/SQLAlchemy backend.

[![Version](https://img.shields.io/badge/version-3.1.0--alpha.8-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)
[![Tests](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml/badge.svg)](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/zyclope0/mathakine/graph/badge.svg)](https://codecov.io/gh/zyclope0/mathakine)

## Product Status

- visible release: `3.1.0-alpha.8`
- release source of truth: `CHANGELOG.md` and `frontend/package.json`
- note: `pyproject.toml` still carries a historical Python package version and does not define the visible product release

## Key Capabilities

- adaptive math exercises
- logic challenges and AI-backed content
- badges, progression and user dashboard
- admin analytics and moderation surfaces
- cookie/session authentication with account recovery
- multilingual Next.js frontend

## Read First

- [README_TECH.md](README_TECH.md): living technical reference
- [docs/INDEX.md](docs/INDEX.md): documentation entry point
- [docs/00-REFERENCE/GETTING_STARTED.md](docs/00-REFERENCE/GETTING_STARTED.md): setup guide
- [docs/00-REFERENCE/ARCHITECTURE.md](docs/00-REFERENCE/ARCHITECTURE.md): active architecture
- [docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md): active recap of the latest backend hardening iteration
- [CHANGELOG.md](CHANGELOG.md): product history and release status

## Current Verified State On 15/03/2026

- backend iteration `exercise/auth/user`: closed
- backend iteration `challenge/admin/badge`: closed
- iteration `Runtime Truth`: closed
- iteration `Contracts / Hardening`: closed
- iteration `Production Hardening`: closed
- local reference baseline:
  - full suite excluding the false gate: `868 passed, 2 skipped`
  - `black app/ server/ tests/ --check`: green
  - `isort app/ server/ --check-only --diff`: green
  - backend coverage gate in CI: `63 %`

## Stack

- Frontend: Next.js 16, React 19, TypeScript, React Query, Zustand
- Backend: Starlette, SQLAlchemy 2, PostgreSQL, Alembic
- AI: OpenAI
- Tests: pytest, Vitest, Playwright
- CI/CD: GitHub Actions and Render

## Quick Start

### Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python enhanced_server.py
```

Backend default URL: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:3000`

## Repository Structure

```text
frontend/   Next.js user interface
server/     Starlette HTTP layer (routes, handlers, auth, middleware)
app/        business logic, services, repositories, models, schemas
migrations/ Alembic migrations
tests/      backend and frontend tests
docs/       project documentation
```

## Reading Rules

- active route truth lives in `server/routes/`
- active backend architecture truth lives in `server/` and `app/`
- `app/api/endpoints/*` has been archived under `_ARCHIVE_2026/` and is not part of the live runtime
- the active diagnostic contract uses a signed `state_token`; `/api/diagnostic/question` no longer exposes `correct_answer`
- production rate limiting now relies on Redis; memory fallback is dev/test only
- detailed lot-by-lot execution notes are archived; the active recap documents take precedence

## Tests And Quality

Useful commands:

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
cd frontend && npm run lint:ci
cd frontend && npx tsc --noEmit
```

Important:
- `tests/api/test_admin_auth_stability.py` is not a standard gate while it still launches `pytest` from inside `pytest`
- on Windows, repeated coverage runs should use a dedicated `COVERAGE_FILE` to avoid false `.coverage` lock failures

## Project References

- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md)
- [docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
