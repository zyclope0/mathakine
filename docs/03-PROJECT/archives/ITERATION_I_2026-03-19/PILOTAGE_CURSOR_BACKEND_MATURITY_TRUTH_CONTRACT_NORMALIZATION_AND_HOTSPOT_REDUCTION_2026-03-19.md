# Pilotage Cursor - Backend Maturity Truth, Contract Normalization, and Hotspot Reduction

> Iteration `I`
> Created: 19/03/2026
> Status: **closed** (2026-03-19, lot I8)

## Why This Iteration Exists

The backend is now strong on runtime stability, validation discipline, and operability.
It is not yet uniformly strong on architectural truth, internal contracts, and hotspot density.

The maturity audit performed on 19/03/2026 confirmed four active structural gaps:
1. architecture truth and data-layer doctrine are not fully aligned with the code
2. service contracts and error conventions remain heterogeneous
3. challenge and diagnostic hotspots are still too dense
4. HTTP handlers are mostly thin per endpoint, but still too repetitive and too large at module level

This iteration exists to close those gaps without reopening a global rewrite.

## Verified Starting Point

Verified backend baseline at iteration **closure** (I8, 2026-03-19):
- gate standard backend:
  - `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`
  - `962 passed, 3 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- backend CI coverage gate -> `63 %`

Important note:
- one additional skip now comes from the OpenAI live test becoming opt-in under pytest
- `test_admin_auth_stability.py` remains a special non-gate test

## What The Audit Proved

### 1. Runtime and QA maturity are real

- standard backend gate is green
- formatting, import order, typing gate, and lint gate are green
- the backend remains reproducible and operable by command

### 2. Architecture purity is not yet uniform

- many services still use SQLAlchemy `Session` directly
- `app/repositories/` remains minimal and selective
- several service/application boundaries still expose tuples, booleans, and `status_code`
- challenge and diagnostic hotspots remain materially dense

### 3. The active architectural truth is narrower than some docs implied

What is true today:
- handlers are async
- business/application services are mostly sync
- DB-bound work goes through `run_db_bound(...)`
- sync services open `sync_db_session()` where needed

What is not yet true globally:
- repositories are not the dominant data-access abstraction across the backend
- service contracts are not yet uniform
- API mapping has not been fully separated from services

## Quantified Evidence

Audit counts on the current tree:
- `app/services/`: `64` service modules
- service modules importing `Session`: `40`
- repository files in `app/repositories/`: `2`

Representative files:
- data/ORM direct use:
  - `app/services/auth/auth_service.py`
  - `app/services/challenges/challenge_service.py`
  - `app/services/users/user_service.py`
  - `app/services/admin/admin_content_service.py`
  - `app/services/diagnostic/diagnostic_service.py`
- weak contract examples:
  - `app/services/auth/auth_session_service.py`
  - `app/services/users/user_application_service.py`
  - `app/services/admin/admin_content_service.py`
- dense hotspots:
  - `app/services/challenges/challenge_service.py`
  - `app/services/challenges/challenge_validator.py`
  - `app/services/diagnostic/diagnostic_service.py`
- repetitive handler modules:
  - `server/handlers/auth_handlers.py`
  - `server/handlers/user_handlers.py`
  - `server/handlers/exercise_handlers.py`

## What This Iteration Is Allowed To Change

- architecture-truth documentation and explicit doctrine
- bounded service-contract normalization
- bounded error-model normalization
- real decomposition of dense challenge and diagnostic hotspots
- bounded HTTP-layer normalization where duplication is obvious
- small residual legacy cleanup only if it naturally falls out of the scoped work

## What This Iteration Must Not Turn Into

- a global repository rollout
- a clean-architecture rewrite
- a public HTTP/API redesign
- a frontend iteration
- global strict mypy
- a blind coverage chase
- a broad service rewrite with no bounded proof

## Ordered Lots

### `I1` - Architecture Truth and Data-Layer Doctrine

Goal:
- make the active backend architecture claim defensible again
- explicitly state what is isolated today and what is not
- decide the real doctrine for `Session`, repositories, and sync services

### `I2` - Auth and User Boundary Contract Normalization

Goal:
- remove the most visible tuple and `status_code` leakage on auth/user application boundaries
- improve typed success/failure contracts without changing public HTTP behavior

### `I3` - Admin Boundary Contract Cleanup

Goal:
- reduce tuple/status leakage on admin application/content mutation boundaries
- make admin facade behavior more explicit and easier to test

### `I4` - Challenge Service Boundary and Decomposition

Goal:
- reduce density in `challenge_service.py`
- separate API-oriented mapping from core service responsibility on a bounded cluster

### `I5` - Challenge Validator Real Decomposition

Goal:
- decompose one real validation cluster inside `challenge_validator.py`
- reduce monolithic validation density without rewriting the whole module

### `I6` - Handler Error Pipeline and Response Normalization

Goal:
- reduce duplicated try/except/log/traceback boilerplate
- keep handlers thin in practice, not only in intention

### `I7` - Diagnostic Service Decomposition

Goal:
- split one dense responsibility cluster from `diagnostic_service.py`
- make the diagnostic module easier to explain, test, and evolve

### `I8` - Final Maturity Closure and Residual Legacy Cleanup

Goal:
- reassess the backend honestly after `I1` to `I7`
- close small residual framework/legacy drifts only if the gain is local and proven

## Required Execution Order

1. `I1`
2. `I2`
3. `I3`
4. `I4`
5. `I5`
6. `I6`
7. `I7`
8. `I8`

Rationale:
- `I1` fixes the truth model first, otherwise later lots optimize against an unclear target
- `I2` and `I3` tackle the most important contract weaknesses
- `I4` and `I5` address the largest challenge-domain structural hotspots
- `I6` becomes easier and safer once service boundaries are cleaner
- `I7` attacks the other major hotspot
- `I8` closes the iteration without overclaiming maturity

## Global Validation Rules

For each implementation lot:
1. prove the bounded scope before editing
2. keep HTTP behavior stable unless the lot explicitly says otherwise
3. add only the tests that prove the structural change
4. run the targeted battery twice
5. rerun the standard full gate when the blast radius is broader than the chosen seam
6. keep `black`, `isort`, `mypy`, and `flake8` green
7. do not claim maturity gain without visible reduction in ambiguity, density, or weak contracts

## Reserve Tracking Rule
For every lot review:
- if no reserve remains after review, say it explicitly
- if a reserve exists, document it in the lot file itself under a dedicated review-reserve section
- if the reserve remains active after GO, also propagate it into POINTS_RESTANTS_2026-03-15.md
- do not treat a reserve as implicitly closed just because the lot is GO
At iteration closure:
- consolidate all still-open reserves under a dedicated Residual Reservations Still Open section
- distinguish:
  - reserve fixed during the iteration
  - reserve accepted as still open
  - reserve requalified as non-priority

## Global GO / NO-GO

### GO if

- the lot stays bounded
- the architectural truth becomes clearer
- service contracts become more explicit
- hotspot density actually drops
- the backend becomes easier to explain and maintain

### NO-GO if

- the lot expands into generic cleanup
- the lot replaces one weak convention with another
- the lot changes HTTP behavior opportunistically
- the lot claims repository isolation globally without proving it
- the lot claims academic cleanliness while the core seams remain mixed

## Expected End State

If iteration `I` succeeds:
- the docs will tell the truth about the active backend architecture
- auth/user/admin boundaries will expose fewer weak contracts
- the challenge domain will have lower structural density
- diagnostic will be easier to reason about
- handlers will remain transport-oriented with less repeated glue code
- the backend will be more defensible as high-quality and industrializable, while staying honest about what still remains out of scope

---

## Iteration closure (I8, 2026-03-19)

- Statut itération : **closed**
- Synthèse finale, baseline vérifiée, réserves consolidées : [PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I8_FINAL_MATURITY_CLOSURE_AND_LEGACY_CLEANUP_2026-03-19.md](./PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I8_FINAL_MATURITY_CLOSURE_AND_LEGACY_CLEANUP_2026-03-19.md)
- Tracker actif des suites : [../../POINTS_RESTANTS_2026-03-15.md](../../POINTS_RESTANTS_2026-03-15.md)


