# D5 - Public Listing Bounds

> Date: 15/03/2026
> Status: closed (2026-03-15)
> Scope: bound the public badges listing endpoint

## 1. Mission

Introduce an explicit upper bound on `/api/badges/available` without turning the lot into a full pagination project.

## 2. Proven Current State (avant D5)

- `server/handlers/badge_handlers.py` expose `/api/badges/available`
- `app/services/badge_user_view_service.py` utilisait `.all()` sans borne

## 2b. État final D5 (scope strict)

- **Contrat** : `GET /api/badges/available?limit=N` (optionnel)
- **Borne par défaut** : 100
- **Borne max serveur** : 200
- **Preuve** : `.limit(effective_limit).all()` dans `badge_user_view_service.get_available_badges`
- **Tests D5** : `test_get_badges_available_limit_param`, `test_get_badges_available_limit_clamped_max`, `test_available_badges_max_limit_constant`, `test_available_badges_effective_limit_clamped`

## 3. Risk

- unbounded growth in response size
- increasing DB and memory cost as badge volume grows
- no explicit contract for callers

## 4. Architecture Decision

Imposed decisions:
- add an explicit service-side bound
- keep the contract simple
- a default limit plus a server-side maximum is preferred
- do not open a full cursor/pagination redesign unless trivially necessary

## 5. Allowed Scope

- `server/handlers/badge_handlers.py`
- `app/services/badge_user_view_service.py`
- API docs if the endpoint contract changes
- tests for limit/max behavior

## 6. Forbidden Scope

- broad badge system redesign
- frontend changes unless strictly unavoidable
- generalized pagination framework

## 7. Files To Read Before Action

- `server/handlers/badge_handlers.py`
- `app/services/badge_user_view_service.py`
- relevant badge tests
- API docs if query parameters already exist elsewhere as a pattern

## 8. Validation

Minimum validation:
- targeted badge endpoint tests
- run 1
- run 2
- full backend suite if the endpoint contract changes materially
- `black`
- `isort`

## 9. GO / NO-GO

`GO` only if:
- the listing is no longer unbounded
- the change remains simple and documented

`NO-GO` if:
- the endpoint still effectively returns all data without limit
- the implementation explodes into a bigger pagination program
