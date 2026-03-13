# TESTING GUIDE - MATHAKINE

> Strategie et gates de test
> Mise a jour : 13/03/2026
> Portee : backend + frontend

## Principes

- la verite terrain est un code relu + des gates reproduites
- un lot runtime ou contracts n'est pas valide si `run 2` recasse
- les batteries cibles priment sur un simple test isole
- la full suite est obligatoire quand le runtime ou le wiring transverse est touche

## Backend - prerequis

- PostgreSQL local joignable sur `localhost:5432`
- `TEST_DATABASE_URL` distinct de `DATABASE_URL`
- dependances Python installees via `pip install -r requirements.txt`

Preparation rapide:

```bash
python scripts/check_local_db.py
```

Run local complet backend:

```bash
python scripts/test_backend_local.py
```

## Backend - gates standards

### Gate complete

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

### Gate de lot runtime ou contracts

```bash
pytest -q <batterie-cible> --maxfail=20
pytest -q <batterie-cible> --maxfail=20
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
black app/ server/ tests/ --check
isort app/ server/ --check-only --diff
```

## Couverture CI

La CI impose un seuil minimal de couverture backend (`app/` + `server/`):

- **Seuil actuel** : 62 %
- **Config** : `--cov-fail-under=62` dans `.github/workflows/tests.yml`
- **Source de verite** : le workflow CI ; `pytest.ini` documente le seuil sans l'imposer en local

Pour reproduire le gate coverage localement:

```bash
python -m pytest tests/ --ignore=tests/archives/ --ignore=tests/api/test_admin_auth_stability.py \
  --cov=app --cov=server --cov-fail-under=62 -m "not slow"
```

## Typing CI

Etat actuel:
- la CI lance encore un `mypy app/ server/ --ignore-missing-imports`
- le projet complete cela par des overrides plus stricts module par module dans `pyproject.toml`
- scopes deja durcis:
  - badge
  - auth session / recovery
  - exercise generation / query
  - challenge query / stream

## Faux positifs connus

### `tests/api/test_admin_auth_stability.py`

Ce test n'est pas un gate standard. Il lance `pytest` depuis `pytest`, ce qui le rend impropre comme preuve de validation normale. Il est exclu de la CI et des gates locaux.

### Lock `.coverage` sur Windows

Ne pas lancer plusieurs commandes `pytest` avec couverture en parallele sur Windows.

Symptomes typiques:
- `PermissionError` sur `.coverage`
- run rouge sans lien avec le code touche
- echec present seulement quand plusieurs jobs `pytest-cov` tournent en meme temps

Interpretation correcte:
- c'est un faux positif tooling
- ce n'est pas une preuve de regression runtime

## Cible actuelle a garder en tete

Etat global observe localement:
- les iterations backend `exercise/auth/user`, `challenge/admin/badge`, `Runtime Truth` et `Contracts / Hardening` sont cloturees
- les sujets restants sont hors scope des iterations cloturees et listes dans `docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md`

## Frontend - gates standards

```bash
cd frontend
npm run lint:ci
npm run test
```

Selon le lot:

```bash
npm run build
npm run test:e2e
```

## Commandes utiles par domaine

### Auth / user

```bash
pytest -q tests/api/test_auth_flow.py tests/api/test_user_endpoints.py tests/unit/test_auth_service.py tests/unit/test_user_service.py --maxfail=20
```

### Exercise / challenge

```bash
pytest -q tests/api/test_exercise_endpoints.py tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_exercise_service.py tests/unit/test_logic_challenge_service.py --maxfail=20
```

### Admin / badge

```bash
pytest -q tests/api/test_admin_ai_stats.py tests/api/test_admin_analytics.py tests/api/test_admin_badges.py tests/api/test_admin_content.py tests/api/test_admin_users_delete.py tests/api/test_badge_endpoints.py --maxfail=20
```

## Regles de redaction d'un verdict

Un lot est `GO` uniquement si:
- les endpoints reellement touches sont listes
- les fichiers runtime modifies sont listes
- la batterie cible passe deux fois
- la full suite requise est verte
- `black` et `isort` sont verts
- la cause d'un rouge precedent est prouvee ou explicitement exclue

## References

- [CREATE_TEST_DATABASE.md](CREATE_TEST_DATABASE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../../README_TECH.md](../../README_TECH.md)
- [../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](../03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md)
- [../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
