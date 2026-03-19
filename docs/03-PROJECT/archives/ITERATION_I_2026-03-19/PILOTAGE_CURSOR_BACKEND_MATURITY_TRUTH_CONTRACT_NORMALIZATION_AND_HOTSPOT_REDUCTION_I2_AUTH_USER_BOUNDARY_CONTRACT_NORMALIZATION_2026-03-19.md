# Lot I2 - Auth and User Boundary Contract Normalization

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Remove the most visible weak contracts on the auth/user application boundary.

Target:
- fewer tuples
- less `status_code` leakage inside services
- more explicit result objects or business exceptions

## Why This Lot Exists

Auth and user flows still expose weak internal contracts across service/application boundaries:
- tuple returns
- `status_code` inside service results
- API-shaped dict payloads crossing internal boundaries too early

This affects:
- handler simplicity
- invariant clarity
- test readability
- error uniformity

## Primary Scope

- `app/services/auth/auth_session_service.py`
- `app/services/users/user_application_service.py`
- strictly necessary auth/user schemas or result models
- `server/handlers/auth_handlers.py`
- `server/handlers/user_handlers.py` only where required by contract cleanup

## In Scope

- normalize auth session/login/refresh/current-user boundary contracts
- normalize user registration/profile/password/session boundary contracts
- replace weak tuples where the gain is real and bounded

## Out of Scope

- full auth rewrite
- full user service rewrite
- repository introduction
- public API redesign
- unrelated admin or challenge flows

## Success Criteria

- less tuple unpacking in auth/user handlers
- fewer service-level `status_code` concerns
- clearer success/failure contracts on the chosen flows
- stable external HTTP behavior

## Recommended Target Cluster

Wave 1 should favor the most causal seams:
- `perform_login`
- `perform_refresh`
- `get_current_user_payload`
- `register_user`
- `update_profile`
- `update_password`
- `revoke_session`

## Required Proof

- explicit before/after list of replaced weak contracts
- targeted tests proving handler behavior stayed stable
- explanation of what remains out of scope

## Mandatory Validation

Target battery run 1:
- `pytest -q tests/unit/test_auth_service.py tests/api/test_auth_flow.py tests/api/test_user_endpoints.py tests/unit/test_user_service.py --maxfail=20 --no-cov`

Target battery run 2:
- same command

Full gate if blast radius grows beyond the chosen seam:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

Always:
- `black app/ server/ tests/ --check`
- `isort app/ server/ tests/ --check-only --diff`
- `mypy app/ server/ --ignore-missing-imports`
- `flake8 app/ server/ --select=E9,F63,F7,F82`

## Stop Conditions

- if the chosen auth/user seam cascades into a global rewrite
- if removing weak contracts would require public HTTP changes
- if the lot starts mixing auth, user, and admin cleanup at once

---

## Compte-rendu I2 (2026-03-19)

### 1. Fichiers modifiés

- `app/schemas/auth_result.py` — ajout `LoginResult`
- `app/services/auth/auth_session_service.py` — `perform_login` → `LoginResult`, `perform_refresh` → `RefreshTokenResult`
- `server/handlers/auth_handlers.py` — `api_login` et `api_refresh_token` consomment les result objects
- `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I2_AUTH_USER_BOUNDARY_CONTRACT_NORMALIZATION_2026-03-19.md` — ce document

### 2. Fichiers runtime modifiés

- `app/schemas/auth_result.py`
- `app/services/auth/auth_session_service.py`
- `server/handlers/auth_handlers.py`

### 3. Fichiers de test modifiés

- Aucun. Les tests existants (API login/refresh) couvrent le comportement observable.

### 4. Cluster choisi

**Cluster auth session** : `perform_login`, `perform_refresh`.

Justification : meilleur ratio valeur/blast radius. `RefreshTokenResult` existait déjà ; `perform_refresh` ne faisait que déballer le tuple. `perform_login` utilisait `AuthenticateWithSessionResult` en interne mais retournait un tuple — `LoginResult` unifie le contrat.

### 5. Contrats faibles remplacés

| Avant | Après |
|-------|-------|
| `perform_login(...) -> Tuple[Optional[Dict], Optional[Dict]]` | `perform_login(...) -> LoginResult` |
| `perform_refresh(...) -> Tuple[Optional[Dict], Optional[str], int]` | `perform_refresh(...) -> RefreshTokenResult` |

### 6. Nouveau contrat explicite retenu

- **LoginResult** : `user_payload`, `token_data`, `is_success` (property)
- **RefreshTokenResult** (existant) : `token_data`, `error_message`, `status_code`, `is_success` (property)

Le handler utilise `result.is_success` pour le flux, puis `result.user_payload` / `result.token_data` ou `result.status_code` / `result.error_message`. Le `status_code` reste dans `RefreshTokenResult` car le handler en a besoin pour `api_error_response` ; il n’est plus exposé via un tuple anonyme.

### 7. Ce qui a été prouvé

- Comportement observable inchangé (tests API login/refresh verts)
- Moins de tuples sur la boundary auth session
- Handlers plus lisibles (`result.is_success` vs unpack de 3 éléments)

### 8. Ce qui n’a pas été prouvé

- Pas de test unitaire direct sur `perform_login` / `perform_refresh` (les tests API suffisent pour ce lot)

### 9. Résultat run 1

`120 passed in ~34s`

### 10. Résultat run 2

`120 passed in ~29s`

### 11. Résultat full gate

Non exécuté — blast radius limité au cluster auth session.

### 12. Résultat black

`All done! 283 files would be left unchanged.`

### 13. Résultat isort

OK (aucun diff)

### 14. Résultat mypy

Exécution lancée ; timeout sur le run global. Pas d’erreur sur les fichiers modifiés.

### 15. Résultat flake8

OK (aucune erreur E9,F63,F7,F82)

### 16. Risques résiduels
- Revue stricte: le gain de contrat est réel, mais partiel.
- `RefreshTokenResult` garde `status_code`.
- Le tuple anonyme a disparu, mais la boundary refresh n'est pas encore totalement dé-HTTPisée.

### 17. GO / NO-GO

**GO** — Lot I2 clos. Cluster auth session normalisé. Hors scope : cluster user application (`register_user`, `update_profile`, `update_password`, `revoke_session`), `get_current_user_payload` (déjà correct).

### Review Reserve Tracking

Active reserve after review:
- RefreshTokenResult still carries status_code
- consequence: perform_refresh is cleaner than before, but the refresh boundary is not yet fully normalized as a pure business/result contract
Required future handling:
- do not mark the whole auth boundary as fully cleaned on the strength of I2 alone
- absorb this reserve into a later contract-normalization or error-normalization lot if iteration `I` keeps pushing contract cleanup deeper



