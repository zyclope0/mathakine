# Lot final - Reliquats runtime factuels

> Date: 12/03/2026
> Mise a jour statut: 13/03/2026
> Statut: cloture

## Mission

Fermer les derniers reliquats runtime factuels sans ouvrir de refactor metier large.

## Reliquats traites

| Fichier | Probleme initial | Correctif implemente |
|---|---|---|
| `server/handlers/exercise_handlers.py` | `_submit_answer_sync()` ouvrait `sync_db_session()` dans la couche handler | entree sync deplacee dans `exercise_attempt_service.submit_answer_sync()` |
| `app/services/challenge_ai_service.py` | persistance DB via `async with db_session()` | persistance sync isolee + `run_db_bound(...)` |
| `app/services/exercise_ai_service.py` | persistance DB via `async with db_session()` | persistance sync isolee + `run_db_bound(...)` |
| `app/utils/settings_reader.py` | lecture DB via faux async | `get_setting_bool()` rendu sync |

## Ce qui est prouve sur le code

- plus de `async with db_session()` dans le scope du lot, hors helper legacy de compatibilite
- plus de `with sync_db_session()` dans `server/handlers/`
- call sites async de `get_setting_bool()` passes via `run_db_bound(...)`
- `submit_answer` n'ouvre plus la DB dans le module handler

## Micro-lot de fermeture deja passe

Le micro-lot de fermeture a bien corrige deux points reels:
1. collision fixture/cleanup sur `logic_challenge_db`
2. imports `isort` sur `challenge_ai_service.py` et `exercise_attempt_service.py`

Ce correctif a bien stabilise `tests/api/test_challenge_endpoints.py`.

## Statut reel des gates au 13/03/2026

### Vert prouve

- `tests/api/test_challenge_endpoints.py` : vert
- `black --check` : vert
- `isort --check-only --diff` : vert
- full suite hors faux gate : verte localement lors de la derniere verification documentaire
- full suite hors faux gate : `821 passed, 2 skipped`

### Cloture obtenue

Les derniers blockers de cloture ont ete fermes cote test:
- `tests/unit/test_exercise_service.py::test_list_exercises` stabilise
- `tests/unit/test_badge_requirement_engine.py::TestCheckRequirementsMinPerType::test_min_per_type_satisfied` aligne sur la semantique reelle de `min_per_type`

La batterie mixte et la full suite hors faux gate sont maintenant reproductiblement vertes localement.

## Faux positifs a ne pas confondre

- les locks `.coverage` observes sous Windows quand plusieurs `pytest` avec couverture tournent en parallele sont un faux positif de tooling
- ils ne doivent pas etre confondus avec un rouge runtime

## Verdict documentaire

- code runtime du lot final: implemente
- cloture de lot: prononcee
