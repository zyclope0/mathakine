# Lot E3 - Challenge Service Boundary Clarification

> Iteration `E`
> Status: closed (2026-03-16)

## Problem To Solve

`challenge_service.py` remains a structural hotspot.
The target is to make its boundaries clearer between generation, validation, and persistence concerns without reopening the already-closed challenge/admin iteration at the HTTP level.

## Scope

Primary target:
- `app/services/challenge_service.py`

Allowed support scope:
- challenge helper modules or schemas strictly needed by the chosen decomposition
- tests needed to prove unchanged public behavior

Out of scope:
- challenge handler redesign
- admin endpoint redesign
- LLM product changes

## Required Outcome

- clearer internal separation between business stages
- reduced density in the treated challenge service seam
- preserved external behavior

## Recommended Strategy

- pick one dense orchestration path
- split stage-specific logic into smaller internal units
- keep the public service entrypoint stable if possible

## Validation Expectation

- targeted challenge tests twice
- full backend suite if shared challenge flows are touched
- `black` and `isort` green

## E3 Implémentation (2026-03-16)

### Flux choisi
`list_challenges` — chemin critique pour GET /api/challenges, utilisé par `challenge_query_service.list_challenges_for_api`.

### Densité initiale
La logique d’ordre et d’exécution était inline dans `list_challenges` (~30 lignes) :
- ordre "recent" : tri par date
- ordre "random" avec total : random_offset O(1) (B4.1)
- ordre "random" sans total : func.random() O(n) fallback

### Étapes séparées après décomposition
1. **Préparation** : requête de base + `_apply_challenge_filters`
2. **Ordre et exécution** : `_execute_list_with_ordering(query, order, limit, offset, total)`
3. **Résultat** : liste de LogicChallenge

### Structure retenue
- `_execute_list_with_ordering` : helper interne dans `challenge_service.py`, responsabilité unique (stratégie d’ordre + pagination)
- `list_challenges` : orchestration lisible (filtres → exécution)

### Hors scope (inchangé)
- Flux validation/correction (dans `challenge_ai_service.py`)
- `record_attempt`, `create_challenge`, `get_challenge_for_api`
- Handlers HTTP

## GO / NO-GO

GO:
- stage boundaries are clearer after the lot
- the treated path is easier to explain and test

NO-GO:
- "clean architecture" rewrite across challenge modules
- opportunistic product changes

---

## Compte-rendu final E3 (format obligatoire)

### 1. Fichiers modifiés
- `app/services/challenge_service.py` — ajout de `_execute_list_with_ordering`, simplification de `list_challenges`
- `tests/unit/test_challenge_service.py` — nouveau fichier, 3 tests pour le flux list
- `docs/03-PROJECT/PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_E3_CHALLENGE_SERVICE_BOUNDARY_CLARIFICATION_2026-03-16.md` — implémentation et compte-rendu

### 2. Fichiers runtime modifiés
- `app/services/challenge_service.py`

### 3. Fichiers de test modifiés
- `tests/unit/test_challenge_service.py` (nouveau)

### 4. Flux challenge choisi
`list_challenges` — liste des défis avec filtres et stratégie d’ordre (recent / random).

### 5. Densité initiale constatée
~30 lignes inline mélangeant 3 stratégies d’ordre (recent, random_offset, func.random) dans `list_challenges`.

### 6. Étapes séparées après décomposition
1. Préparation : requête + filtres (`_apply_challenge_filters`)
2. Ordre et exécution : `_execute_list_with_ordering`
3. Résultat : liste

### 7. Structure retenue
- Helper `_execute_list_with_ordering` dans `challenge_service.py`
- `list_challenges` délègue à ce helper après filtrage

### 8. Ce qui a été prouvé
- Comportement stable : tests API et unitaires verts
- Testabilité : 3 tests unitaires pour les modes order=recent, random+total, random sans total

### 9. Ce qui n’a pas été prouvé
- Flux validation/correction (challenge_ai_service)
- record_attempt, create_challenge, get_challenge_for_api

### 10. Résultat run 1
109 passed (batterie cible)

### 11. Résultat run 2
109 passed

### 12. Résultat full suite éventuelle
892 passed, 2 skipped

### 13. Résultat black
OK

### 14. Résultat isort
OK

### 15. Risques résiduels
Aucun : blast radius limité à `list_challenges`, comportement observable inchangé.

### 16. GO / NO-GO
**GO**

---

## E3b (2026-03-16) — Complément

Le micro-lot E3b a décomposé `create_challenge` en 4 étapes métier :
1. _prepare_challenge_data
2. _validate_challenge_data
3. _persist_challenge
4. create_challenge (orchestration)

Voir `PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_E3B_CHALLENGE_SERVICE_CREATE_FLOW_2026-03-16.md`.
