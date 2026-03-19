# CI/CD, DEPLOY ET ROLLBACK

> Mise a jour : 15/03/2026
> Source de verite CI : `.github/workflows/tests.yml`

## CI active

Le workflow principal est `CI (Tests + Lint)`.

Declenchement:
- `push` sur `main`, `master`, `develop`
- `pull_request` vers `main`, `master`, `develop`

Jobs actifs:
- `test` : backend pytest + couverture + smoke `/health`
- `lint` : flake8 critique, black, isort, mypy
- `frontend` : TypeScript, ESLint, Prettier, Vitest, build Next.js
- `codecov` : agrege les artefacts de couverture

## Ce que verifie la CI backend

### Test job

- PostgreSQL 15 en service GitHub Actions
- creation / initialisation de `test_mathakine`
- `python -m pytest tests/ -v --ignore=tests/archives/ --ignore=tests/api/test_admin_auth_stability.py --cov=app --cov=server --cov-fail-under=63 --tb=short -m "not slow"`
- smoke test `GET /health`

### Lint job

- `flake8 app/ server/ --select=E9,F63,F7,F82`
- `black app/ server/ tests/ --check --diff`
- `isort app/ server/ tests/ --check-only --diff`
- `mypy app/ server/ --ignore-missing-imports`

### Typing progressif

En plus du mypy global permissif, `pyproject.toml` porte des overrides plus stricts sur des ilots cibles.
Etat reel apres le service slicing:
- auth session / recovery : overrides alignes
- badge / exercise / challenge : overrides realignes vers les nouveaux chemins de modules
- analytics / feedback / daily challenge / diagnostic : overrides deja sur les chemins de domaine

### Frontend job

- `npm ci`
- `npx tsc --noEmit`
- `npm run lint`
- `npm run format:check`
- `npx vitest --coverage --run`
- `npm run build`

## Ce que la CI ne prouve pas encore

- elle n'impose pas encore un mypy global strict
- le faux gate `tests/api/test_admin_auth_stability.py` ne doit pas servir de reference locale standard
- une full suite verte en CI ne remplace pas un diagnostic causal quand un lot local rouge est flake

## Verification locale recommandee avant push

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
cd frontend && npm run lint
```

## Smoke post-deploiement

Verifications minimales:

```bash
curl -s https://mathakine-backend.onrender.com/health
curl -s -o /dev/null -w "%{http_code}" https://mathakine-frontend.onrender.com/
```

## Migrations Alembic

Le backend applique `alembic upgrade head` pendant le build/deploiement.

Commandes utiles:

```bash
alembic current
alembic history -r current:head
alembic revision -m "description_courte"
alembic upgrade head
```

## Rollback

### Code

Depuis Render:
1. ouvrir le service
2. aller sur `Deploys`
3. choisir un deploy reussi
4. lancer un rollback manuel

### Base de donnees

Avant tout downgrade:
- faire un backup
- verifier que le code cible supporte l'etat schema voulu

Commandes utiles:

```bash
alembic downgrade -1
alembic downgrade <revision>
```

## References

- [../01-GUIDES/DEPLOYMENT_ENV.md](../01-GUIDES/DEPLOYMENT_ENV.md)
- [../01-GUIDES/TROUBLESHOOTING.md](../01-GUIDES/TROUBLESHOOTING.md)
- [../../README_TECH.md](../../README_TECH.md)
- [../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
- [../03-PROJECT/POINTS_RESTANTS_2026-03-15.md](../03-PROJECT/POINTS_RESTANTS_2026-03-15.md)
