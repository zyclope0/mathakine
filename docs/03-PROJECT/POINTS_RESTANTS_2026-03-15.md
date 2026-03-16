# Remaining Follow-Ups - 2026-03-15

> Active recap of the points still outside the closed backend iterations.
> Updated after `Production Hardening` and `Security, Boundaries, and API Discipline` closure.

## Current Status

The backend iterations below are closed and should not be reopened as generic cleanups:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`
- `Production Hardening`
- `Security, Boundaries, and API Discipline`

Verified local baseline:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green
- backend CI coverage gate -> `63 %`

## Active Remaining Points

### 1. Global typing remains partial

Still out of scope today:
- global strict `mypy`
- dense modules not yet migrated to stricter scoped typing

This is a maintainability topic, not a production blocker.

### 2. Coverage margin remains modest

Current gate is `63 %` and the margin is still limited.
Future increases should stay incremental and test-led.

Recommended direction:
- target low-coverage but bounded modules
- avoid raising the CI gate without proof first

### 3. Dense historical services remain to decompose

Standard D6 (Handler Subjectivity Review) : these modules are **future refactor candidates**, not immediate defects. See `archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D6_HANDLER_SUBJECTIVITY_REVIEW_2026-03-15.md`.

Main structural hotspots still worth bounded future lots:
- `app/services/auth_service.py`
- `app/services/exercise_service.py`
- `app/services/challenge_service.py`
- `app/services/challenge_validator.py`
- `app/services/admin_content_service.py`
- `app/services/badge_requirement_engine.py`

These are change-cost risks, not immediate blockers.

### 4. Remaining compatibility legacy

Still present in the runtime or service layer:
- `app/services/enhanced_server_adapter.py`
- `app/utils/db_utils.py::db_session()` compatibility usage

These should be treated as explicit legacy until removed, not as active architecture targets.

### 5. Legacy memory limiter to retire

`app/utils/rate_limiter.py` is no longer part of the active protected IA flow.
It now behaves as a legacy artifact candidate for removal or archive, not as the production source of truth.

## Product / Frontend Gaps Still Plausible

No endpoint integration gap is currently proved as priority.
Potential future topics only if there is product evidence:
- additional admin/frontend exploitation of already existing backend capabilities
- UX polish if a real user-facing issue is reproduced again
- deeper proof on non-critical error branches if a new risk appears

## Maintenance Rule

This file is the active follow-up tracker for `docs/03-PROJECT`.
The planned execution framework for the next architecture iteration is:
- `PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_2026-03-16.md`

When a point is closed or re-scoped:
1. update this file
2. update the relevant active recap if needed
3. archive the old note instead of keeping duplicate active trackers
