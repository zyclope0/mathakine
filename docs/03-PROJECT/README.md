# Project Governance - Mathakine

> Project master index
> Updated: 24/03/2026

## Read First

| Document | Role |
|---|---|
| [../../CHANGELOG.md](../../CHANGELOG.md) | product release and versioning |
| [../../README_TECH.md](../../README_TECH.md) | living technical reference |
| [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md) | current AI model governance and runtime observability truth |
| [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md) | single active tracker for remaining follow-ups |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | quality-first backend protocol |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD, coverage and typing gates |
| [PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md](./PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md) | AI lot ledger and historical pilotage |

## Verified Project State

- `exercise/auth/user`: closed
- `challenge/admin/badge`: closed
- `Runtime Truth`: closed
- `Contracts / Hardening`: closed
- `Production Hardening`: closed
- `Security, Boundaries, and API Discipline`: closed
- `Typed Contracts, Service Decomposition, and Legacy Retirement`: closed
- `Academic Backend Rigor, Replicability, and Operability`: closed
- `Lots G (Residual Contracts and Cleanup)`: closed (G1-G4)
- `Architecture Clean Cible A + B`: closed (vertical slicing `app/services/`)
- `Backend Maturity Truth, Contract Normalization, and Hotspot Reduction`: closed (`I1`-`I8`)
- `Recommendation remediation`: closed (`R1`-`R7`)
- AI lots consolidated on 22/03/2026: `IA10/IA10b`, `IA11a/IA11b`, `IA12`, `IA13a/IA13b` closed; `IA14` remains in cleanup mode. Source project ledger: [PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md](./PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md)
- `DRY frontend/proxy cleanup`: lots `DRY-1`, `DRY-2`, `DRY-3` closed (shared `backendUrl`, contrat SSE exercices, revue ciblee `exhaustive-deps`)
- `AT technical cleanup`: lots `AT-1`, `AT-2`, `AT-3`, `AT-4` closed on the treated scope (challenge edge cases, pagination/completion perf, aggregate stats, OpenAI circuit breaker, real Next proxy route tests, explicit auth/CSRF request failures)

## Active References

| Document | Role |
|---|---|
| [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md) | active cross-workload AI governance reference |
| [POINTS_RESTANTS_2026-03-15.md](./POINTS_RESTANTS_2026-03-15.md) | remaining points still worth tracking |
| [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md) | closed recommendation iteration R - baseline and reserves |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | validation protocol |
| [PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md](./PILOTAGE_CURSOR_BACKEND_ARCHITECTURE_CLEAN_2026-03-18.md) | architecture clean recap |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD truth |
| [PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md](./PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md) | AI lot ledger and historical sequence |
| [AUDIT_DRY_2026-03-23.md](./AUDIT_DRY_2026-03-23.md) | DRY audit and closure tracker (`DRY-1` -> `DRY-3`) |
| [AUDIT_TECHNIQUE_2026-03-22.md](./AUDIT_TECHNIQUE_2026-03-22.md) | historical technical review snapshot, now reduced to the remaining live backlog after `AT-1` -> `AT-4` |
| [evaluation/AI_GENERATION_HARNESS.md](./evaluation/AI_GENERATION_HARNESS.md) | harness usage and persistence |

## Historical Recaps

| Document | Role |
|---|---|
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | historical recap of `Runtime Truth` and `Contracts / Hardening` |
| [BILAN_PRODUCTION_HARDENING_2026-03-15.md](./BILAN_PRODUCTION_HARDENING_2026-03-15.md) | historical recap of `Production Hardening` |
| [AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md) | historical dashboard refactor note (legacy archive namespace) |
| [AUDIT_IA_LAYER_2026-03-22.md](./AUDIT_IA_LAYER_2026-03-22.md) | historical AI review snapshot - not runtime truth |
| [CODE_REVIEW_2026-03-22.md](./CODE_REVIEW_2026-03-22.md) | historical working-tree review snapshot |
| [AUDIT_TECHNIQUE_2026-03-22.md](./AUDIT_TECHNIQUE_2026-03-22.md) | historical technical review snapshot |

## Active Notes By Theme

| Document | Role |
|---|---|
| [IMPLEMENTATION_F07_TIMELINE.md](./IMPLEMENTATION_F07_TIMELINE.md) | timeline implementation note |
| [IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) | interleaved session note |
| [IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) | DB log redaction traceability |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md) | PII / log policy |

## Maintenance Rule

`POINTS_RESTANTS_2026-03-15.md` is the only active follow-up tracker in this folder.
Closed bilans, temporary delta files, and superseded lot notes belong in `archives/`. `AUDITS_ET_RAPPORTS_ARCHIVES/` is now a legacy compatibility collection only.

## Archives

- [archives/README.md](./archives/README.md)
- [archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](./archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md](./archives/PRODUCTION_HARDENING_DETAIL_2026-03-15/README.md)
- [archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md](./archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md)
- [archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md](./archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md)
- [archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md](./archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md)
- [archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md](./archives/LOTS_G_RESIDUAL_CONTRACTS_AND_CLEANUP_2026-03-18/README.md)
- [archives/ITERATION_I_2026-03-19/README.md](./archives/ITERATION_I_2026-03-19/README.md)
- [archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md](./archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/README.md)
- [archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md](./archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md)
- [AUDITS_ET_RAPPORTS_ARCHIVES/README.md](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md) (legacy compatibility collection)



