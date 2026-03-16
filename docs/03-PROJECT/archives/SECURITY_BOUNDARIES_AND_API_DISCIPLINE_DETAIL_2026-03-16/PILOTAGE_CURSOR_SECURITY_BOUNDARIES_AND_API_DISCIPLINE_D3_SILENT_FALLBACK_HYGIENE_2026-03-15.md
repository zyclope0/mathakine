# D3 - Silent Fallback Hygiene

> Date: 15/03/2026
> Status: pending
> Scope: small, objective cleanup of silent failure patterns

## 1. Mission

Remove or clarify small silent failure patterns on a tightly bounded scope.

## 2. Proven Current State

Known examples:
- `app/services/badge_user_view_service.py` contains `except ...: pass`
- `server/middleware.py` contains a fail-open maintenance fallback with only debug-level observability

## 3. Risk

- hidden degraded behavior
- weaker observability during incidents
- difficulty proving whether a fallback was intentional or accidental

## 4. Architecture Decision

Imposed decisions:
- no silent swallow without explicit fallback intent
- if a fail-open policy remains, it must be deliberate, documented in code, and logged clearly enough
- keep this lot small; do not broaden it into a global observability refactor

## 5. Allowed Scope

- `app/services/badge_user_view_service.py`
- `server/middleware.py`
- tests strictly needed for the changed behavior

## 6. Forbidden Scope

- broad logging framework changes
- global middleware redesign
- unrelated services

## 7. Files To Read Before Action

- `app/services/badge_user_view_service.py`
- `server/middleware.py`
- tests on badges or maintenance behavior if present

## 8. Validation

Minimum validation:
- targeted tests where causal
- run 1
- run 2
- full backend suite if middleware semantics change
- `black`
- `isort`

## 9. GO / NO-GO

`GO` only if:
- the identified silent patterns are either removed or explicitly clarified
- no broad refactor was required

`NO-GO` if:
- the lot grows beyond the bounded scope
- the result is still functionally silent in the same way
