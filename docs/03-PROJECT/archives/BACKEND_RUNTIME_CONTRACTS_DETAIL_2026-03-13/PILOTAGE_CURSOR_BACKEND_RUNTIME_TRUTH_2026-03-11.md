# Iteration A - Runtime Truth & Boundary Completion

> Date: 11/03/2026
> Mise a jour statut: 13/03/2026
> Statut: cloturee
> Strategie: quality-first, max-effort
> Protocole: `CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`

## Objectif

Rendre l'execution backend coherente sans re-ecrire tout le metier:
1. sortir du faux async DB
2. homogeniser la regle `no DB in handlers`
3. fermer les boundaries hybrides restantes
4. documenter honnetement le legacy encore actif

## Decision d'architecture retenue

Pour cette iteration, pas de migration globale vers `AsyncSession`.

Modele cible:
- handlers HTTP `async`
- services / facades / repositories `sync`
- acces DB sync executes via `run_db_bound(...)`
- `sync_db_session()` dans les services proprietaires
- SSE/LLM laissent la couche generation en `async`, mais isolent les sous-appels DB en sync

## Etat reel au 13/03/2026

### Code runtime

Le code a ete largement aligne:
- `A1` a `A6` implementes
- lot final reliquats runtime implemente
- plus de `async with db_session()` restant dans le scope runtime actif traite, hors helper legacy de compatibilite dans `app/utils/db_utils.py`
- plus de `with sync_db_session()` dans `server/handlers/`

### Gates

Cloture prouvee localement avec gates reproduites:
- batterie runtime ciblee verte sur `run 1` et `run 2`
- full suite verte hors faux gate standard:
  - `821 passed, 2 skipped`
- `black --check` vert
- `isort --check-only --diff` vert

Le dernier blocage de cloture a ete ferme cote test:
- `tests/unit/test_exercise_service.py::test_list_exercises` stabilise
- `tests/unit/test_badge_requirement_engine.py::TestCheckRequirementsMinPerType::test_min_per_type_satisfied` realigne sur la semantique reelle du moteur

### Faux positifs de tooling a ne pas confondre

- lock `.coverage` sous Windows si plusieurs commandes `pytest` avec couverture tournent en parallele
- `tests/api/test_admin_auth_stability.py` reste hors gate standard

## Lots de l'iteration A

- `A1` : execution model
- `A2` : auth/session
- `A3` : lightweight handlers
- `A4` : exercise / recommendation boundaries
- `A5` : reserve `exercise_generation` + legacy adapter truth
- `A6` : facades sync
- lot final : reliquats runtime (`submit_answer`, services AI, `settings_reader`)

## Ce qui est ferme

- auth/session sur `run_db_bound(...)`
- facades admin / badge / user / challenge sync
- generation exercice active runtime alignee
- `settings_reader` sync + call sites async via `run_db_bound(...)`
- persistance DB des flux AI runtime isolee en sync

## Ce qui reste ouvert

- aucun blocage Runtime ouvert sur l'iteration A
- l'etape suivante logique est l'ouverture de l'iteration `Contracts / Hardening`

## Gate de cloture Runtime

Gate de cloture atteinte:
- batterie runtime ciblee verte deux fois
- full suite verte hors faux gate standard
- `black --check` vert
- `isort --check-only --diff` vert
- statut documentaire aligne sur ces preuves

## References

- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT1_EXECUTION_MODEL_2026-03-11.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT2_AUTH_SESSION_EXECUTION_2026-03-11.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT3_LIGHT_HANDLERS_2026-03-11.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT4_EXERCISE_RECO_BOUNDARIES_2026-03-11.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT5_LEGACY_ADAPTER_TRUTH_2026-03-11.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT6_FACADES_SYNC_2026-03-12.md`
- `PILOTAGE_CURSOR_BACKEND_RUNTIME_LOT_FINAL_RELIQUATS_2026-03-12.md`
