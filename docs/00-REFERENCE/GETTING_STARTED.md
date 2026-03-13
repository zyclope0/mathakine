# GETTING STARTED - MATHAKINE

> Demarrage rapide
> Mise a jour : 13/03/2026
> Release produit visible : `3.1.0-alpha.8`

## Prerequis

- Node.js `>= 18.17`
- npm `>= 9`
- Python `>= 3.12`
- PostgreSQL `>= 15`
- Git

Important:
- le backend de dev et les tests backend s'appuient sur PostgreSQL local
- la source de verite release produit est `CHANGELOG.md` + `frontend/package.json`
- `pyproject.toml` ne doit pas etre lu comme version produit courante

## Installation rapide

### 1. Cloner le projet

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

Backend par defaut: `http://localhost:8000`

Variables minimales a verifier dans `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mathakine
SECRET_KEY=<secret>
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Frontend par defaut: `http://localhost:3000`

Variable frontend utile:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Base de test locale

Pour preparer la base backend de test locale:

```powershell
python scripts/check_local_db.py
```

Pour un run local backend complet (DB + schema + pytest):

```powershell
python scripts/test_backend_local.py
```

## Verification rapide

### Backend

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

### Frontend

```bash
cd frontend
npm run lint:ci
npm run test
```

## Points de vigilance

- ne pas lancer plusieurs commandes `pytest` avec couverture en parallele sur Windows: lock `.coverage` et faux positifs possibles
- `tests/api/test_admin_auth_stability.py` n'est pas un gate standard
- les routes actives sont definies dans `server/routes/`
- `app/api/endpoints/` existe encore mais n'est pas monte dans le runtime Starlette actif

## Lire ensuite

- [../../README_TECH.md](../../README_TECH.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [../01-GUIDES/TESTING.md](../01-GUIDES/TESTING.md)
- [../01-GUIDES/TROUBLESHOOTING.md](../01-GUIDES/TROUBLESHOOTING.md)
- [../03-PROJECT/README.md](../03-PROJECT/README.md)
