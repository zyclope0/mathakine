# Lots G (Residual Contracts and Cleanup) - Archive

> Closed: 18/03/2026

## Scope

Four lots extending iteration F discipline without reopening F:
- **G1** — Contrat `authenticate_user_with_session` (AuthenticateWithSessionResult)
- **G2** — Extraction cluster `success_rate` (badge_requirement_volume)
- **G3** — Flux `create_exercise` admin (admin_exercise_create_flow)
- **G4** — Normalisation imports `db_boundary` (sync_db_session via db_boundary)

## Archived Document

| Document | Role |
|---|---|
| [PILOTAGE_LOTS_G_2026-03-17.md](./PILOTAGE_LOTS_G_2026-03-17.md) | Master plan, lot specifications, realisation notes |

## Closure Fix (2026-03-18)

- **G2** : Suppression du code mort `_progress_success_rate` resté dans `badge_requirement_engine.py` (PROGRESS_GETTERS utilisait déjà `progress_success_rate` depuis volume).

## Final Verified Baseline

- full suite (excl. test_admin_auth_stability): `952 passed, 2 skipped`
- black, isort, mypy, flake8: green
- backend CI coverage gate: `63 %`

## Active Sources Of Truth

This archive is traceability only. For current state:
- [../../POINTS_RESTANTS_2026-03-15.md](../../POINTS_RESTANTS_2026-03-15.md)
- [../../README.md](../../README.md)
- [../../../README_TECH.md](../../../README_TECH.md)
