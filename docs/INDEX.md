# Documentation Mathakine

> Documentation entry point
> Updated: 17/03/2026

## Read First

1. [Root README](../README.md)
2. [README_TECH](../README_TECH.md)
3. [Architecture](00-REFERENCE/ARCHITECTURE.md)
4. [API quick reference](02-FEATURES/API_QUICK_REFERENCE.md)
5. [Project index](03-PROJECT/README.md)

## Current Documented State

- visible product release: `3.1.0-alpha.8`
- backend iterations closed:
  - `exercise/auth/user`
  - `challenge/admin/badge`
  - `Runtime Truth`
  - `Contracts / Hardening`
  - `Production Hardening`
  - `Security, Boundaries, and API Discipline`
  - `Typed Contracts, Service Decomposition, and Legacy Retirement`
  - `Academic Backend Rigor, Replicability, and Operability` (F1-F6)
  - `Lots G (Residual Contracts and Cleanup)` (G1-G4)
- local reference baseline (post-F):
  - full suite excluding the false gate: `936 passed, 2 skipped`
  - `black app/ server/ tests/ --check`: green
  - `isort app/ server/ tests/ --check-only --diff`: green
  - `mypy app/ server/ --ignore-missing-imports`: green
  - `flake8 app/ server/ --select=E9,F63,F7,F82`: green
  - measured local coverage on `app` + `server`: `67.30 %`
  - backend coverage gate in CI: `63 %`

## Main References

| Need | Document |
|---|---|
| Setup | [00-REFERENCE/GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) |
| Global architecture | [00-REFERENCE/ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md) |
| Testing guide | [01-GUIDES/TESTING.md](01-GUIDES/TESTING.md) |
| Deployment env | [01-GUIDES/DEPLOYMENT_ENV.md](01-GUIDES/DEPLOYMENT_ENV.md) |
| Sentry monitoring | [01-GUIDES/SENTRY_MONITORING.md](01-GUIDES/SENTRY_MONITORING.md) |
| Troubleshooting | [01-GUIDES/TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) |
| Active API | [02-FEATURES/API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) |
| Auth flow | [02-FEATURES/AUTH_FLOW.md](02-FEATURES/AUTH_FLOW.md) |
| Diagnostic flow | [02-FEATURES/F03_DIAGNOSTIC_INITIAL.md](02-FEATURES/F03_DIAGNOSTIC_INITIAL.md) |
| Project / governance | [03-PROJECT/README.md](03-PROJECT/README.md) |
| Runtime + Contracts recap | [03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) |
| Production Hardening recap | [03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md](03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md) |
| Iteration F archive | [03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md](03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md) |
| Iteration E archive | [03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md](03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md) |
| Security / boundaries archive | [03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md](03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md) |
| Remaining follow-ups | [03-PROJECT/POINTS_RESTANTS_2026-03-15.md](03-PROJECT/POINTS_RESTANTS_2026-03-15.md) |
| Lots G (residual contracts, closed) | [03-PROJECT/archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md](03-PROJECT/archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md) |
| Product changelog | [../CHANGELOG.md](../CHANGELOG.md) |

## Reading Rules

- the live code in `server/` and `app/` is the ultimate truth
- `server/routes/` is the source of truth for active endpoints
- `app/api/endpoints/*` is archived under `_ARCHIVE_2026/` and is not part of the live runtime
- the active diagnostic contract uses a signed `state_token` plus a server-side `pending_ref`
- repeated Windows coverage reruns should isolate `COVERAGE_FILE`

## Archives

- [03-PROJECT/archives/README.md](03-PROJECT/archives/README.md)
- [03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [03-PROJECT/archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md](03-PROJECT/archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md)
- [03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md](03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md)
- [03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md](03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md)
- [03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md](03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md)
- [03-PROJECT/archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md](03-PROJECT/archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md)
- [03-PROJECT/archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md](03-PROJECT/archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md)
- [03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
