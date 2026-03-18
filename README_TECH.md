# Technical README - Mathakine

> Updated: 18/03/2026

## Runtime Truth

- live backend runtime is the Starlette stack under `server/`
- active route truth is `server/routes/`
- active HTTP behavior is implemented by `server/handlers/` delegating to `app/services/`
- runtime/data boundary: `app.core.db_boundary` (run_db_bound, sync_db_session) — all services import via db_boundary (G4)
- `app/api/endpoints/*` is archived and not part of the active runtime

## Current Stability Baseline (post-G, post–H1–H3, 2026-03-18)

Gate standard backend (`test_admin_auth_stability.py` exclu — test spécial non-bloquant) :
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `951 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- measured local coverage on `app` + `server`: `67.30 %`
- backend CI coverage gate -> `63 %`

## Active Architecture Notes

### Diagnostic

- the diagnostic flow uses a signed `state_token`
- `/api/diagnostic/question` does not expose `correct_answer`
- trusted answer correction is resolved server-side through an opaque `pending_ref`
- the frontend may receive `correct_answer` only after answer submission for feedback

### Runtime boundaries

- `MATH_TRAINER_DEBUG` defaults to `false`
- external JSON error payloads no longer expose traceback or raw exception details
- `MAX_CONTENT_LENGTH` is enforced before JSON/body parsing on the hardened request paths
- `/api/badges/available` is now explicitly bounded (`default=100`, `max=200`)

### Monitoring

- backend Sentry is initialized from `SENTRY_DSN` (fallback `NEXT_PUBLIC_SENTRY_DSN` kept only for backward compatibility)
- backend sends errors, HTTP traces, SQLAlchemy spans, and HTTP metrics
- backend profiling remains disabled by default (`SENTRY_PROFILES_SAMPLE_RATE=0`)
- frontend Sentry sends errors, traces, and Replay through `/monitoring`
- frontend Replay defaults are `0.1` baseline sessions and `1.0` on error
- Sentry release correlation should use the deployed commit via `SENTRY_RELEASE` / `NEXT_PUBLIC_SENTRY_RELEASE`

### Rate limiting

- production source of truth is Redis via `RedisRateLimitStore`
- `REDIS_URL` is mandatory in production
- Redis runtime failures are fail-closed on the protected scope
- challenge stream is now aligned on the same distributed backend limiter

## Architecture Clean (Cible A + B — closed)

- **Cible A** : `app/models/` and `app/schemas/` use explicit per-module imports; `all_models.py` and `all_schemas.py` have been removed (A1–A6).
- **Cible B** : `app/services/` is organised by DDD domains (auth, users, badges, exercises, challenges, progress, admin, analytics, communication, core, diagnostic, feedback, recommendation). No business logic file remains at root. See `docs/00-REFERENCE/ARCHITECTURE.md` § app/services/.

## Iteration E + F + G Outcome

The backend is now materially stronger on:
- bounded typed contracts on auth recovery / verification (E) and auth_service (F1)
- decomposition of challenge_service create flow (E) and badge_requirement_engine volume (F2)
- isolated badge requirement validation (E) and admin badge create flow (F3)
- scoped typing (F4) and runtime/data boundary formalization (F5)
- replicability and operability closure (F6)
- lots G: `authenticate_user_with_session` typed result (G1), success_rate cluster in volume (G2), admin exercise create flow (G3), db_boundary imports (G4)

## Explicit Remaining Debt (post-G)

- remaining tuple-shaped auth/admin paths not yet treated
- other clusters in badge_requirement_engine (consecutive, max_time, etc.) not decomposed
- admin mutation paths: put_challenge, other dense admin-content flows
- global strict mypy remains out of scope
- `app/services/core/enhanced_server_adapter.py` remains legacy compatibility
