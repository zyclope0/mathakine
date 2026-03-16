# Project Governance - Mathakine

> Project master index
> Updated: 16/03/2026

## Read First

| Document | Role |
|---|---|
| [../../CHANGELOG.md](../../CHANGELOG.md) | product release and versioning |
| [../../README_TECH.md](../../README_TECH.md) | living technical reference |
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | recap of `Runtime Truth` and `Contracts / Hardening` |
| [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) | active recap of `Production Hardening` |
| [PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md](./PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md) | closed recap of the audit-driven hardening iteration |
| [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md) | single active tracker for remaining follow-ups |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | quality-first backend protocol |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD, coverage and typing gates |

## Verified Project State

- `exercise/auth/user`: closed
- `challenge/admin/badge`: closed
- `Runtime Truth`: closed
- `Contracts / Hardening`: closed
- `Production Hardening`: closed
- `Security, Boundaries, and API Discipline`: closed

Local reference baseline:
- full suite excluding the false gate: `882 passed, 2 skipped`
- `black app/ server/ tests/ --check`: green
- `isort app/ server/ --check-only --diff`: green
- backend coverage gate in CI: `63 %`

## Active References

| Document | Role |
|---|---|
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | recap for `Runtime Truth` and `Contracts / Hardening` |
| [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) | recap for `Production Hardening` |
| [PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md](./PILOTAGE_CURSOR_SECURITY_BOUNDARIES_AND_API_DISCIPLINE_2026-03-15.md) | closed audit-driven hardening recap |
| [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md) | remaining points still worth tracking |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | validation protocol |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD truth |

## Active Notes By Theme

| Document | Role |
|---|---|
| [IMPLEMENTATION_F07_TIMELINE.md](./IMPLEMENTATION_F07_TIMELINE.md) | timeline implementation note |
| [IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) | interleaved session note |
| [IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) | DB log redaction traceability |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md) | PII / log policy |
| [REFACTOR_DASHBOARD_2026-03.md](./REFACTOR_DASHBOARD_2026-03.md) | dashboard refactor note |

## Maintenance Rule

`POINTS_RESTANTS_2026-03-15.md` is the only active follow-up tracker in this folder.
Closed bilans, temporary delta files, and superseded quick-win notes belong in archives.

## Archives

- [archives/README.md](./archives/README.md)
- [archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](./archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md](./archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md)
- [archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md](./archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md)
- [archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md](./archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md)
- [AUDITS_ET_RAPPORTS_ARCHIVES/README.md](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
