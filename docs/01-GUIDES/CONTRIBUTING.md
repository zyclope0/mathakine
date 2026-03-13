# CONTRIBUTING GUIDE - MATHAKINE

> Mise a jour : 13/03/2026
> Audience : contributeurs code et documentation

## Principes de contribution

- la verite terrain est le code actif + les gates reproduites
- un handler doit rester mince: HTTP, validation transport, mapping reponse
- la logique metier va dans `app/services/`
- l'acces DB ne doit pas vivre dans les handlers
- tout changement runtime doit etre accompagne de tests ou d'une justification explicite

## Mise en place locale

### Backend

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
```

### Base de test

```powershell
python scripts/check_local_db.py
```

## Workflow recommande

### 1. Synchroniser et creer une branche

```bash
git checkout main
git pull
git checkout -b feature/nom-court
```

### 2. Developper

Regles backend:
- handler `async`
- service / facade / repository `sync`
- body JSON valide par schema Pydantic
- appels DB depuis les handlers via `run_db_bound(...)` quand le modele runtime cible l'impose

### 3. Verifier localement

#### Backend

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

#### Frontend

```bash
cd frontend
npm run lint:ci
npm run test
```

Important:
- ne pas lancer plusieurs `pytest` avec couverture en parallele sur Windows
- `tests/api/test_admin_auth_stability.py` n'est pas un gate standard

### 4. Commit

Format recommande:

```text
type(scope): sujet court
```

Types frequents:
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

Exemples:

```bash
git commit -m "fix(auth): revoke old tokens after password reset"
git commit -m "refactor(challenge): move DB boundary out of handler"
git commit -m "docs(runtime): align docs with active Starlette wiring"
```

### 5. Pull request

Une PR propre doit expliciter:
- fichiers runtime modifies
- fichiers de test modifies
- endpoints reellement touches
- ce qui est prouve
- ce qui n'est pas prouve
- checks executes

## Documentation

Si tu modifies un point de runtime, verifie aussi:
- `README_TECH.md`
- `docs/00-REFERENCE/ARCHITECTURE.md`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md` si une route active ou son contrat change
- `docs/03-PROJECT/` si le changement appartient a une iteration suivie

## References

- [DEVELOPMENT.md](DEVELOPMENT.md)
- [TESTING.md](TESTING.md)
- [../../README_TECH.md](../../README_TECH.md)
- [../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
