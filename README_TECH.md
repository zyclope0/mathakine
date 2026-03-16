# Technical README - Mathakine

> Updated: 16/03/2026

## Runtime Truth

- live backend runtime is the Starlette stack under `server/`
- active route truth is `server/routes/`
- active HTTP behavior is implemented by `server/handlers/` delegating to `app/services/`
- `app/api/endpoints/*` is archived and not part of the active runtime

## Current Stability Baseline

- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green
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

### Rate limiting

- production source of truth is Redis via `RedisRateLimitStore`
- `REDIS_URL` is mandatory in production
- Redis runtime failures are fail-closed on the protected scope
- challenge stream is now aligned on the same distributed backend limiter

## Explicit Remaining Debt

- global strict `mypy` is still out of scope
- coverage above `63 %` needs dedicated future lots
- large historical services still deserve bounded decomposition
- `app/services/enhanced_server_adapter.py` remains legacy compatibility
- `app/utils/db_utils.py::db_session()` remains legacy compatibility
- `app/utils/rate_limiter.py` is now legacy dead weight candidate, not active production truth
