# Remaining Follow-Ups - 2026-03-19

> Active recap of the points still outside the closed backend iterations.
> Updated after backend maturity audit, **closure of iteration `I`** (2026-03-19), and **closure of recommendation iteration `R`** (R7, 2026-03-21).

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
- **Recommendation remediation** (`R1`–`R7` closure, 2026-03-21) — see [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md)

Verified local baseline (post-G, post–H1–H3, **post–iteration `I` 2026-03-19**):
- gate standard backend: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `962 passed, 3 skipped`
- OpenAI live tests remain opt-in and are not part of the standard gate
- `test_admin_auth_stability.py` : test spécial, exclu du gate standard (non-bloquant)
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- backend CI coverage gate -> `63 %`

**Additional citation — post–recommendation iteration `R` (closure R7, 2026-03-21)** — does not erase the I-era gate above; re-run if the tree diverges:
- gate standard backend: same command → **`991 passed, 2 skipped`**
- reco ciblée: `pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` → **`40 passed`**
- frontend (from `frontend/`): `npm run lint`, `npm run format:check`, `npm run build` → **green** ; vitest `useRecommendationsReason` → **`3 passed`**
- backend quality: `black` / `isort` / `mypy` / `flake8` (same scopes as § Current Status) → **green**

## Active Remaining Points

### Recommendation iteration `R` — **closed** (R7 governance, 2026-03-21)

**Clôture** : [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md) — baseline, ce que R prouve / ne revendique pas, réserves résiduelles, verdict de maturité sobre.

**Trace technique** : R1 types canoniques, R2 diagnostic par type, R3 ranking stable + anti-répétition, R3b honnêteté discovery **puis R6** alignement pipeline, R4/R4b feedback + QuickStart, R5–R5d défis + raisons structurées + stabilité tests, R6 discovery explicite + `reason_code` exercice + i18n.

**Historique R3** : [CLOTURE_LOT_R3_REMEDIATION_MOTEUR_RECOMMANDATIONS_EXERCICE_2026-03-20.md](./CLOTURE_LOT_R3_REMEDIATION_MOTEUR_RECOMMANDATIONS_EXERCICE_2026-03-20.md) — bannière en tête : § 2.2 **supersédé** par R6 (ne plus lire la branche discovery comme vérité active).

### 0. Backend maturity truth (**iteration `I` closed** 2026-03-19)

**I1 — Architecture Truth and Data-Layer Doctrine: done (doc-only).** Active doctrine is now explicit in `docs/00-REFERENCE/ARCHITECTURE.md` § Data-Layer Doctrine.

**Lots `I2`–`I8` : done** — synthèse archivée : [iteration I archive](./archives/ITERATION_I_2026-03-19/README.md).

I1 established the truthful doctrine (toujours vraie après `I`) :
- runtime boundary via run_db_bound + sync_db_session is real
- repositories are selective (2 modules); many services still use ORM/Session directly
- no global repository isolation is claimed

Structural gaps **still real** (partiellement réduits par `I`, non effacés) :
- contrats faibles résiduels — réserves I2/I3
- hotspots challenge/diagnostic — réserves I4/I5/I7
- duplication handlers — réserve I6 (autres modules que `challenge_handlers`)
- legacy drift (`enhanced_server_adapter`, `HTTPException` dans `server/auth.py`) — non traité en I8 (doc-only)

Traceability archive for iteration `I` (**closed**) :
- [archives/ITERATION_I_2026-03-19/README.md](./archives/ITERATION_I_2026-03-19/README.md)

Ordered lots (état final) :
- `I1` — **done**
- `I2` — **done** (réserves actives)
- `I3` — **done** (réserves actives)
- `I4` — **done** (réserves actives)
- `I5` — **done** (réserves actives)
- `I6` — **done** (réserves actives)
- `I7` — **done** (réserves actives)
- `I8` — **done** (doc-only)

Documented review reserves from closed lots:
- `I1`: no active reserve remains after `I1b` fixed the stale baseline/date inconsistencies in `ARCHITECTURE.md` and `README_TECH.md`
- `I2`: `RefreshTokenResult` still carries `status_code`; the auth refresh boundary is improved but not yet fully de-HTTPized
- `I3`: `AdminContentMutationResult` still carries `status_code`, and `data` remains a weak `Dict[str, Any]`; the admin badge mutation boundary is improved but not yet fully normalized
- `I4`: `challenge_to_api_dict(...)` remains in `challenge_service.py` as a compatibility shim; the challenge retrieval/mapping split is real, but the list-path mapping boundary is not yet fully externalized
- `I5`: cluster **CODING** extrait vers `challenge_coding_validation.py` ; `validate_puzzle_challenge`, `validate_spatial_challenge`, `auto_correct_challenge` et le reste des validateurs restent denses dans `challenge_validator.py`. Réserve review : la batterie prescrite incluant `test_logic_challenge_service` peut être flaky en isolation DB (non causal pour le validateur) ; full gate vert après stabilisation.
- `I6`: pipeline erreur/réponse normalisé sur **`challenge_handlers.py`** via `ErrorHandler.create_error_response(..., handler_log_context=...)` ; la même duplication (logs + traceback + 500) subsiste dans **`exercise_handlers`**, **`auth_handlers`**, etc. — hors scope du lot.
- `I7`: cluster **pending storage** extrait vers `diagnostic_pending_storage.py` ; IRT, génération de questions, persistance `DiagnosticResult` / refresh reco restent dans `diagnostic_service.py` — hotspot résiduel documenté dans le pilotage I7.
- `I8`: **clôture itération** (doc-only) — pas de correctif runtime legacy dans ce lot ; voir réserves transversales ci-dessus (`enhanced_server_adapter`, `server/auth.py`).

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

After **iteration `I` (closed)** — voir aussi § *Recommended Next Iteration Candidates* dans le pilotage I8.

1. **Poursuites ciblées** (non lancées ici) :
   - handlers : même discipline I6 sur `exercise_handlers` / `auth_handlers` si prioritaire
   - challenge : validateur hors CODING ou externalisation liste/shim `challenge_to_api_dict`
   - diagnostic : IRT / persistance hors pending storage
   - contrats I2/I3 : retirer `status_code` des résultats de service sur chemins restants
   - legacy ponctuel : `server/auth.py`, `enhanced_server_adapter` — micro-lots avec preuve
2. continue badge engine decomposition after `I`
   - streak / regularity
   - performance / accuracy outside `success_rate`
3. continue admin mutation-boundary cleanup after `I`
   - `put_challenge`
   - other dense admin-content mutation paths still left after `I3`
4. decide later whether a bounded stricter typing island is still worth opening
   - without turning into global strict mypy
5. ~~optionally normalize imports toward app.core.db_boundary~~ - done by G4

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
Iteration `F` is closed. Lots `G` and Architecture Clean are also closed. **Iteration `I` is closed** (2026-03-19). **Recommendation iteration `R` is closed** (R7, 2026-03-21) — residual reco reserves live in R7, not as a reopened R-series.
The next backend work should use **this file** (`POINTS_RESTANTS`) and the summarized residual reservations captured here and in the iteration I archive — not generic reopenings of earlier series.

When a point is closed or re-scoped:
1. update this file
2. update the relevant active recap if needed
3. archive the old note instead of keeping duplicate active trackers




