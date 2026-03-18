# Remaining Follow-Ups - 2026-03-17

> Active recap of the points still outside the closed backend iterations.
> Updated after iteration `F` (Academic Backend Rigor, Replicability, and Operability) closure.

## Current Status

The backend iterations below are closed and should not be reopened as generic cleanups:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`
- `Production Hardening`
- `Security, Boundaries, and API Discipline`
- `Typed Contracts, Service Decomposition, and Legacy Retirement`
- `Academic Backend Rigor, Replicability, and Operability` (F1-F6)
- `Lots G (Residual Contracts and Cleanup)` (G1-G4)

Verified local baseline (post-G, post–H1–H3):
- gate standard backend: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `951 passed, 2 skipped`
- `test_admin_auth_stability.py` : test spécial, exclu du gate standard (non-bloquant)
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- backend CI coverage gate -> `63 %`

## Active Remaining Points

### 1. Residual weak internal contracts (addressed by F1 + G1)

F1 strengthened `auth_service` on `create_user`, `refresh_access_token`, `update_user_password`, and `create_registered_user_with_verification`.
G1 : `authenticate_user_with_session` retourne désormais `AuthenticateWithSessionResult`. Autres chemins auth/admin en tuples restent éventuels.

### 2. Badge requirement engine (partially addressed by F2 + G2 + H3)

F2 extracted the volume cluster to `badge_requirement_volume.py`. G2 : `success_rate` cluster. H3 : fallback `expert`/`perfectionist` délègue désormais à `check_success_rate` (source unique).
Other clusters in `badge_requirement_engine.py` remain; density is reduced but not closed.

### 3. Admin content mutation boundaries (addressed by F3 + G3)

F3 decomposed `create_badge` in `admin_badge_create_flow.py`. G3 : `create_exercise` décomposé dans `admin_exercise_create_flow.py`. Reste : `put_challenge` et autres chemins admin denses.

### 4. Strict typing (addressed locally by F4)

F4 strengthened typing on the admin badge create seam (`BadgeCreatePrepared`, `ValidationResult`).
Global strict mypy remains out of scope.

### 5. Runtime / data boundary (addressed by F5 + G4)

F5 formalized the boundary through `app.core.db_boundary`. G4 : tous les services importent `sync_db_session` depuis `app.core.db_boundary`.

### 6. Replicability and operability (addressed by F6)

F6 produced closure: invariants, baseline, reproducible commands, and explicit `What F Proved / What F Still Does Not Claim` sections.
Active docs now reflect the post-F truth.

## Next Technical Candidates

If a new backend-focused iteration is opened, the most causal candidates are:

1. **Architecture Clean** (pilotage dédié) — Cible A terminée ; Cible B (vertical slicing app/services/) **closed** (2026-03-18)
2. remaining weak internal contracts
   - remaining tuple-shaped auth/admin paths (G1 a traité authenticate_user_with_session)
3. continue badge engine decomposition
   - streak / regularity
   - performance / accuracy
4. continue admin mutation-boundary cleanup
   - `put_challenge`
   - other dense admin-content mutation paths (G3 a traité create_exercise)
5. decide whether a bounded stricter typing island is worth opening
   - without turning into global strict mypy
6. ~~optionally normalize imports toward app.core.db_boundary~~ — fait par G4

## Product / Frontend Gaps Still Plausible

No backend endpoint gap is currently proved as priority.
Potential future topics only if product evidence appears:
- additional admin/frontend exploitation of already existing backend capabilities
- UX polish if a real user-facing issue is reproduced again
- deeper proof on non-critical error branches if a new risk appears

## Lots G (Residual Contracts and Cleanup) — Closed (18/03/2026)

Archive: [archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md](./archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md)

Tous les lots G1–G4 réalisés.

## Architecture Clean — Cible A + Vertical Slicing

Pilotage : [PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md](./PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md)

- **Cible A** : Désamorçage imports globaux — **closed** (6 itérations A1–A6)
- **Cible B** : Vertical slicing app/services/ en sous-dossiers domaine (8 itérations B1–B8) — **closed** (2026-03-18)
- Méthodologie : Baby Steps, protocole Cursor Max Effort, validation QA par itération

## Maintenance Rule

This file is the active follow-up tracker for `docs/03-PROJECT`.
Iteration `F` is closed. The next backend lot should start from the points above rather than reopen `F` as generic cleanup.

When a point is closed or re-scoped:
1. update this file
2. update the relevant active recap if needed
3. archive the old note instead of keeping duplicate active trackers
