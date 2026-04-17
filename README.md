# Mathakine

Gamified mathematics learning platform with a Next.js frontend and a Starlette/SQLAlchemy backend.

[![Version](https://img.shields.io/badge/version-3.6.0--beta.1-blue.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](CHANGELOG.md)
[![Tests](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml/badge.svg)](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/zyclope0/mathakine/graph/badge.svg)](https://codecov.io/gh/zyclope0/mathakine)

## Product Status

- visible release: `3.6.0-alpha.1`
- release source of truth: `CHANGELOG.md` and `frontend/package.json`
- note: `pyproject.toml` now carries the aligned Python package metadata version `3.6.0b1`, but visible product release governance still lives in `CHANGELOG.md` and `frontend/package.json`

## Key Capabilities

- adaptive math exercises
- logic challenges and AI-backed content
- badges, progression, user dashboard and spaced review flow
- admin analytics and moderation surfaces
- cookie/session authentication with account recovery
- multilingual Next.js frontend

## Read First

- **Backend env (typed settings)** : `app/core/config.py` + root `.env.example` (aligned with `Settings`; SMTP/SendGrid and Sentry use `os.getenv` in their modules — see `.env.example` comments)
- [README_TECH.md](README_TECH.md): living technical reference
- [docs/INDEX.md](docs/INDEX.md): documentation entry point
- [docs/00-REFERENCE/GETTING_STARTED.md](docs/00-REFERENCE/GETTING_STARTED.md): setup guide
- [docs/00-REFERENCE/ARCHITECTURE.md](docs/00-REFERENCE/ARCHITECTURE.md): active architecture
- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md): active project governance, frontend quality snapshot, and archive map
- [docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/POINTS_RESTANTS_2026-03-15.md](docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/POINTS_RESTANTS_2026-03-15.md): archived backend remaining-follow-ups tracker
- [docs/03-PROJECT/archives/RECOMMENDATION_ITERATION_R_2026-03/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](docs/03-PROJECT/archives/RECOMMENDATION_ITERATION_R_2026-03/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md): archived recommendation iteration `R` closure
- [CHANGELOG.md](CHANGELOG.md): product history and release status

## Current verified state (closed iterations + cited baselines)

Figures below are **citations** from documented closure runs; **re-run** the same commands if your tree has diverged.

- backend iteration `exercise/auth/user`: closed
- backend iteration `challenge/admin/badge`: closed
- iteration `Runtime Truth`: closed
- iteration `Contracts / Hardening`: closed
- iteration `Production Hardening`: closed
- iteration `Security, Boundaries, and API Discipline`: closed
- iteration `Typed Contracts, Service Decomposition, and Legacy Retirement`: closed
- iteration `Academic Backend Rigor, Replicability, and Operability`: closed
- lots `G` (`Residual Contracts and Cleanup`): closed
- `Architecture Clean` (service slicing cible A + B): closed
- `Backend Maturity Truth, Contract Normalization, and Hotspot Reduction`: closed (`I1`-`I8`)
- **Recommendation remediation** (`R1`�`R7`): **closed** (2026-03-21) � bounded heuristic rules, structured reasons, and test-backed behaviour on exercised paths; **not** a learned / ML personalization engine. Closure doc: [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](docs/03-PROJECT/archives/RECOMMENDATION_ITERATION_R_2026-03/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md).

**Historical reference baseline — post–iteration `I` (2026-03-19)**

- gate standard backend: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `962 passed, 3 skipped`
- OpenAI live tests remain opt-in and are not part of the standard gate
- `test_admin_auth_stability.py`: test special, excluded from the standard gate (non-blocking)
- `black app/ server/ tests/ --check`: green
- `isort app/ server/ tests/ --check-only --diff`: green
- backend coverage gate in CI: `63 %`

**Additional citation — post–recommendation closure R7 (2026-03-21)** (reco engine + same standard gate, after more tests landed)

- targeted recommendation tests: `pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` -> **`40 passed`**
- standard backend gate (same command as above): **`991 passed, 2 skipped`**
- _(Micro-lot R7b, doc-only: root README alignment; no test rerun.)_

## Versioning Rule

- visible product releases follow SemVer prerelease stages
- current visible train: `3.6.0-beta.1`
- moving from `3.5.0-alpha.1` to `3.6.0-alpha.1` opens a new minor prerelease train because learner/adult surface routing, canonical roles, neuro-inclusion UX, and the visible theme system changed materially for end users
- moving directly to `3.2.0` stable would be misleading in the current context
- while still in `alpha`, incrementing `alpha.N` is the normal bugfix cadence; patch numbers become meaningful after a stable `X.Y.Z` exists
- internal iterations (`I`, `R`, etc.) are engineering milestones, not product versions

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
pip install -r requirements-dev.txt
cp .env.example .env   # or Copy-Item .env.example .env on Windows; then edit secrets
alembic upgrade head
python enhanced_server.py
```

For Render or other production images, keep `requirements.txt` as the lean runtime set. For local development, tests, linting and docs tooling, use `requirements-dev.txt`.

Backend default URL: `http://localhost:10000` (`PORT` défaut dans `enhanced_server.py`)

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
isort app/ server/ tests/ --check-only --diff
cd frontend && npm run lint:ci
cd frontend && npx tsc --noEmit
```

Important:

- `tests/api/test_admin_auth_stability.py` is not a standard gate while it still launches `pytest` from inside `pytest`
- on Windows, repeated coverage runs should use a dedicated `COVERAGE_FILE` to avoid false `.coverage` lock failures

## Project References

- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md)
- [docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/POINTS_RESTANTS_2026-03-15.md](docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/POINTS_RESTANTS_2026-03-15.md)
- [docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md](docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md)
