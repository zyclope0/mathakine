# 🎓 Mathakine

Plateforme d'apprentissage des mathematiques gamifiee avec frontend Next.js et backend Starlette/SQLAlchemy.

[![Version](https://img.shields.io/badge/version-3.1.0--alpha.8-blue.svg)](CHANGELOG.md)
[![Statut](https://img.shields.io/badge/statut-alpha-orange.svg)](CHANGELOG.md)
[![Tests](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml/badge.svg)](https://github.com/zyclope0/mathakine/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/zyclope0/mathakine/graph/badge.svg)](https://codecov.io/gh/zyclope0/mathakine)

## 📌 Statut produit actuel

- release visible : `3.1.0-alpha.8`
- source de verite versioning : `CHANGELOG.md` + `frontend/package.json`
- note : la metadata Python de `pyproject.toml` n'est pas alignee sur la release produit

## ✨ Fonctionnalites cles

- 🎯 Exercices mathematiques adaptatifs
- 🧩 Defis logiques et contenus IA
- 🏆 Gamification, badges et progression
- 📊 Dashboard utilisateur et analytics admin
- 🔐 Authentification par session/cookies et recuperation de compte
- 🌍 Frontend Next.js multilingue

## 📚 Documentation a lire en premier

- [README_TECH.md](README_TECH.md) : reference technique vivante
- [docs/INDEX.md](docs/INDEX.md) : point d'entree de la documentation
- [docs/00-REFERENCE/GETTING_STARTED.md](docs/00-REFERENCE/GETTING_STARTED.md) : installation pas a pas
- [docs/00-REFERENCE/ARCHITECTURE.md](docs/00-REFERENCE/ARCHITECTURE.md) : architecture globale
- [CHANGELOG.md](CHANGELOG.md) : historique produit et statut de release

## ✅ Etat reel au 14/03/2026

- backend `exercise/auth/user` : iteration cloturee
- backend `challenge/admin/badge` : iteration cloturee
- iteration Runtime `quality-first` : cloturee
- iteration Contracts / Hardening : cloturee
- baseline locale de reference :
  - full suite hors faux gate : `823 passed, 2 skipped`
  - `black --check` : vert
  - `isort --check-only --diff` : vert

## 🏗️ Stack

- Frontend : Next.js 16, React 19, TypeScript, React Query, Zustand
- Backend : Starlette, SQLAlchemy 2, PostgreSQL, Alembic
- IA : OpenAI
- Tests : pytest, Vitest, Playwright
- CI/CD : GitHub Actions + Render

## ⚡ Demarrage rapide

### Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python enhanced_server.py
```

Le backend ecoute par defaut sur `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend ecoute par defaut sur `http://localhost:3000`.

## 📁 Structure

```text
frontend/   interface utilisateur Next.js
server/     couche HTTP Starlette (routes, handlers, auth, middleware)
app/        logique metier, services, repositories, modeles, schemas
migrations/ migrations Alembic
tests/      tests backend et frontend
docs/       documentation projet
```

## 🧭 Regles de lecture

- la source de verite des routes actives est `server/routes/`
- la source de verite de l'architecture backend active est `server/` + `app/`
- `app/api/endpoints/` existe encore physiquement mais n'est pas monte dans le wiring Starlette actif
- les details lot par lot `Runtime` et `Contracts` sont archives ; le recapitulatif actif fait foi

## 🧪 Tests et qualite

Commandes utiles :

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
cd frontend && npm run lint:ci
```

Important :
- ne pas lancer plusieurs commandes `pytest` avec couverture en parallele sur Windows : cela peut provoquer des faux positifs de lock `.coverage`
- `tests/api/test_admin_auth_stability.py` n'est pas un gate standard tant qu'il lance `pytest` dans `pytest`

## 🔎 References projet

- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md)
- [docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
- [docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
