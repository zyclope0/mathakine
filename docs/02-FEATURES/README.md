# Features Docs - Scope and Truth

> Folder status index for `docs/02-FEATURES`
> Updated: 2026-03-24
> Truth review: roadmap + workflow + API quick reference + i18n + dashboard widget notes + AI generation client notes realigned with code on 2026-03-24

## Purpose

This folder mixes several kinds of documents:
- active runtime references
- feature backlog/spec documents
- implemented feature notes kept as reference
- historical ideation / analysis documents that are no longer the primary source of truth

This file defines which document should be trusted for what.

## Reading Rules

- live code remains the final truth
- active HTTP/API truth remains `server/routes/` + `server/handlers/`
- cross-workload AI governance truth now lives in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`
- active product backlog truth remains [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- if a document is marked historical, do not use it as sole implementation source
- when a feature is already implemented, prefer the dedicated implementation note or runtime code over older ideation docs

## Document Map

| Document | Role | Status | Notes |
|---|---|---|---|
| [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) | Backlog source of truth | Active | Priorities, implemented history, open follow-ups |
| [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) | Active runtime/API reference | Active / truth-reviewed | Mirrors current routes at a high level; runtime notes refreshed 2026-03-23 |
| [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md) | Gamification account + ledger reference | Active | Account-level points, level computation, ledger writes and read surfaces |
| [CHALLENGE_CONTRACT_IA9.md](CHALLENGE_CONTRACT_IA9.md) | Contrat défis : `response_mode`, `choices`, symétrie | Active | Lot IA9 ; code source `challenge_contract_policy.py` |
| [AUTH_FLOW.md](AUTH_FLOW.md) | Auth reference | Active | Runtime auth flow reference |
| [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md) | Implemented feature note | Active reference | Daily challenges are implemented |
| [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md) | Implemented feature note | Active reference | Diagnostic is implemented; remaining gaps should also appear in roadmap/backlog |
| [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md) | Implemented feature note + follow-ups | Active reference | Includes F05 follow-up backlog |
| [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md) | Implemented admin analytics note | Active reference | Quick Start analytics instrumentation is implemented |
| [F04_REVISIONS_ESPACEES.md](F04_REVISIONS_ESPACEES.md) | Future feature spec | Active backlog spec | Not implemented |
| [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md) | Future feature spec | Active backlog spec | Product wish, not implemented |
| [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) | Admin security constraints | Active reference | Use before extending admin endpoints |
| [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md) | Admin feature proposal | Partial / mixed | Some admin/security foundations exist; this doc is not full runtime truth |
| [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md) | Badge analysis and partial implementation note | Historical + partial reference | Truth-reviewed 2026-03-23; F4.1/F4.2/F4.6 shipped, F4.4/F4.7 partial, remaining backlog stays in roadmap |
| [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md) | Progress analytics ideation | Historical / partially superseded | F07 exists; F12/F16/F37 now carry active backlog relevance |
| [WORKFLOW_EDUCATION_REFACTORING.md](WORKFLOW_EDUCATION_REFACTORING.md) | Product/refactoring context | Historical design reference | Truth-reviewed 2026-03-23; use for rationale, not as runtime or priority truth |
| [THEMES.md](THEMES.md) | Frontend/theme reference | Reference | Keep as supporting design/system note |
| [I18N.md](I18N.md) | Internationalization reference | Reference | System-level reference; includes `LocaleInitializer` runtime/lang sync note and test coverage |
| [../assets/prototypes/F34_SCIENCES_PROTOTYPE.html](../assets/prototypes/F34_SCIENCES_PROTOTYPE.html) | Prototype asset | Prototype | Not implemented; kept outside the feature corpus because it is a static HTML prototype only |

## Rationalized Usage

### Use first

- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)
- [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)
- [AUTH_FLOW.md](AUTH_FLOW.md)
- feature notes already marked implemented when working on the same area

### Use with caution

- [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md)
- [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md)
- [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md)
- [WORKFLOW_EDUCATION_REFACTORING.md](WORKFLOW_EDUCATION_REFACTORING.md)

These are useful for rationale and design intent, but they are not the primary truth for runtime or current backlog ordering.

## Current Rationalization Decisions

1. Already implemented features are not removed from this folder if they still provide useful implementation context.
2. Historical ideation is not deleted, but must be explicitly marked as historical or partially superseded.
3. New backlog items must land in [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md), not in scattered standalone notes only.
4. If a future refactor needs a dedicated spec, that spec must link back to the roadmap item that owns the priority.



## Roadmap Maintenance Ritual

After each product lot that changes a feature state:
- update the corresponding roadmap row status (`[DONE]`, `[PARTIAL]`, `[BACKLOG]`)
- keep shipped items visible in roadmap history instead of removing them
- if only technical foundations shipped, add or update the item in section `8.2`
- if a dedicated feature note changed truth status, update that note in the same lot

The roadmap stays motivational only if shipped work remains visible and stale backlog rows are corrected quickly.
