# DEVELOPMENT GUIDE - MATHAKINE

> Guide de developpement quotidien
> Mise a jour : 13/03/2026

## Modele d'architecture a respecter

Backend actif:
- `server/routes/` : routes actives
- `server/handlers/` : HTTP, validation transport, mapping reponse
- `app/services/` : orchestration metier et applicative
- `app/repositories/` : acces data quand la convention repository est introduite
- `app/models/` : ORM SQLAlchemy
- `app/schemas/` : validation Pydantic

Regle runtime actuelle:
- handlers HTTP `async`
- acces DB et orchestration sync
- DB sync via `sync_db_session()`
- appels DB depuis les handlers via `await run_db_bound(...)`

A ne pas faire:
- logique metier dans les handlers
- acces DB direct dans un handler
- nouvelles entrees HTTP sans schema Pydantic si body JSON
- modifications opportunistes hors scope du lot courant

## Environnement local

### Backend

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python enhanced_server.py
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

### Base de test

```powershell
python scripts/check_local_db.py
```

## Workflow recommande

### Avant de coder

```bash
git status --short
git diff --name-only
```

### Pendant un lot backend

1. relire les handlers, routes et services reellement touches
2. verifier le wiring runtime, pas seulement les tests
3. lancer une batterie cible deux fois si le runtime est touche
4. lancer la full suite si le lot modifie un comportement runtime transverse

### Gates backend standards

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

### Gates frontend standards

```bash
cd frontend
npm run lint:ci
npm run test
```

## Qualite attendue

- typage fort
- erreurs metier explicites
- fonctions courtes
- zero duplication evitables
- contrats HTTP stables si le lot n'annonce pas un changement public

## Regles de documentation

- la verite terrain est le code actif + les gates reproduites
- `CHANGELOG.md` + `frontend/package.json` portent la release produit visible
- les docs de pilotage dans `docs/03-PROJECT/` ne valent jamais preuve sans relecture du code
- ne pas conclure `GO` si `run 2` ou la batterie mixte recasse

## Points de vigilance connus

- `tests/api/test_admin_auth_stability.py` n'est pas un gate standard
- ne pas lancer plusieurs `pytest` avec couverture en parallele sur Windows
- l'iteration Runtime est cloturee localement; la prochaine sequence de solidification backend est `Contracts / Hardening`

## References

- [../../README_TECH.md](../../README_TECH.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [TESTING.md](TESTING.md)
- [../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
