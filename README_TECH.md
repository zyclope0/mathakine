# README_TECH.md - Mathakine

> Reference technique vivante
> Mise a jour : 13/03/2026
> Release produit visible : `3.1.0-alpha.8`

## 1. Vue d'ensemble

Mathakine est une plateforme educative gamifiee composee de:
- un frontend Next.js 16 dans `frontend/`
- une couche HTTP Starlette dans `server/`
- une couche domaine / metier dans `app/`
- une base PostgreSQL pilotee via SQLAlchemy et Alembic

Etat reel actuel:
- les iterations backend `exercise/auth/user` puis `challenge/admin/badge` sont cloturees
- l'iteration Runtime est cloturee
- l'iteration Contracts / Hardening est cloturee sur son scope cible
- baseline locale de reference:
  - full suite hors faux gate : `823 passed, 2 skipped`
  - `black --check` vert
  - `isort --check-only --diff` vert

Versioning:
- source de verite produit: `CHANGELOG.md` et `frontend/package.json`
- `pyproject.toml` porte encore une version Python package historique et ne doit pas etre lu comme release produit courante

## 2. Architecture active

```text
Browser
  -> frontend/ (Next.js)
  -> server/routes + server/handlers (Starlette)
  -> app/services / app/repositories / app/models
  -> PostgreSQL
```

### Repartition des responsabilites

- `server/routes/` : declaration des routes actives
- `server/handlers/` : adaptation HTTP, parsing, validation transport, mapping des reponses
- `app/services/` : orchestration metier et applicative
- `app/repositories/` : acces data isole quand la convention repository a deja ete introduite
- `app/models/` : ORM SQLAlchemy
- `app/schemas/` : schemas Pydantic
- `app/generators/` : source de verite de la generation d'exercices

### Runtime model retenu

Le modele cible applique sur le scope refactore est:
- handlers HTTP `async`
- services / facades / repositories `sync`
- acces DB sync via `sync_db_session()`
- execution des appels DB depuis les handlers via `await run_db_bound(...)`
- SSE/LLM restent `async`, mais leurs sous-appels DB sont isoles en sync

Ce modele a ete choisi pour sortir du faux async sans migration globale immediate vers `AsyncSession`.

## 3. Legacy et verite terrain

### Actif

- `enhanced_server_adapter.py` reste encore actif sur certains chemins legacy
- `app/utils/db_utils.py` expose encore `db_session()` pour compatibilite legacy, mais ce n'est plus le modele cible des refactors runtime

### Present mais non monte

- `app/api/endpoints/` existe physiquement mais n'est pas reference par le wiring Starlette actif
- le wiring runtime passe par `server/app.py` puis `server/routes/get_routes()`

### Compatibilite generateur

- `server/exercise_generator.py`
- `server/exercise_generator_helpers.py`
- `server/exercise_generator_validators.py`

Ces fichiers sont des re-exports de compatibilite. La source de verite se trouve dans `app/generators/` et `app/utils/`.

## 4. Domaines backend stabilises

Iterations cloturees:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`

Services applicatifs / boundaries introduits ou stabilises:
- `auth_session_service.py`
- `auth_recovery_service.py`
- `user_application_service.py`
- `exercise_generation_service.py`
- `exercise_attempt_service.py`
- `exercise_query_service.py`
- `exercise_stream_service.py`
- `challenge_query_service.py`
- `challenge_attempt_service.py`
- `challenge_stream_service.py`
- `admin_read_service.py`
- `admin_application_service.py`
- `badge_application_service.py`

## 5. Qualite et durcissement

Points fermes sur le scope cible:
- use cases challenge types
- contracts admin / badge clarifies
- decomposition des hotspots badge, admin stats et challenge validator cible
- principaux hotspots SQL traites sur `challenge_service.py` et `recommendation_service.py`
- gate coverage CI explicite a `62 %`
- ilots mypy plus stricts sur:
  - badge
  - auth session / recovery
  - exercise generation / query
  - challenge query / stream

Ce qui reste volontairement hors scope global:
- mypy global strict
- hausse du coverage gate a `65 %` puis `70 %`
- gros services historiques encore denses (`auth_service`, `exercise_service`, `challenge_service`, `challenge_validator`, `admin_content_service`, `badge_requirement_engine`)

## 6. Endpoints et contrats

La source de verite des routes actives est `server/routes/`.
References:
- [docs/02-FEATURES/API_QUICK_REFERENCE.md](docs/02-FEATURES/API_QUICK_REFERENCE.md)
- [docs/02-FEATURES/AUTH_FLOW.md](docs/02-FEATURES/AUTH_FLOW.md)

Points contractuels notables:
- `POST /api/exercises/generate` est la route active de generation d'exercice montee runtime
- le handler HTML `generate_exercise` existe encore mais n'est pas monte comme route active Starlette
- `POST /api/auth/reset-password` et `PUT /api/users/me/password` revoquent desormais les anciens tokens via `password_changed_at` + `iat`

## 7. Tests et gates

Gates backend standards:

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

Regles importantes:
- `tests/api/test_admin_auth_stability.py` n'est pas un gate standard tant qu'il lance `pytest` dans `pytest`
- ne pas lancer plusieurs commandes `pytest` avec couverture en parallele sur Windows: les locks `.coverage` produisent des faux positifs de tooling
- un lot runtime ou contracts n'est jamais `GO` si le vert n'est pas reproductible sur `run 1` et `run 2`

CI active:
- coverage backend bloquante a `62 %`
- lint Python: `flake8`, `black`, `isort`, `mypy`
- mypy global reste permissif, complete par des overrides plus stricts module par module dans `pyproject.toml`

## 8. References canoniques

- [docs/00-REFERENCE/ARCHITECTURE.md](docs/00-REFERENCE/ARCHITECTURE.md)
- [docs/INDEX.md](docs/INDEX.md)
- [docs/03-PROJECT/README.md](docs/03-PROJECT/README.md)
- [docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
- [docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
