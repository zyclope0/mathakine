# Lot I4 - Challenge Service Boundary and Decomposition

> Iteration `I`
> Status: **done** (2026-03-19)

## Mission

Reduce real density inside `challenge_service.py` while separating API-facing mapping from core service responsibilities on a bounded cluster.

## Why This Lot Exists

`challenge_service.py` still combines too many concerns:
- age-group normalization
- DTO/API mapping
- challenge creation and validation steps
- persistence-oriented service orchestration

The file remains a historical hotspot even after earlier decomposition work.

## Primary Scope

- `app/services/challenges/challenge_service.py`
- strictly necessary helper/module extracted from it
- tests for challenge service and challenge endpoints

## In Scope

- select one dense cluster with real change-cost
- remove API-oriented mapping from the core service if that cluster touches it
- reduce local density and improve explainability

## Out of Scope

- full challenge domain rewrite
- challenge validator rewrite
- challenge AI stream rewrite
- frontend challenge payload redesign

## Recommended Target Cluster

Best candidates:
- list/query/API mapping cluster
- creation/preparation/validation cluster not yet fully normalized

Choose one and prove why it is the highest-value cluster before editing.

## Success Criteria

- lower density in `challenge_service.py`
- clearer separation of concern on the chosen cluster
- no HTTP contract break
- better local testability

## Required Proof

- show the chosen cluster before changes
- show the exact responsibilities separated after the lot
- state clearly what remains outside the chosen cluster

## Mandatory Validation

Target battery run 1:
- `pytest -q tests/unit/test_challenge_service.py tests/unit/test_challenge_validation_analysis.py tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py --maxfail=20 --no-cov`

Target battery run 2:
- same command

Full gate if the blast radius exceeds the chosen challenge seam:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`

Always:
- `black app/ server/ tests/ --check`
- `isort app/ server/ tests/ --check-only --diff`
- `mypy app/ server/ --ignore-missing-imports`
- `flake8 app/ server/ --select=E9,F63,F7,F82`

## Stop Conditions

- if the lot starts rewriting both query/list and generation/create paths at once
- if it drifts into validator or AI-stream cleanup
- if the only achievable gain is cosmetic file movement

---

## Compte-rendu I4 (2026-03-19)

### 1. Fichiers modifiés

- `app/services/challenges/challenge_age_group.py` — nouveau
- `app/services/challenges/challenge_api_mapper.py` — nouveau
- `app/services/challenges/challenge_service.py` — refactoré
- `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_MATURITY_TRUTH_CONTRACT_NORMALIZATION_AND_HOTSPOT_REDUCTION_I4_CHALLENGE_SERVICE_BOUNDARY_AND_DECOMPOSITION_2026-03-19.md` — ce document

### 2. Fichiers runtime modifiés

- `app/services/challenges/challenge_age_group.py` (nouveau)
- `app/services/challenges/challenge_api_mapper.py` (nouveau)
- `app/services/challenges/challenge_service.py`

### 3. Fichiers de test modifiés

- Aucun. Les tests existants couvrent le comportement observable.

### 4. Cluster choisi

**Cluster retrieval + mapping** : `get_challenge_for_api`, `challenge_to_api_dict`, et le mapping des groupes d'âge (frontend ↔ DB).

Justification : densité prouvée (mapping inline ~90 lignes mélangé à l'orchestration), séparation claire possible, pas de dépendance à challenge_validator.

### 5. Densité initiale constatée

- `challenge_service.py` : ~547 lignes
- Mapping age group : FRONTEND_TO_DB, DB_TO_FRONTEND, normalize_for_db, normalize_for_frontend (~80 lignes) mélangés en tête de fichier
- `challenge_to_api_dict` : ~20 lignes de mapping liste
- `get_challenge_for_api` : ~30 lignes de mapping détail inline (choices, visual_data, hints via safe_parse_json, etc.)
- Responsabilités mélangées : orchestration, requête, mapping API dans le même flux

### 6. Responsabilités séparées après décomposition

| Responsabilité | Module | Contenu |
|----------------|--------|---------|
| Mapping age_group frontend ↔ DB | `challenge_age_group.py` | FRONTEND_TO_DB_AGE_GROUP, DB_TO_FRONTEND_AGE_GROUP, normalize_age_group_for_db, normalize_age_group_for_frontend |
| Mapping LogicChallenge → dict API | `challenge_api_mapper.py` | challenge_to_list_item, challenge_to_detail_dict |
| Orchestration, requête, persistance | `challenge_service.py` | list_challenges, get_challenge, get_challenge_for_api (délègue mapping), create_challenge, etc. |

### 7. Structure retenue

```
app/services/challenges/
├── challenge_age_group.py    # Mapping age_group (nouveau)
├── challenge_api_mapper.py   # LogicChallenge → dict API (nouveau)
├── challenge_service.py      # Orchestration, délègue mapping
└── ...
```

`challenge_service` conserve `challenge_to_api_dict` et `normalize_age_group_for_frontend` en réexport pour compatibilité (challenge_ai_service, recommendation_service, enum_mapping).

### 8. Ce qui a été prouvé

- Comportement observable inchangé (tests challenge verts)
- Vraie baisse de densité dans challenge_service (~40 lignes retirées, mapping extrait)
- Séparation claire : mapping dans modules dédiés, orchestration dans challenge_service

### 9. Ce qui n'a pas été prouvé

- Pas de test unitaire direct sur challenge_api_mapper ou challenge_age_group (les tests API suffisent)

### 10. Résultat run 1

`93 passed, 1 skipped in 17.32s`

### 11. Résultat run 2

`93 passed, 1 skipped in 19.99s`

### 12. Résultat full gate

Non exécuté — blast radius limité au cluster retrieval + mapping.

### 13. Résultat black

`All done! 285 files would be left unchanged.`

### 14. Résultat isort

OK (aucun diff)

### 15. Résultat mypy

Exécution lancée ; pas d'erreur sur les fichiers modifiés.

### 16. Résultat flake8

OK (aucune erreur E9,F63,F7,F82)

### 17. Risques résiduels
- Revue stricte: l'extraction est réelle, mais un shim de compatibilité mapping reste encore dans `challenge_service.py`.
- `challenge_to_api_dict(...)` existe toujours comme façade vers `challenge_to_list_item(...)` pour les call sites existants.
- Conséquence: le cluster retrieval + mapping est mieux séparé, mais la boundary liste n'est pas encore totalement nettoyée du nommage/mapping historique.

### 18. GO / NO-GO

**GO** — Lot I4 clos. Cluster retrieval + mapping décomposé. Hors scope : cluster attempt/result view, cluster mutation admin, challenge_validator, list_challenges/count_challenges (filtres/ordering restent dans challenge_service).
### Review Reserve Tracking

Active reserve after review:
- challenge_to_api_dict(...) remains in challenge_service.py as a compatibility shim over challenge_to_list_item(...)

Consequence:
- the extraction is real and the density drop is defendable
- but the list-path mapping boundary is not yet fully externalized from challenge_service.py

Required future handling:
- either remove the shim in a later bounded lot, or explicitly decide to keep it as the stable public seam for challenge list mapping




