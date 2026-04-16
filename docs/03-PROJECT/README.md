# Project Governance - Mathakine

> Project governance and traceability index
> Updated: 16/04/2026

## Purpose

This folder now keeps:

- active governance/runbook documents that are still useful in day-to-day work
- implementation notes that still add concrete traceability
- archive buckets for closed audits, pilotage streams, and superseded notes

It is not the single source of truth for in-flight founder planning: runtime truth stays in the code, feature prioritization in the roadmap, and the current local founder plan lives in `.claude/session-plan.md`.

## Read First

| Document                                                                               | Role                                                 |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| [../../CHANGELOG.md](../../CHANGELOG.md)                                               | product release and versioning                       |
| [../../README_TECH.md](../../README_TECH.md)                                           | living technical reference                           |
| [../../.claude/session-plan.md](../../.claude/session-plan.md)                         | current local founder plan / session intent (not runtime truth by itself) |
| [../02-FEATURES/ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md) | active product backlog and feature status truth      |
| [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)       | active AI governance and runtime observability truth |

## Frontend Source Hierarchy

| Document                                                                                                                                                             | Role                                                                |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [../../.claude/session-plan.md](../../.claude/session-plan.md)                                                                                                       | current founder planning note; use alongside roadmap/audits, not as sole runtime proof |
| [../02-FEATURES/ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md)                                                                               | active product prioritization                                       |
| [AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md](./AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md)                                                                       | active frontend architecture/debt reference                         |
| [AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md)                                                                   | active frontend quality snapshot and targeted follow-up tracker     |
| [archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md](./archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md) | historical audit only; rationale and original findings, not backlog |

Latest active frontend audit checkpoint:

- `2026-04-16` : active frontend quality snapshot remains [AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md) ; `ACTIF-03` is closed, `ACTIF-04` remains the last active frontend quality finding, and `frontend/__tests__/unit/` is intentionally reduced to the architecture guardrail test plus the `_testRequest.ts` helper.

## Active Root Documents

| Document                                                                                               | Role                                                                           |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md)                                                                     | CI/CD, quality gates, deploy and rollback                                      |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | quality-first execution protocol                                               |
| [ANALYSE_DEPENDANCES_ET_OPPORTUNITES_2026-04-13.md](./ANALYSE_DEPENDANCES_ET_OPPORTUNITES_2026-04-13.md) | active dependency-upgrade analysis and opportunity notes                       |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md)                                   | policy for PII/secret log redaction                                            |

## Archive Buckets

| Bucket                                                                                                               | Role                                                                            |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [archives/AUDITS_AND_REVIEWS_2026-03/README.md](./archives/AUDITS_AND_REVIEWS_2026-03/README.md)                     | closed audits and review snapshots                                              |
| [archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/README.md](./archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/README.md)   | closed implementation and validation notes kept for traceability                |
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
