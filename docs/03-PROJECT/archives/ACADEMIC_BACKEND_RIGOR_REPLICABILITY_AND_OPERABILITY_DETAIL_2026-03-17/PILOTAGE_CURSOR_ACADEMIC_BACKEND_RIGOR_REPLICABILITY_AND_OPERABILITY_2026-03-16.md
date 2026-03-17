# Pilotage Cursor - Academic Backend Rigor, Replicability, and Operability

> Iteration `F`
> Created: 16/03/2026
> Status: closed (2026-03-17)

## Why This Iteration Exists

Iteration `E` improved the backend materially, but it did not fully close the gap to a backend that can be defended as:
- academically rigorous
- industrializable
- replicable
- adaptable
- manageable

The remaining work is not about runtime rescue anymore.
It is about finishing the structural discipline that still varies by module and by historical seam.

## Proven Starting Point

Closed backend iterations that must not be reopened as generic cleanup:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`
- `Production Hardening`
- `Security, Boundaries, and API Discipline`
- `Typed Contracts, Service Decomposition, and Legacy Retirement`

Current verified backend baseline before opening `F`:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `916 passed, 2 skipped`
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --cov=app --cov=server --cov-report=term --no-cov-on-fail` -> `71 %`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green (non-blocking `annotation-unchecked` notes remain)
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- backend CI coverage gate -> `63 %`

## What `E` Closed And What It Left Open

### Closed by `E`

- bounded typed auth-result contracts on the email verification / password reset scope
- a local challenge validation seam (`find_question_position_in_grid`)
- a real decomposition of `challenge_service.create_challenge`
- extraction of badge requirement validation from admin badge mutations
- retirement / clarification of selected legacy seams:
  - `app/utils/rate_limiter.py` removed
  - `app/utils/db_utils.py` simplified to `sync_db_session`
  - `app/services/enhanced_server_adapter.py` isolated as explicit compatibility legacy
- targeted proof uplift on the `badge_requirement_validation` and `db_utils` seams

### Not Closed by `E`

- residual weak internal contracts still present outside the bounded auth scope
- a real decomposition of `badge_requirement_engine.py`
- deeper mutation-boundary cleanup inside `admin_content_service.py`
- a stricter, better-scoped typing discipline on core historical modules
- a more formal runtime/data boundary story
- a stronger replicability and operability package for onboarding and repeatable execution

## Iteration Goal

Close the last structural gaps that prevent the backend from being described, without overstatement, as:
- academically rigorous in its internal contracts
- industrializable in its change model
- replicable in its environment and execution conventions
- adaptable without reopening dense hotspots each time
- manageable in day-to-day engineering and operations

This remains a bounded architecture iteration, not a rewrite.

## What `F` Is Allowed To Change

- residual weak service contracts on critical backend flows
- bounded decomposition of the densest historical service modules still left after `E`
- scoped typing upgrades with real proof value
- runtime/data boundary clarification where ambiguity still remains
- documentation and execution conventions required for replicability / operability closure

## What `F` Must Not Turn Into

- a global clean-architecture rewrite
- a repository rollout across the whole codebase
- a public API redesign
- a frontend iteration
- a broad observability expansion project
- a blind coverage chase
- strict mypy everywhere without bounded proof

## Ordered Lots

### `F1` - Residual Weak Contracts Elimination

Goal:
- replace remaining weak tuples / weak implicit result shapes on critical flows still left after `E`
- make success/failure contracts more uniform across the most important services

Primary scope:
- `app/services/auth_service.py`
- `app/services/admin_application_service.py`
- `app/services/admin_content_service.py`

### `F2` - Badge Requirement Engine Real Decomposition

Goal:
- decompose a real badge-rule cluster in `badge_requirement_engine.py` by business responsibility
- reduce local change-cost in the strongest remaining historical badge hotspot

Primary scope:
- `app/services/badge_requirement_engine.py`

### `F3` - Admin Content Mutation Boundary Cleanup

Goal:
- separate preparation, validation, persistence, and result mapping on a dense admin-content mutation path
- reduce the architectural ambiguity still left in `admin_content_service.py`

Primary scope:
- `app/services/admin_content_service.py`

### `F4` - Scoped Strict Typing Upgrade

Goal:
- push a bounded but meaningful typing upgrade on the seams clarified by `E` and `F1` to `F3`
- move from acceptable typing to defensible typed discipline on a real sub-scope

Primary scope:
- tightly bounded modules touched by `E` and early `F`

### `F5` - Runtime/Data Boundary Formalization

Goal:
- document and tighten the active service/data boundary where the runtime story still feels pragmatic rather than explicit
- reduce remaining ambiguity without opening a repository-pattern rewrite

Primary scope:
- bounded runtime/data seams still active after `E5`

### `F6` - Replicability and Operability Closure

Goal:
- close the gap between "works for the current project team" and "repeatably operable by another team"
- formalize the minimal runbook, environment, and engineering invariants required for backend repeatability

Primary scope:
- technical docs, environment truth, and repeatable validation rules

## Required Execution Order

1. `F1`
2. `F2`
3. `F3`
4. `F4`
5. `F5`
6. `F6`

Rationale:
- `F1` removes the weakest contracts still poisoning the core style
- `F2` and `F3` tackle the most visible historical hotspots left after `E`
- `F4` becomes more credible once those seams are clarified
- `F5` should formalize the boundary after the major service truth is cleaner
- `F6` closes the iteration by turning the result into something easier to operate and replicate

## Global Validation Rules

For each implementation lot:
1. prove the chosen bounded scope before editing
2. keep HTTP behavior stable unless the lot explicitly says otherwise
3. add only the tests that prove the structural change
4. run the targeted battery twice
5. rerun the full suite if the blast radius exceeds the bounded scope
6. keep `black`, `isort`, `mypy`, and `flake8` green
7. do not claim an academic/industrial gain without a visible reduction in change-cost or ambiguity

## Global GO / NO-GO

### GO if

- the lot stays bounded
- internal contracts become more explicit or more uniform
- local density actually drops on the chosen hotspot
- the code becomes easier to type, test, explain, and repeat
- the docs better reflect runtime truth and engineering invariants

### NO-GO if

- the lot spreads into global architecture cleanup
- the lot replaces one weak convention with another weak convention
- the lot changes HTTP behavior opportunistically
- the lot claims academic rigor without stronger internal discipline
- the lot claims replicability without improving environment / validation truth

## Expected End State

If iteration `F` is successful:
- critical internal contracts are much more explicit and uniform
- the strongest remaining historical hotspots are decomposed by business responsibility
- a bounded stricter typing discipline is in place on high-value seams
- runtime/data boundaries are easier to explain and defend
- the backend is more credible as industrializable, replicable, adaptable, and manageable

## Closure (F6)

See [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F6_REPLICABILITY_AND_OPERABILITY_CLOSURE_2026-03-16.md](PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F6_REPLICABILITY_AND_OPERABILITY_CLOSURE_2026-03-16.md) for:
- What F Proved
- What F Still Does Not Claim
- Replicability / Operability Invariants
- Validated Backend Baseline
