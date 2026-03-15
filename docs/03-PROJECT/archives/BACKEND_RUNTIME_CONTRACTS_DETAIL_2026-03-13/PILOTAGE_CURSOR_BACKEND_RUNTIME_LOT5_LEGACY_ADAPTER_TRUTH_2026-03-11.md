# Lot A5 - Legacy Adapter Truth

> Mise a jour : 13/03/2026
> Statut : valide en code, cloture documentaire corrigee

## Mission

1. fermer la reserve runtime reportee depuis A4 sur `exercise_generation`
2. documenter honnetement le legacy encore actif
3. eviter toute survente sur l'etat du backend Starlette

## Ce qui a ete ferme

### Reserve A4 `exercise_generation`

Le vertical de generation active runtime a ete aligne sur le modele cible:
- handlers async
- appel via `run_db_bound(...)`
- service sync avec `sync_db_session()`

Endpoint runtime actif concerne:
- `POST /api/exercises/generate`

Point important:
- le handler HTML `generate_exercise` existe encore mais n'est pas monte comme route Starlette active

## Legacy documente correctement

### Actif

- `enhanced_server_adapter.py`
- `app/utils/db_utils.py::db_session()` comme helper legacy de compatibilite

### Present mais non monte

- `app/api/endpoints/`
- preuve runtime: le wiring actif passe par `server/app.py` -> `get_routes()` puis `server/routes/*`

## Tests et preuves a retenir

- les tests de ce lot portent sur `generate_exercise_sync` et le wiring handler associe
- la correction documentaire de cloture a explicitement distingue:
  - handler modifie
  - endpoint runtime monte
  - legacy actif
  - legacy archive / inactif

## Risques residuels

- le legacy adapter n'est pas encore retire
- la simplification complete du legacy backend est repoussee a une iteration dediee

## Verdict

- reserve A4 `exercise_generation` : fermee
- statut A5 : GO
- la documentation ne doit plus affirmer `GET /generate` comme endpoint runtime actif
