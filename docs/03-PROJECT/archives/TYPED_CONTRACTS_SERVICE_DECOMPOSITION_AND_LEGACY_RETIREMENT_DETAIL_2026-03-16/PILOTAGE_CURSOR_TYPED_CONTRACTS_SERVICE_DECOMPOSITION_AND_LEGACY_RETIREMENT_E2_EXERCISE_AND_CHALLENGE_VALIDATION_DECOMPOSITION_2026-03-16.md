# Lot E2 - Exercise and Challenge Validation Decomposition

> Iteration `E`
> Status: closed (2026-03-16)

## Problem To Solve

`exercise_service.py` and `challenge_validator.py` remain dense and mix validation rules with broader orchestration.
That raises change-cost and makes narrow testing harder than necessary.

## Scope

Primary targets:
- `app/services/exercise_service.py`
- `app/services/challenge_validator.py`

Allowed support scope:
- closely related schemas or helper modules
- tests required to prove the new seams

Out of scope:
- challenge HTTP contract redesign
- generator rewrite
- frontend exercise work

## Required Outcome

- validation logic is more isolated from orchestration
- the treated modules become easier to read and easier to test in smaller units
- no public behavior drift is introduced casually

## Recommended Strategy

- identify one or two validation clusters with high branching
- extract or isolate them behind explicit helper/service boundaries
- keep orchestration readable at the parent service level

Do not try to make both modules “small” in one shot.

## Validation Expectation

- targeted service/API tests around the treated validation flows, twice
- full backend suite if shared validation paths are touched
- `black` and `isort` green

## E2 Implémentation (2026-03-16)

### Sous-scope traité
- `challenge_validator.py` + `challenge_pattern_sequence_validation.py` : logique « trouver la position de la première cellule '?' dans une grille » dupliquée 4 fois.

### Blocs de validation isolés
- `find_question_position_in_grid(grid) -> Optional[Tuple[int, int]]` : helper dédié dans `challenge_validation_analysis.py`.

### Structure retenue
- `challenge_validation_analysis.py` : ajout de `find_question_position_in_grid`
- `challenge_pattern_sequence_validation.py` : utilise le helper
- `challenge_validator.py` : utilise le helper dans `validate_grid_in_visual` et `auto_correct_challenge` (3 sites)

### Hors scope (inchangé)
- `exercise_service.py` : non traité (pas de cluster de validation identifié)
- Autres validateurs (PUZZLE, GRAPH, CODING, etc.) : inchangés
- Handlers : inchangés

## GO / NO-GO

GO:
- clearer validation seams
- lower rule density in the treated scope
- test proof improved on those rules

NO-GO:
- giant refactor with mixed concerns
- extraction that only renames code without reducing complexity

---

## Compte-rendu final E2 (format obligatoire)

### 1. Fichiers modifiés
- `app/services/challenge_validation_analysis.py` — ajout de `find_question_position_in_grid`
- `app/services/challenge_pattern_sequence_validation.py` — utilisation du helper
- `app/services/challenge_validator.py` — utilisation du helper (3 sites)
- `tests/unit/test_challenge_validation_analysis.py` — 4 tests pour `find_question_position_in_grid`
- `docs/03-PROJECT/PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_E2_EXERCISE_AND_CHALLENGE_VALIDATION_DECOMPOSITION_2026-03-16.md` — implémentation et compte-rendu

### 2. Fichiers runtime modifiés
- `app/services/challenge_validation_analysis.py`
- `app/services/challenge_pattern_sequence_validation.py`
- `app/services/challenge_validator.py`

### 3. Fichiers de test modifiés
- `tests/unit/test_challenge_validation_analysis.py`

### 4. Sous-scope choisi
Logique « trouver la position de la première cellule `?` dans une grille » dupliquée 4 fois dans `challenge_validator.py` et `challenge_pattern_sequence_validation.py`.

### 5. Blocs de validation isolés
- `find_question_position_in_grid(grid) -> Optional[Tuple[int, int]]` : helper pur, testable isolément.

### 6. Structure retenue après décomposition
- Helper dans `challenge_validation_analysis.py` (module déjà dédié à l’analyse de validation)
- Appels depuis `challenge_validator.py` (3 sites) et `challenge_pattern_sequence_validation.py` (1 site)

### 7. Ce qui a été prouvé
- Comportement stable : mêmes tests que les 4 sites existants.
- Testabilité locale : 4 tests unitaires dédiés à `find_question_position_in_grid`.
- Pas de changement de contrat HTTP ni de handler.

### 8. Ce qui n’a pas été prouvé
- `exercise_service.py` : non traité (aucun cluster de validation identifié)
- Autres validateurs (PUZZLE, GRAPH, CODING, etc.) : inchangés

### 9. Résultat run 1
94 passed (batterie cible : exercise_service, challenge_validation_analysis, exercise_endpoints, challenge_endpoints)

### 10. Résultat run 2
94 passed

### 11. Résultat full suite éventuelle
885 passed, 2 skipped (exécution précédente)

### 12. Résultat black
OK

### 13. Résultat isort
OK

### 14. Risques résiduels
- Aucun : blast radius limité au sous-scope, comportement observable inchangé.

### 15. GO / NO-GO
**GO**
