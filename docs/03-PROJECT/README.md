# Project Governance - Mathakine

> Project master index
> Updated: 15/03/2026

## Read First

| Document | Role |
|---|---|
| [../../CHANGELOG.md](../../CHANGELOG.md) | product release and versioning |
| [../../README_TECH.md](../../README_TECH.md) | living technical reference |
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | recap of `Runtime Truth` and `Contracts / Hardening` |
| [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) | active recap of `Production Hardening` |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | quality-first backend protocol |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD, coverage and typing gates |

## Verified Project State

- `exercise/auth/user`: closed
- `challenge/admin/badge`: closed
- `Runtime Truth`: closed
- `Contracts / Hardening`: closed
- `Production Hardening`: closed

Local reference baseline:
- full suite excluding the false gate: `868 passed, 2 skipped`
- `black app/ server/ tests/ --check`: green
- `isort app/ server/ --check-only --diff`: green
- backend coverage gate in CI: `63 %`

## Active References

| Document | Role |
|---|---|
| [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](./BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) | closed recap of `exercise/auth/user` |
| [BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](./BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) | closed recap of `challenge/admin/badge` |
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | active recap for `Runtime Truth` and `Contracts / Hardening` |
| [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) | active recap for `Production Hardening` |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | validation protocol |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD truth |

## Active Notes By Theme

| Document | Role |
|---|---|
| [ENDPOINTS_NON_INTEGRES.md](./ENDPOINTS_NON_INTEGRES.md) | remaining endpoint/product gaps still worth tracking |
| [IMPLEMENTATION_F07_TIMELINE.md](./IMPLEMENTATION_F07_TIMELINE.md) | timeline implementation note |
| [IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) | interleaved session note |
| [IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) | DB log redaction traceability |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md) | PII / log policy |
| [REFACTOR_DASHBOARD_2026-03.md](./REFACTOR_DASHBOARD_2026-03.md) | dashboard refactor note |

## Remaining Follow-Ups Outside Closed Iterations

- global strict mypy remains out of scope
- coverage above `63 %` still needs dedicated test lots
- dense historical services remain to be decomposed incrementally
- `enhanced_server_adapter.py` and `db_session()` legacy compatibility still exist
- `app/utils/rate_limiter.py` remains outside the distributed Redis scope closed in C2

## Archived Historical Notes

Closed lot notes and superseded deltas were moved out of the active root:
- [archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md](./archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md)

## Archives

- [archives/README.md](./archives/README.md)
- [archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](./archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md](./archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md)
- [archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md](./archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md)
- [archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md](./archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md)
- [AUDITS_ET_RAPPORTS_ARCHIVES/README.md](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
