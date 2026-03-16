# Pilotage Cursor - Security, Boundaries, and API Discipline

> Date: 15/03/2026
> Status: closed (2026-03-16)
> Scope: objective security and input-boundary findings first, subjective architecture findings reframed

## 1. Mission

Close the external audit findings that are factually grounded in the current codebase, without reopening a broad architectural refactor.

This iteration exists to:
- harden runtime defaults and external error exposure
- enforce request-size boundaries before JSON parsing
- remove small but real silent failure patterns
- reduce one fragile service-contract pattern
- add explicit bounds to one public listing endpoint
- challenge the subjective audit points with a documented standard instead of a dogmatic rewrite

## 2. Verified Baseline Before Opening This Iteration

Reference baseline before opening the iteration on 15/03/2026:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `870 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green

## 3. Objective Findings vs Subjective Findings

### Objective findings to correct in code

1. `enhanced_server.py` starts with `MATH_TRAINER_DEBUG=true` by default
2. `app/utils/error_handler.py` can expose `error_type` and traceback `details` in API responses outside production when debug logging is active
3. `MAX_CONTENT_LENGTH` exists in config but no effective guard is applied before `await request.json()`
4. some small silent fallback patterns still exist:
   - `except ...: pass`
   - fail-open with weak observability
5. `app/services/admin_application_service.py` still uses heterogeneous tuple contracts
6. `/api/badges/available` is unbounded and returns `.all()` without explicit service-side limit

### Subjective findings to challenge, not blindly implement

1. handlers are still "too imperative"
2. some layers are "still anemic / infra-coupled"
3. `badge_requirement_engine.py` is large

These are not ignored, but they are not treated as immediate defects in this iteration unless a small, causal, low-risk improvement is obvious.

## 4. Iteration Order

Mandatory order:
1. `D1 - Debug and Error Exposure`
2. `D2 - Payload Size Enforcement`
3. `D3 - Silent Fallback Hygiene`
4. `D5 - Public Listing Bounds`
5. `D4 - Admin Tuple Contracts`
6. `D6 - Handler Subjectivity Review`

Order rationale:
- `D1` and `D2` are the strongest security boundary findings
- `D3` is small and objective
- `D5` is low-risk and easy to validate
- `D4` has more blast radius and comes later
- `D6` is intentionally last because it is partly a documentation/governance exercise

## 5. Scope Discipline

Rules for all lots:
- no broad runtime refactor
- no opportunistic redesign of unrelated modules
- one lot = one causal problem
- if a fix requires opening a large module outside the planned scope, stop and document
- tests and docs must follow the exact truth of the implemented behavior

## 6. Validation Protocol

For every lot:
- `git status --short`
- `git diff --name-only`
- targeted run 1
- targeted run 2
- `black app/ server/ tests/ --check`
- `isort app/ server/ --check-only --diff`

If a transverse runtime file is changed:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

No lot is `GO` if:
- run 2 is not green
- the fix leaves the original finding materially open
- the scope spills into a broader refactor without being documented and approved by the iteration rules

## 7. Active Documents for This Iteration

- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D1_DEBUG_ERROR_EXPOSURE_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D2_PAYLOAD_SIZE_ENFORCEMENT_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D3_SILENT_FALLBACK_HYGIENE_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D4_ADMIN_TUPLE_CONTRACTS_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D5_PUBLIC_LISTING_BOUNDS_2026-03-15.md`
- `docs/03-PROJECT/PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_D6_HANDLER_SUBJECTIVITY_REVIEW_2026-03-15.md`

## 8. Exit Condition for the Iteration

The iteration is closable only if:
- all objective findings treated in `D1` to `D5` are either closed or explicitly documented as blocked
- `D6` produces a clear standard on what remains acceptable vs what should become future refactor work
- active documentation reflects the final truth of the codebase

## 9. Final Outcome (2026-03-16)

Lot status:
- `D1 - Debug and Error Exposure`: closed
- `D2 - Payload Size Enforcement`: closed
- `D3 - Silent Fallback Hygiene`: closed
- `D5 - Public Listing Bounds`: closed
- `D4 - Admin Tuple Contracts`: closed
- `D6 - Handler Subjectivity Review`: closed

Final independently revalidated backend baseline:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ --check-only --diff` -> green

Iteration result:
- runtime defaults hardened
- external error payloads no longer expose traceback details
- request-size limits are enforced on the previously uncovered body/json paths
- small silent fallbacks were made explicit
- a bounded subset of fragile admin tuple contracts was replaced
- the public badges listing is now explicitly bounded
- the subjective audit claims are now reframed as a pragmatic standard, not as a false rewrite trigger
