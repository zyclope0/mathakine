# GETTING STARTED - MATHAKINE

> Quick start
> Updated: 27/03/2026
> Visible product release: `3.4.0-alpha.1`

## Prerequisites

- Node.js `>= 18.17`
- npm `>= 9`
- Python `>= 3.12`
- PostgreSQL `>= 15`
- Git

Important:
- backend development and backend tests rely on a local PostgreSQL instance
- visible release truth comes from `CHANGELOG.md` and `frontend/package.json`
- `pyproject.toml` is not the visible product release source

## Quick Install

### 1. Clone the repository

```bash
git clone <repository-url>
cd mathakine
```

### 2. Backend

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python enhanced_server.py
```

Backend default URL: `http://localhost:10000`

Useful backend variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mathakine
SECRET_KEY=<secret>
BACKEND_CORS_ORIGINS=http://localhost:3000
# optional in local dev, mandatory in production for distributed rate limiting
REDIS_URL=
```

### 3. Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Frontend default URL: `http://localhost:3000`

Frontend variable usually required locally:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000
```

## Local Test Database

Prepare the local backend test database:

```powershell
python scripts/check_local_db.py
```

Run the local backend verification script:

```powershell
python scripts/test_backend_local.py
```

## Quick Verification

### Backend

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
```

### Frontend

```bash
cd frontend
npm run lint:ci
npx tsc --noEmit
npm run test
```

## Watch-Outs

- on Windows, repeated coverage reruns should use a dedicated `COVERAGE_FILE`
- `tests/api/test_admin_auth_stability.py` is not a standard gate
- active routes are defined in `server/routes/`
- `app/api/endpoints/*` is archived under `_ARCHIVE_2026/`; live runtime truth is `server/routes/` + `server/handlers/`

## Read Next

- [../../README_TECH.md](../../README_TECH.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [../01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md)
- [../01-GUIDES/DEPLOYMENT_ENV.md](../01-GUIDES/DEPLOYMENT_ENV.md)
- [../03-PROJECT/README.md](../03-PROJECT/README.md)
