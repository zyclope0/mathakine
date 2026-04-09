# Project Governance - Mathakine

> Project governance and traceability index
> Updated: 09/04/2026

## Purpose

This folder now keeps:

- active governance/runbook documents that are still useful in day-to-day work
- implementation notes that still add concrete traceability
- archive buckets for closed audits, pilotage streams, and superseded notes

It is no longer the place for the single active tracker of ongoing work.

## Read First

| Document                                                                               | Role                                                 |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| [../../CHANGELOG.md](../../CHANGELOG.md)                                               | product release and versioning                       |
| [../../README_TECH.md](../../README_TECH.md)                                           | living technical reference                           |
| [../../.claude/session-plan.md](../../.claude/session-plan.md)                         | active execution tracker for current lots            |
| [../02-FEATURES/ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md) | active product backlog and feature status truth      |
| [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)       | active AI governance and runtime observability truth |

## Frontend Source Hierarchy

| Document                                                                                                    | Role                                                                  |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [../../.claude/session-plan.md](../../.claude/session-plan.md)                                              | active execution order for frontend and cross-cutting lots            |
| [../02-FEATURES/ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md)                    | active product prioritization                                         |
| [AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md](./AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md)            | active frontend architecture/debt reference                           |
| [AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md)              | historical audit only; rationale and original findings, not backlog   |

Latest active frontend audit checkpoint:

- `2026-04-09` : structural sequence `FFI-L1` à `FFI-L18B` considered closed; `FFI-L20A`–`FFI-L20H` closed; targeted follow-ups **CHAT-AUTH-01**, **RQ-PROVIDERS-02** and **CHAT-I18N-03** are closed; next targeted lot in `session-plan.md` : **CHAT-LOG-04**.

## Active Root Documents

| Document                                                                                               | Role                                                                          |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md)                                                                     | CI/CD, quality gates, deploy and rollback                                     |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | quality-first execution protocol                                              |
| [IMPLEMENTATION_F07_TIMELINE.md](./IMPLEMENTATION_F07_TIMELINE.md)                                     | implementation note for timeline progress                                     |
| [IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md)                 | implementation note for interleaved sessions                                  |
| [IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md)                   | implementation note for DB log redaction                                      |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md)                                   | policy for PII/secret log redaction                                           |
| [RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md](./RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md)   | 429 `validate-token` : diagnostic + correctif FFI-L19A (quota dédié 90/min IP) |

## Archive Buckets

| Bucket                                                                                                               | Role                                                                            |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [archives/AUDITS_AND_REVIEWS_2026-03/README.md](./archives/AUDITS_AND_REVIEWS_2026-03/README.md)                     | closed audits and review snapshots                                              |
| [archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/README.md](./archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/README.md) | closed pilotage streams and superseded trackers                                 |
| [archives/RECOMMENDATION_ITERATION_R_2026-03/README.md](./archives/RECOMMENDATION_ITERATION_R_2026-03/README.md)     | recommendation iteration R closure corpus                                       |
| [archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/README.md](./archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/README.md)   | former feature notes removed from `docs/02-FEATURES/` after roadmap integration |
| [archives/README.md](./archives/README.md)                                                                           | archive root for older detailed families and legacy collections                 |

## Reading Rules

- current execution tracking lives in [../../.claude/session-plan.md](../../.claude/session-plan.md)
- active product prioritization lives in [../02-FEATURES/ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md)
- runtime truth lives in the code and the active references under `docs/00-REFERENCE/`
- a dated audit, review, pilotage, or closure note is historical by default once its lot is closed
- if a closed note still contains useful rationale, it should live in an archive bucket, not at the root of this folder
