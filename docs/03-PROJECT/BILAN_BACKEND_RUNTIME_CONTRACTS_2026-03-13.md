# Bilan Backend Runtime + Contracts

> Date: 13/03/2026
> Status: active recap for `Runtime Truth` and `Contracts / Hardening`
> Scope: historical recap of those two iterations only

## 1. Global status at closure on 13/03/2026

| Iteration | Status | Closure proof |
|---|---|---|
| `exercise/auth/user` | closed | recap and delta 09/03/2026 |
| `challenge/admin/badge` | closed | recap and delta 11/03/2026 |
| `Runtime Truth` | closed | full suite excluding false gate green, `black` green, `isort` green |
| `Contracts / Hardening` | closed | lots `B1` to `B5` executed and validated |

Baseline retained at closure on 13/03/2026:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py` -> `823 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green
- backend CI coverage gate at closure -> `--cov-fail-under=62`

## 2. What Runtime brought

Closed architecture decision:
- HTTP handlers `async`
- services / facades / repositories `sync`
- sync DB access via `sync_db_session()`
- DB calls from handlers through `await run_db_bound(...)`
- SSE/LLM DB subcalls isolated in sync boundaries

Closed results on the treated scope:
- fake async removed from the refactored verticals
- handlers in scope no longer own DB sessions directly
- active exercise generation aligned with the runtime model
- admin / badge / user / challenge facades homogenized in sync boundaries
- `settings_reader` and the remaining runtime relics in scope were closed

## 3. What Contracts brought

### B1 - Challenge use cases
- stronger challenge attempt contracts
- challenge SSE preparation clarified
- challenge handlers limited to HTTP concerns

### B2 - Admin / badge contracts
- weak tuples hidden behind explicit boundaries
- admin / badge error mapping clarified
- API proof completed on admin challenge detail endpoints

### B3 - Hotspot decomposition
- `BadgeService` turned into a facade
- `badge_award_service.py` decomposed
- badge fallback dispatch made explicit
- `admin_stats_service.py` split by responsibility
- `challenge_validator.py` clarified with dispatch and extracted analyzers

### B4 - SQL / performance
- main `ORDER BY RANDOM()` path removed from `challenge_service.py`
- two query-in-loop hotspots removed from `recommendation_service.py`
- public challenge / recommendation contracts preserved

### B5 - CI / typing
- explicit CI coverage gate at `62 %`
- formal exclusion of the false gate `tests/api/test_admin_auth_stability.py`
- stricter mypy islands on:
  - badge
  - auth session / recovery
  - exercise generation / query
  - challenge query / stream
  - analytics / feedback / daily challenge / diagnostic

## 4. Post-closure updates that changed the current truth

This recap stays valid for the 13/03 closure state, but the current repository truth moved further during `Production Hardening` on 15/03/2026 and `Security, Boundaries, and API Discipline` on 16/03/2026.

Current notable updates:
- backend reference baseline is now `882 passed, 2 skipped`
- backend CI coverage gate is now `63 %`
- `app/api/endpoints/*` and `app/api/deps.py` are now archived in `_ARCHIVE_2026/app/api/`
- diagnostic endpoints now use a signed `state_token`
- runtime defaults and external error payloads are hardened
- request-size guards are enforced before the previously uncovered JSON/body parsing paths
- production rate limiting now relies on Redis

Read [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) and [archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md](./archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md) for the current post-hardening state.

## 5. What still remained outside Runtime + Contracts

At the end of these two iterations, the following items were still intentionally outside scope:
- global mypy strictness
- higher coverage gates such as `65 %` and `70 %`
- dense historical modules:
  - `app/services/auth_service.py`
  - `app/services/user_service.py`
  - `app/services/exercise_service.py`
  - `app/services/challenge_service.py`
  - `app/services/challenge_validator.py`
  - `app/services/admin_content_service.py`
  - `app/services/badge_requirement_engine.py`

## 6. Active sources of truth today

For the current state, read:
- `README_TECH.md`
- `docs/INDEX.md`
- `docs/00-REFERENCE/ARCHITECTURE.md`
- `docs/01-GUIDES/TESTING.md`
- `docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md`
- `docs/03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md`
- this document for the historical closure state of `Runtime Truth` and `Contracts / Hardening`

## 7. Archives

Detailed lot-by-lot `Runtime` and `Contracts` notes are archived here:
- `docs/03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/`
