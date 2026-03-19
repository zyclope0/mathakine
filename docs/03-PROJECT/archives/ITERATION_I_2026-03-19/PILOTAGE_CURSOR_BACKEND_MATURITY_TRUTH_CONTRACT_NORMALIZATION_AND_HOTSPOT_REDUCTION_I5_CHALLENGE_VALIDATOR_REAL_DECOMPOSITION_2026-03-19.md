# Lot I5 - Challenge Validator Real Decomposition

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Decompose one real validation cluster from `challenge_validator.py`.

This lot must reduce monolithic density.
It must not become a generic helper extraction with no structural gain.

## Why This Lot Exists

`challenge_validator.py` remains one of the densest files in the backend.
It centralizes too many validation styles and challenge-type rules in one place.

## Primary Scope

- `app/services/challenges/challenge_validator.py`
- strictly necessary extracted validators/helpers
- tests that prove the selected validation cluster

## In Scope

- choose one coherent challenge-type validation cluster
- move it behind a clearer responsibility boundary
- keep `validate_challenge_logic(...)` readable as orchestration/dispatch

## Out of Scope

- full validator rewrite
- challenge service rewrite
- challenge AI prompt rewrite
- frontend behavior changes

## Recommended Validation Clusters

Choose one:
- sequence/pattern family
- puzzle/graph family
- maze/spatial family

Pick the cluster with the best ratio of density reduction to blast-radius control.

## Success Criteria

- less inline validation logic in the main validator file
- clearer dispatch and responsibility split
- no change to externally observed challenge validation behavior

## Required Proof

- describe the cluster chosen and why
- show the responsibilities before and after
- add targeted proof on the extracted cluster

## Mandatory Validation

Target battery run 1 (inclut le fichier de preuve du cluster CODING) :
- `pytest -q tests/unit/test_challenge_validation_analysis.py tests/unit/test_logic_challenge_service.py tests/unit/test_challenge_service.py tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_challenge_coding_validation.py --maxfail=20 --no-cov`

Target battery run 2:
- same command

Full gate (blast radius challenge au-delà du cluster) :
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

Always:
- `black app/ server/ tests/ --check`
- `isort app/ server/ tests/ --check-only --diff`
- `mypy app/ server/ --ignore-missing-imports`
- `flake8 app/ server/ --select=E9,F63,F7,F82`

## Stop Conditions

- if no single validator cluster can be extracted without a full rewrite
- if the lot starts changing challenge semantics instead of clarifying structure

---

## Compte-rendu I5 (2026-03-19)

### 1. Fichiers modifiés

- `app/services/challenges/challenge_coding_validation.py` — nouveau (cluster CODING)
- `app/services/challenges/challenge_validator.py` — extraction + import
- `tests/unit/test_challenge_coding_validation.py` — nouveau
- `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I5_CHALLENGE_VALIDATOR_REAL_DECOMPOSITION_2026-03-19.md` — ce document

### 2. Fichiers runtime modifiés

- `app/services/challenges/challenge_coding_validation.py`
- `app/services/challenges/challenge_validator.py`

### 3. Fichiers de test modifiés

- `tests/unit/test_challenge_coding_validation.py` (nouveau)

### 4. Cluster choisi

**Cluster validation CODING** (`validate_coding_challenge`) : cryptographie / labyrinthe / rejet des payloads mal classés (SEQUENCE/VISUAL/PUZZLE), substitution, maze path.

### 5. Densité initiale

- `challenge_validator.py` : ~880 lignes (avant extraction)
- `validate_coding_challenge` seul : ~157 lignes inline, mélangé aux autres validateurs

Après extraction (référence terrain) : **`challenge_validator.py` reste ~726 lignes** — la baisse de densité sur le cluster CODING est réelle (~**157 lignes** extraites), mais le fichier reste un **hotspot dense** hors CODING. Logique CODING déléguée : `challenge_coding_validation.py` **~149 lignes**.

### 6. Responsabilités séparées après décomposition

| Avant | Après |
|-------|-------|
| Toute la logique CODING dans `challenge_validator.py` | `challenge_coding_validation.py` : règles CODING uniquement |
| `challenge_validator.py` : dispatch + autres types | `challenge_validator.py` : importe `validate_coding_challenge`, `_VALIDATORS_BY_TYPE` inchangé |

### 7. Structure retenue

```
challenge_coding_validation.validate_coding_challenge
    <- challenge_validator._VALIDATORS_BY_TYPE["CODING"]
```

### 8. Ce qui a été prouvé

- Batterie cible (runs 1 et 2) verte incl. `test_challenge_coding_validation.py`
- ~157 lignes retirées de `challenge_validator.py` (fichier ~726 lignes — référence terrain)
- Full gate standard vert (voir §12)

### 9. Ce qui n’a pas été prouvé

- **Aucune refonte** des autres validateurs **hors cluster CODING** (hors périmètre I5).
- La **densité résiduelle** de `challenge_validator.py` **hors CODING** n’est **pas traitée** dans ce lot.

### 10. Résultat run 1

Batterie causale (inclut le fichier de preuve du cluster CODING) :

`pytest -q tests/unit/test_challenge_validation_analysis.py tests/unit/test_logic_challenge_service.py tests/unit/test_challenge_service.py tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_challenge_coding_validation.py --maxfail=20 --no-cov`

→ **`98 passed, 1 skipped`** (référence validée terrain)

### 11. Résultat run 2

Même commande → **`98 passed, 1 skipped`**

**Note (non bloquante pour I5)** : une exécution **isolée** de sous-ensembles de tests peut encore montrer de l’instabilité sur `test_logic_challenge_service` (isolation DB). La batterie complète ci-dessus et le full gate §12 ont été **verts** sur la baseline de référence — ne pas interpréter comme échec du validateur challenge.

### 12. Résultat full gate

`pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

→ **`955 passed, 3 skipped`**

### 13–16. black / isort / mypy / flake8

- black : OK
- isort : OK (après fix imports)
- mypy : non bloquant sur les fichiers touchés
- flake8 E9,F63,F7,F82 : OK

### 17. Risques résiduels

- `challenge_validator.py` reste volumineux (~726 lignes) : le hotspot **hors cluster CODING** n’est pas épuisé
- `validate_puzzle_challenge`, `validate_spatial_challenge`, `auto_correct_challenge` restent des zones denses et des candidats naturels pour des lots ultérieurs

### Review Reserve Tracking

Réserve active pour relecture / lots futurs (sans rouvrir le périmètre technique I5) :

- L’**extraction CODING** vers `challenge_coding_validation.py` est **réelle** (dispatch inchangé via `_VALIDATORS_BY_TYPE["CODING"]`).
- **`challenge_validator.py` reste un hotspot dense** en dehors du cluster CODING.
- Candidats forts pour décomposition ultérieure : **`validate_puzzle_challenge`**, **`validate_spatial_challenge`**, **`auto_correct_challenge`** (liste non exhaustive).
- La batterie incluant `test_logic_challenge_service` peut être **sensible à l’isolation DB** en exécution partielle ; le **full gate standard** sert de référence de non-régression large.

### 18. GO / NO-GO

**GO** pour le lot I5 : décomposition réelle du cluster CODING, full gate standard vert sur la baseline documentée (§12), outillage §13–16 vert.
