# TESTING GUIDE - MATHAKINE

> Test strategy and gates
> Updated: 18/03/2026
> Scope: backend + frontend

## Principles

- documented truth requires reviewed code and reproduced gates
- a runtime or contracts lot is not valid if `run 2` fails
- targeted batteries matter more than a single isolated test
- the full suite is required when backend runtime or transversal wiring changes

## Backend Prerequisites

- local PostgreSQL reachable on `localhost:5432`
- `TEST_DATABASE_URL` distinct from `DATABASE_URL`
- Python dependencies installed via `pip install -r requirements.txt`

Quick preparation:

```bash
python scripts/check_local_db.py
```

Local backend verification script:

```bash
python scripts/test_backend_local.py
```

## Backend Standard Gates

### Full gate

```bash
git status --short
git diff --name-only
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
```

### Runtime / contracts / hardening lot gate

```bash
pytest -q <target-battery> --maxfail=20
pytest -q <target-battery> --maxfail=20
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
```

## Coverage In CI

Backend CI enforces a minimal coverage threshold on `app/` + `server/`:

- current gate: `63 %`
- config: `--cov-fail-under=63` in `.github/workflows/tests.yml`
- local source of truth: reproduce the workflow command, not `pytest.ini` comments alone

Command to reproduce the coverage gate locally:

```bash
python -m pytest tests/ --ignore=tests/archives/ --ignore=tests/api/test_admin_auth_stability.py \
  --cov=app --cov=server --cov-fail-under=63 -m "not slow"
```

## Typing In CI

Current state:
- CI still runs `mypy app/ server/ --ignore-missing-imports`
- the project complements this with stricter per-module overrides in `pyproject.toml`
- stricter islands already enabled on:
  - badge
  - auth session / recovery
  - exercise generation / query
  - challenge query / stream
  - analytics / feedback / daily challenge / diagnostic

## Known Tooling False Positives

### `tests/api/test_admin_auth_stability.py`

This test is not a standard gate. It launches `pytest` from inside `pytest`, so it is excluded from CI and normal local gates.

### `.coverage` lock on Windows

Do not launch multiple coverage-bearing `pytest` commands at the same time on Windows.

Typical symptoms:
- `PermissionError` on `.coverage`
- a red run with no causal relation to the changed code
- a failure that disappears when the same test battery is rerun with isolated coverage output

Correct handling:
- treat it as a tooling false positive, not as runtime proof
- for repeated coverage reruns, use a dedicated `COVERAGE_FILE` per run

## Current Verified State

As of 18/03/2026 (post-G, post–H1–H3):
- exercise/auth/user, challenge/admin/badge, Runtime Truth, Contracts/Hardening, Production Hardening, Security/Boundaries, Typed Contracts, Academic Backend Rigor (F1–F6), Lots G (G1–G4) are closed
- backend gate standard: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `951 passed, 2 skipped`
- `test_admin_auth_stability.py` : test spécial, exclu du gate standard (non-bloquant)
- measured local coverage on `app` + `server`: `67.30 %`
- backend CI coverage gate is `63 %`

## Frontend Standard Gates

Minimum frontend battery:

```bash
cd frontend
npm run lint:ci
npx tsc --noEmit
npm run test
```

When frontend runtime or build wiring changes:

```bash
npm run build
npm run i18n:validate
npm run test:e2e
```

## Useful Domain Batteries

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

## GO Rules

A lot is `GO` only if:
- touched endpoints or flows are listed
- touched runtime files are listed
- the target battery passes twice
- the required full suite is green
- `black` and `isort` are green
- any prior red run is causally explained or explicitly excluded

## References

- [CREATE_TEST_DATABASE.md](CREATE_TEST_DATABASE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../../README_TECH.md](../../README_TECH.md)
- [../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](../03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
