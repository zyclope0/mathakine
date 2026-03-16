# Bilan Production Hardening

> Date: 15/03/2026
> Status: active recap
> Scope: closed recap of iteration `Production Hardening`

## 1. Global Status

| Lot | Status | Main proof |
|---|---|---|
| `C1 - Diagnostic integrity` | closed | signed state token plus server-side pending answer truth |
| `C2 - Distributed rate limit` | closed | Redis source of truth in prod, fail-closed on Redis runtime failure |
| `C3 - Coverage margin` | closed | CI coverage gate raised from `62 %` to `63 %` |
| `C4 - Legacy API truth` | closed | `app/api/endpoints/*` archived and removed from live runtime |
| `C5 - Hygiene / DRY` | closed | duplicated OpenAI import block removed |

Latest verified local baseline carried by active docs:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green
- backend CI coverage gate -> `--cov-fail-under=63`

## 2. What Changed

### C1 - Diagnostic integrity

- diagnostic mutation steps now rely on a signed `state_token`
- `/api/diagnostic/question` no longer leaks `correct_answer`
- backend answer validation no longer trusts client-supplied answer truth
- the token carries an opaque `pending_ref`; the trusted pending answer data is stored server-side until `/answer`
- frontend diagnostic feedback uses the answer returned by `/api/diagnostic/answer` after submission only

### C2 - Distributed rate limit

- production source of truth is `RedisRateLimitStore`
- `REDIS_URL` is required in production startup validation
- Redis runtime failures on the protected scope are fail-closed
- memory fallback is restricted to dev/test
- protected scope closed in this iteration:
  - login
  - validate-token
  - forgot-password
  - resend-verification
  - register
  - chat and chat stream
  - challenge stream generation flow

### C3 - Coverage margin

- CI coverage gate moved from `62 %` to `63 %`
- targeted tests were added around:
  - `app/services/challenge_validation_analysis.py`
  - `server/handlers/chat_handlers.py`
- current margin is improved but still modest, so future increases must remain incremental

### C4 - Legacy API truth

- `app/api/endpoints/*` and `app/api/deps.py` were archived in `_ARCHIVE_2026/app/api/`
- no active runtime wiring or imports remain in the live Starlette stack
- active route truth is now explicitly documented as `server/routes/` + `server/handlers/`

### C5 - Hygiene / DRY

- the duplicated `AsyncOpenAI` import block in `server/handlers/chat_handlers.py` was removed
- no functional behavior changed

## 3. Documentation Truth Updated With This Iteration

Active documentation now reflects:
- the signed diagnostic contract with server-side pending answer storage
- the production Redis requirement for rate limiting
- the `63 %` CI coverage gate
- the archival of `app/api/endpoints/*`
- the latest verified local baseline (`882 passed, 2 skipped`)

Detailed execution notes for the iteration are archived and no longer act as the primary reference.

## 4. What Remains Outside This Iteration

Not solved by `Production Hardening`:
- global strict mypy on all runtime modules
- coverage increase beyond `63 %`
- dense historical services (`auth_service`, `exercise_service`, `challenge_service`, `challenge_validator`, `admin_content_service`, `badge_requirement_engine`)
- compatibility legacy still present:
  - `app/services/enhanced_server_adapter.py`
  - `app/utils/db_utils.py::db_session()`
- `app/utils/rate_limiter.py` remains only as legacy cleanup candidate, not as active production limiter

## 5. Active Sources Of Truth

Read these documents for the current backend state:
- `README_TECH.md`
- `docs/INDEX.md`
- `docs/00-REFERENCE/ARCHITECTURE.md`
- `docs/01-GUIDES/TESTING.md`
- `docs/01-GUIDES/DEPLOYMENT_ENV.md`
- `docs/02-FEATURES/API_QUICK_REFERENCE.md`
- `docs/02-FEATURES/F03_DIAGNOSTIC_INITIAL.md`
- `docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md`
- this document

## 6. Archives

Detailed iteration documents are archived here:
- `docs/03-PROJECT/archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/`
