# Lot E4 - Admin Content and Badge Rule Decomposition

> Iteration `E`
> Status: closed (2026-03-16)

## Problem To Solve

Two large historical business modules remain obvious change-cost hotspots:
- `admin_content_service.py`
- `badge_requirement_engine.py`

They are not immediate defects, but they still concentrate too much logic for a backend that aims to be highly maintainable.

## Scope

Primary targets:
- `app/services/admin_content_service.py`
- `app/services/badge_requirement_engine.py`

Allowed support scope:
- small helper modules or schemas needed for the decomposition
- tests required to prove unchanged behavior

Out of scope:
- admin UI changes
- badge product redesign
- full rule-engine rewrite

## E4 Implémentation (2026-03-16)

### Cluster choisi
`_validate_badge_requirements` dans `admin_content_service.py` — validation des requirements avant create/put badge.

### Densité initiale
~55 lignes de if/elif par type de requirement (attempts_count, success_rate, consecutive, max_time, etc.).

### Responsabilités séparées après décomposition
- **badge_requirement_validation.py** : module dédié à la validation des requirements (structure + valeurs)
- **admin_content_service** : délègue via `_validate_badge_requirements` → `validate_badge_requirements`

### Structure retenue
- `app/services/badge_requirement_validation.py` : `validate_badge_requirements(req) -> (bool, Optional[str])`
- `admin_content_service._validate_badge_requirements` : wrapper qui délègue (compat AdminService)

### Hors scope (inchangé)
- badge_requirement_engine (checkers, progress getters)
- admin_content_service (mutations exercices, défis, export)
- handlers HTTP

## Required Outcome

- a bounded reduction of density in one or both modules
- clearer business grouping of rules or mutations
- no opportunistic public contract churn

## Recommended Strategy

- treat one dense cluster at a time
- prefer extraction by business concern over technical slicing
- keep the lot bounded even if the file remains large after the first pass

## Validation Expectation

- targeted tests around the treated admin/badge seam, twice
- full backend suite if shared admin or badge paths are affected
- `black` and `isort` green

## GO / NO-GO

GO:
- a real decrease in local complexity
- better grouping of rules or mutations

NO-GO:
- full engine rewrite
- cosmetic reorganization without lowering change-cost

---

## Compte-rendu final E4 (format obligatoire)

### 1. Fichiers modifiés
- `app/services/badge_requirement_validation.py` — nouveau module
- `app/services/admin_content_service.py` — délégation vers badge_requirement_validation
- `tests/unit/test_badge_requirement_validation.py` — nouveau
- `docs/03-PROJECT/PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_E4_ADMIN_CONTENT_AND_BADGE_RULE_DECOMPOSITION_2026-03-16.md`

### 2. Fichiers runtime modifiés
- `app/services/badge_requirement_validation.py` (nouveau)
- `app/services/admin_content_service.py`

### 3. Fichiers de test modifiés
- `tests/unit/test_badge_requirement_validation.py` (nouveau)

### 4. Cluster choisi
`_validate_badge_requirements` dans admin_content_service.

### 5. Densité initiale constatée
~55 lignes de if/elif par type de requirement.

### 6. Responsabilités séparées après décomposition
- Validation : badge_requirement_validation (module dédié)
- Orchestration admin : admin_content_service (délégation)

### 7. Structure retenue
Module dédié + wrapper dans admin_content_service.

### 8. Ce qui a été prouvé
- Comportement stable : tests admin_content, admin_badges, badge_requirement_engine
- Testabilité : 10 tests unitaires pour validate_badge_requirements

### 9. Ce qui n'a pas été prouvé
- badge_requirement_engine (checkers, progress)
- autres clusters admin_content_service

### 10. Résultat run 1
40 passed

### 11. Résultat run 2
40 passed

### 12. Résultat full suite éventuelle
Blast radius limité au flux badge admin (create/put). Batterie cible 40 passed x2.

### 13. Résultat black
OK

### 14. Résultat isort
OK

### 15. Risques résiduels
Aucun : comportement observable inchangé, délégation transparente.

### 16. GO / NO-GO
**GO**
