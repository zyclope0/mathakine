# Pilotage Cursor - Typed Contracts, Service Decomposition, and Legacy Retirement

> Iteration `E`
> Created: 16/03/2026
> Status: planned

## Why This Iteration Exists

The production hardening work is closed.
The remaining backend work is no longer about runtime safety first; it is about making the backend more explicit, more testable, and more academically clean without breaking stable HTTP contracts.

This iteration targets the explicit remaining debt still tracked in:
- [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md)
- [../../README_TECH.md](../../README_TECH.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)

## Proven Starting Point

Closed backend iterations that must not be reopened as generic cleanup:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`
- `Production Hardening`
- `Security, Boundaries, and API Discipline`

Current verified backend baseline before opening `E`:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green
- backend CI coverage gate -> `63 %`

## Iteration Goal

Make the backend more rigorous on three axes:
1. stronger internal typing and explicit service contracts
2. bounded decomposition of dense historical services
3. retirement of remaining compatibility shims and legacy runtime leftovers

This is a maintainability and long-term architecture iteration, not a product iteration.

## What `E` Is Allowed To Change

- service-level contracts and typed results
- bounded decomposition inside large historical service modules
- legacy compatibility code that no longer serves active runtime truth
- targeted coverage increases for changed structural modules
- scoped `mypy` tightening where the proof is real

## What `E` Must Not Turn Into

- a global "strict mypy everywhere" rewrite
- a repository pattern rollout across the whole codebase
- a public HTTP contract redesign
- a handler refactor wave across the entire backend
- a new monitoring or observability project
- a broad frontend iteration

## Ordered Lots

### `E1` - Auth Service Typed Contracts

Goal:
- replace weak internal result shapes on the `auth_service` bounded scope with explicit typed contracts or exceptions
- make password reset / verification / token invalidation flows easier to reason about and test

Primary scope:
- `app/services/auth_service.py`
- directly related schemas / tests only if strictly required

### `E2` - Exercise and Challenge Validation Decomposition

Goal:
- reduce density in `exercise_service` and `challenge_validator`
- isolate validation rules from orchestration and side-effects

Primary scope:
- `app/services/exercise_service.py`
- `app/services/challenge_validator.py`

### `E3` - Challenge Service Boundary Clarification

Goal:
- split the dense orchestration in `challenge_service`
- make generation / validation / persistence boundaries clearer

Primary scope:
- `app/services/challenge_service.py`

### `E4` - Admin Content and Badge Rule Decomposition

Goal:
- de-risk the two largest remaining historical business modules on the admin/badge side

Primary scope:
- `app/services/admin_content_service.py`
- `app/services/badge_requirement_engine.py`

### `E5` - Legacy Compatibility Retirement

Goal:
- remove or isolate remaining runtime compatibility shims that are no longer part of the intended architecture

Primary scope:
- `app/services/enhanced_server_adapter.py`
- `app/utils/db_utils.py`
- `app/utils/rate_limiter.py`

### `E6` - Coverage and Scoped Typing Uplift

Goal:
- consolidate the iteration by increasing proof quality on the treated modules
- raise confidence before any future CI gate increase

Primary scope:
- tests around modules touched by `E1` to `E5`
- scoped `mypy` hardening where the iteration created clean seams

## Required Execution Order

1. `E1`
2. `E2`
3. `E3`
4. `E4`
5. `E5`
6. `E6`

Rationale:
- `E1` creates the explicit contract style to reuse
- `E2` and `E3` tackle the highest-value dense service hotspots
- `E4` addresses the remaining large historical rule engines
- `E5` is cleaner once service truth is more explicit
- `E6` is the closure lot, not the opening move

## Global Validation Rules

For each implementation lot:
1. prove the chosen bounded scope before editing
2. keep HTTP behavior stable unless the lot explicitly says otherwise
3. add or update only the tests that prove the structural change
4. run the same targeted test battery twice
5. rerun the backend full suite if the blast radius is wider than the local scope
6. keep `black` / `isort` green

## Global GO / NO-GO

### GO if

- the lot stays bounded
- internal contracts become more explicit
- tests prove the new seams
- the code becomes easier to explain and easier to change

### NO-GO if

- the lot spreads into global architecture cleanup
- the lot changes HTTP behavior opportunistically
- the lot replaces one weak tuple/dict convention with another equally weak shape
- the lot claims architectural improvement without reducing real change-cost

## Expected End State

If iteration `E` is successful:
- the most fragile remaining service contracts are explicit
- the densest historical services are split into smaller units with clearer responsibilities
- legacy compatibility files are either retired or clearly isolated
- test proof on the structural hotspots is stronger than the current `63 %` gate baseline
