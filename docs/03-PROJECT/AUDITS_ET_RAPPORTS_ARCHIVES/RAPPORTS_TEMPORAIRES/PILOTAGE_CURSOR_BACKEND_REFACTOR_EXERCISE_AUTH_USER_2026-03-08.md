# Pilotage Cursor - Refactor Backend Exercise Auth User - 2026-03-08

## Statut
- Iteration backend `exercise/auth/user` cloturee.
- Version interne finale : `1.0.0`
- Release produit recommandee : `3.1.0-alpha.7`
- Gates finales :
  - `pytest -q --maxfail=20` -> `785 passed, 2 skipped`
  - `black app/ server/ tests/ --check` -> vert

## Contexte
- Strategie imposee pendant l'iteration : `domaine d'abord`
- Objectif : rendre les handlers cibles anemiques, deplacer la logique metier dans des services applicatifs dedies, et isoler l'acces DB dans des repositories explicites.
- Aucun changement volontaire de contrat HTTP public, de route, de middleware, de cookie name, ni de shape JSON frontend.

## Bilan de cloture

### Lots clos
1. Lot 1 - `exercise` generation et persistance
2. Lot 2 - `exercise` soumission de reponse et effets metier
3. Lot 3 - `exercise` lecture, query params, interleaved, stats et SSE boundary
4. Lot 4 - `auth` session boundary
5. Lot 5 - `auth` recovery boundary
6. Lot 6 - `user` handler slimming

### Micro-lots de fermeture / durcissement
- `1.1`, `1.2`
- `2.1`, `2.2`
- `3.1`, `3.2`
- `5.1`, `5.2`, `5.2-fix`
- `6.1`

## Resultat architectural
- `exercise` : generation, submit, query et SSE prep mieux separes
- `auth` : boundaries session et recovery mieux separees, revocation post-reset password active
- `user` : `user_handlers.py` aminci, facade `user_application_service.py`, export RGPD recable et teste

## Documents de lot
1. [`PILOTAGE_CURSOR_BACKEND_LOT1_EXERCISE_GENERATION_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT1_EXERCISE_GENERATION_2026-03-08.md)
2. [`PILOTAGE_CURSOR_BACKEND_LOT2_EXERCISE_ATTEMPT_ORCHESTRATION_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT2_EXERCISE_ATTEMPT_ORCHESTRATION_2026-03-08.md)
3. [`PILOTAGE_CURSOR_BACKEND_LOT3_EXERCISE_QUERY_AND_STREAM_BOUNDARY_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT3_EXERCISE_QUERY_AND_STREAM_BOUNDARY_2026-03-08.md)
4. [`PILOTAGE_CURSOR_BACKEND_LOT4_AUTH_SESSION_BOUNDARY_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT4_AUTH_SESSION_BOUNDARY_2026-03-08.md)
5. [`PILOTAGE_CURSOR_BACKEND_LOT5_AUTH_RECOVERY_AND_VERIFICATION_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT5_AUTH_RECOVERY_AND_VERIFICATION_2026-03-08.md)
6. [`PILOTAGE_CURSOR_BACKEND_LOT6_USER_HANDLER_SLIMMING_2026-03-08.md`](./PILOTAGE_CURSOR_BACKEND_LOT6_USER_HANDLER_SLIMMING_2026-03-08.md)

## References
- [`../../CHANGELOG.md`](../../CHANGELOG.md)
- [`VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md`](./VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md)
- [`BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md`](./BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md)

## Reste hors scope
- Cette iteration ne couvre pas `admin`, `badge`, `challenge`, `recommendation`.
- Le prochain controle backend devra ouvrir un nouveau document maitre.
