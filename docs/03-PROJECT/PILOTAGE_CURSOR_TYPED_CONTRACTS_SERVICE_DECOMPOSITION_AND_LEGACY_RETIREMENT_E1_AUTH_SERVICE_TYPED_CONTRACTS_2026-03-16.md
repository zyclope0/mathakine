# Lot E1 - Auth Service Typed Contracts

> Iteration `E`
> Status: closed (2026-03-16)

## Problem To Solve

`auth_service.py` remains one of the densest active modules and still carries internal flows that are harder to reason about than they should be.
The goal is not to redesign auth HTTP contracts again, but to make the bounded internal contracts explicit and safer.

## Scope

Primary target:
- `app/services/auth_service.py`

Allowed support scope:
- auth-related schemas strictly needed to express explicit service contracts
- tests that prove the treated auth flows

Out of scope:
- frontend auth UX
- handler redesign
- email provider redesign
- global auth rewrite

## Required Outcome

- weak internal return shapes are replaced by explicit contracts or explicit exceptions on the chosen auth sub-scope
- password reset / verification / token invalidation flows become easier to read and test
- public HTTP behavior remains stable

## Recommended Bounded Sub-Scope

Treat only a coherent high-value subset, for example:
- resend verification
- forgot / reset password
- token invalidation after password change or reset

Do not try to rewrite the entire auth service in one lot.

## Validation Expectation

- targeted auth tests, twice
- full backend suite if the treated auth seam affects multiple endpoints
- `black` and `isort` green

## E1 Implémentation (2026-03-16)

### Sous-scope traité
- `verify_email_token` (auth_service)
- `reset_password_with_token` (auth_service)

### Retours faibles remplacés
- `verify_email_token`: `Tuple[Optional[User], Optional[str]]` → `VerifyEmailTokenResult`
- `reset_password_with_token`: `Tuple[Optional[User], Optional[str]]` → `ResetPasswordTokenResult`

### Nouveau contrat
- `app/schemas/auth_result.py`: `VerifyEmailTokenResult`, `ResetPasswordTokenResult` (dataclasses avec `user`, `error_code`, `is_success`)
- `auth_recovery_service` consomme les résultats via `result.error_code`, `result.user`

### Hors scope (inchangé)
- `refresh_access_token` (tuple)
- `update_user_password` (tuple)
- `create_user` (tuple)
- `resend_verification_token`, `initiate_password_reset` (retournent str — déjà explicite)

## GO / NO-GO

GO:
- explicit contracts on a real auth seam
- preserved public behavior
- simpler testability

NO-GO:
- auth mega-refactor
- handler churn without causal gain
- vague “cleaner code” claim without a real contract improvement
