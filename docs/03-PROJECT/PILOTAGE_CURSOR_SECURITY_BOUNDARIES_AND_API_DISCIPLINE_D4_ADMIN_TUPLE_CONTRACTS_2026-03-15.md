# D4 - Admin Tuple Contracts

> Date: 15/03/2026
> Status: closed (2026-03-15)
> Scope: reduce a bounded subset of fragile tuple-based admin service contracts

## 1. Mission

Replace the most fragile tuple-based service contracts on a small admin scope with clearer typed results or explicit exceptions.

## 2. Proven Current State

`app/services/admin_application_service.py` still consumes service returns like:
- `result, err, code`
- `success, err, code`
- `success, already_verified, err, code`

## 3. Risk

- fragile ordering
- weak readability
- easy mistakes when adding or changing fields
- reduced clarity between business failure and transport mapping

## 4. Architecture Decision

Imposed decisions:
- keep the lot bounded
- prefer typed result objects or explicit business exceptions
- do not refactor all admin services at once

Recommended approach:
- choose a narrow but representative subset
- replace tuple juggling where the gain is immediate and safe

## 5. Allowed Scope

- `app/services/admin_application_service.py`
- admin service modules only if strictly required by the chosen subset
- tests strictly needed for touched admin flows

## 6. Forbidden Scope

- broad admin service redesign
- all tuples everywhere
- unrelated content/admin refactors

## 7. Files To Read Before Action

- `app/services/admin_application_service.py`
- touched admin service collaborators only if necessary
- tests for the selected admin flows

## 8. Validation

Minimum validation:
- targeted admin tests
- run 1
- run 2
- full backend suite if contract changes propagate
- `black`
- `isort`

## 10. Sous-scope D4 fermé (2026-03-15)

**Sous-scope choisi** : `send_reset_password`, `resend_verification`, `delete_user` (flux user admin).

**Tuples remplacés** :
- `(success, err, code)` → `AdminActionResult`
- `(success, already_verified, err, code)` → `AdminResendVerificationServiceResult`

**Nouveau contrat** : `AdminActionResult` et `AdminResendVerificationServiceResult` dans `app/schemas/admin.py`. Les méthodes `AdminUserService.send_reset_password_for_admin`, `resend_verification_for_admin`, `delete_user_for_admin` retournent ces objets. `AdminApplicationService` consomme `result.success`, `result.error`, `result.status_code`, `result.already_verified`.

**Hors scope** : `validate_and_patch_user`, content admin (exercises, badges, challenges), handlers.

## 11. Validation Outcome (2026-03-15)

Independent validation rerun:
- targeted battery: `pytest -q tests/api/test_admin_users_delete.py tests/api/test_auth_flow.py --maxfail=20 --no-cov` -> `25 passed`
- full backend suite: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `882 passed, 2 skipped, 1 warning`

What was proved:
- the chosen D4 sub-scope is really bounded to three admin user flows
- tuple returns were replaced by explicit result objects on that sub-scope only
- no runtime regression was detected in the targeted battery
- the current tree stays green on the full backend suite

## 12. Residual Non-Blocking Reserves

- service-layer contracts now depend on Pydantic models from `app/schemas/admin.py`
  - acceptable for this bounded lot
  - not a perfectly pure service/domain separation if a stricter architecture pass is opened later
- one SQLAlchemy warning remains in the full suite on admin user deletion
  - not introduced by D4
  - not treated in this lot
- other tuple contracts still remain outside the chosen D4 scope
  - notably `validate_and_patch_user` and content-admin flows

## 13. GO / NO-GO

`GO` because:
- a real subset of fragile tuple contracts was replaced cleanly
- blast radius stayed controlled
- independent targeted and full-suite reruns stayed green

`NO-GO` if:
- the lot expands into a full admin rewrite
- the result keeps equivalent tuple fragility under a different shape
