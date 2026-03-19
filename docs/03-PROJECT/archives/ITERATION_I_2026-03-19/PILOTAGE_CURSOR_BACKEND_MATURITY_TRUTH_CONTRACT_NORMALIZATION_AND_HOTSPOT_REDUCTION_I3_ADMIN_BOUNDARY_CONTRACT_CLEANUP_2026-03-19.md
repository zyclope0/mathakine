# Lot I3 - Admin Boundary Contract Cleanup

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Reduce tuple and `status_code` leakage on the admin application/content boundary.

The goal is not to rewrite all admin services.
The goal is to make the admin facade layer more explicit and more defensible.

## Why This Lot Exists

Admin paths still combine:
- tuples `(result, err, code)`
- `AdminError`
- result models
- weak dict-based content returns

This makes admin mutation flows harder to reason about than they should be.

## Primary Scope

- `app/services/admin/admin_application_service.py`
- `app/services/admin/admin_content_service.py`
- strictly necessary admin schemas/result models
- `server/handlers/admin_handlers.py` only where needed by the boundary cleanup

## In Scope

- normalize the facade behavior on admin content mutations
- reduce tuple/status plumbing crossing the facade
- make error semantics more uniform

## Out of Scope

- full admin domain rewrite
- admin read/query redesign
- frontend/admin UI
- repository rollout
- changes to business rules

## Success Criteria

- fewer tuple returns crossing `AdminApplicationService`
- clearer `AdminError` or typed-result semantics
- less ambiguity between application boundary and lower-level content services
- stable admin HTTP behavior

## Recommended Sub-Scope

Prefer one coherent cluster:
- exercise admin mutations
- badge admin mutations
- challenge admin mutations

Do not try to normalize the entire admin surface in one pass if the blast radius grows too large.

## Required Proof

- list the exact admin flows normalized
- show the old and new contract style
- explain what still remains mixed after the lot

## Mandatory Validation

Target battery run 1:
- `pytest -q tests/api/test_admin_content.py tests/api/test_admin_badges.py tests/api/test_admin_users_delete.py tests/unit/test_admin_badge_create_flow.py tests/unit/test_admin_exercise_create_flow.py --maxfail=20 --no-cov`

Target battery run 2:
- same command

Full gate if blast radius extends beyond the bounded admin seam:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

Always:
- `black app/ server/ tests/ --check`
- `isort app/ server/ tests/ --check-only --diff`
- `mypy app/ server/ --ignore-missing-imports`
- `flake8 app/ server/ --select=E9,F63,F7,F82`

## Stop Conditions

- if the lot becomes a general admin rewrite
- if it forces simultaneous cleanup of unrelated admin read/query paths
- if the seam cannot be improved without changing public admin payloads

---

## Compte-rendu I3 (2026-03-19)

### 1. Fichiers modifiés

- `app/schemas/admin.py` — ajout `AdminContentMutationResult`
- `app/services/admin/admin_content_service.py` — `create_badge_for_admin`, `put_badge_for_admin`, `delete_badge_for_admin` retournent `AdminContentMutationResult`
- `app/services/admin/admin_application_service.py` — les 3 méthodes badge consomment le result object
- `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I3_ADMIN_BOUNDARY_CONTRACT_CLEANUP_2026-03-19.md` — ce document

### 2. Fichiers runtime modifiés

- `app/schemas/admin.py`
- `app/services/admin/admin_content_service.py`
- `app/services/admin/admin_application_service.py`

### 3. Fichiers de test modifiés

- Aucun. Les tests existants couvrent le comportement observable.

### 4. Cluster choisi

**Cluster badge mutations** : `create_badge_for_admin`, `put_badge_for_admin`, `delete_badge_for_admin`.

Justification : meilleur ratio valeur/blast radius. 3 méthodes cohérentes, pattern identique, pas de dépendance challenge_validator. Exercise (4 méthodes) et challenge (4 méthodes) restent hors scope.

### 5. Contrats faibles remplacés

| Avant | Après |
|-------|-------|
| `create_badge_for_admin(...) -> Tuple[Optional[Dict], Optional[str], int]` | `create_badge_for_admin(...) -> AdminContentMutationResult` |
| `put_badge_for_admin(...) -> Tuple[Optional[Dict], Optional[str], int]` | `put_badge_for_admin(...) -> AdminContentMutationResult` |
| `delete_badge_for_admin(...) -> Tuple[Optional[Dict], Optional[str], int]` | `delete_badge_for_admin(...) -> AdminContentMutationResult` |

### 6. Nouveau contrat explicite retenu

**AdminContentMutationResult** : `data`, `error_message`, `status_code`, `is_success` (property).

AdminApplicationService utilise `r.is_success` pour le flux, puis `r.data` ou `raise AdminError(r.error_message, r.status_code)`. Plus de tuple unpacking sur la boundary badge.

### 7. Ce qui a été prouvé

- Comportement observable inchangé (tests admin badges verts)
- Vraie disparition des tuples `(result, err, code)` sur le cluster badge
- AdminApplicationService ne déballe plus de tuples anonymes pour les 3 méthodes badge

### 8. Ce qui n’a pas été prouvé

- Pas de test unitaire direct sur AdminContentService badge (les tests API suffisent)

### 9. Résultat run 1

`42 passed in 14.20s`

### 10. Résultat run 2

`42 passed in 14.10s`

### 11. Résultat full gate

Non exécuté — blast radius limité au cluster badge.

### 12. Résultat black

`All done! 283 files would be left unchanged.`

### 13. Résultat isort

OK (aucun diff)

### 14. Résultat mypy

`Success: no issues found in 3 source files`

### 15. Résultat flake8

OK (aucune erreur E9,F63,F7,F82)

### 16. Risques résiduels
- Revue stricte: la baisse de tuples est réelle, mais la boundary badge n'est pas encore totalement dé-HTTPisée ni totalement fortement typée.
- `AdminContentMutationResult` garde `status_code`.
- `AdminContentMutationResult.data` reste `Optional[Dict[str, Any]]` plutôt qu'un payload métier plus fort.

### 17. GO / NO-GO

**GO** — Lot I3 clos. Cluster badge mutations normalisé. Hors scope : cluster exercise (create, put, duplicate, patch), cluster challenge (create, put, duplicate, patch), get_badge/get_exercise/get_challenge (read, non mutation).

### Review Reserve Tracking

Active reserve after review:
- AdminContentMutationResult still carries status_code
- AdminContentMutationResult.data remains a weak Dict[str, Any]
Consequence:
- the badge mutation cluster no longer leaks tuple unpacking across the admin boundary
- but the boundary should not yet be described as fully normalized or fully de-HTTPized
Required future handling:
- keep this reserve active until a later lot either removes `status_code`, strengthens the success payload, or explicitly decides the boundary should remain HTTP-aware



