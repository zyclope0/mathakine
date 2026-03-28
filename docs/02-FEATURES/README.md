# Features Docs - Scope and Truth

> Folder status index for `docs/02-FEATURES`
> Updated: 2026-03-28
> Truth review: F42 difficulty/ranks docs plus feature-note rationalization realigned with code and project archives on 2026-03-28

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
- new temporary pilotage notes should not land in this folder; they belong in `docs/03-PROJECT/` and should be archived once closed

## Document Map

| Document | Role | Status | Notes |
|---|---|---|---|
| [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) | Backlog source of truth | Active | Priorities, implemented history, open follow-ups |
| [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) | Active runtime/API reference | Active / truth-reviewed | Mirrors current routes at a high level; runtime notes refreshed 2026-03-23 |
| [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md) | Produit simple: difficulté pédagogique vs rangs publics | Active reference | Version lisible équipe/produit ; le manifeste technique reste dans `00-REFERENCE/` |
| [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md) | Gamification account + ledger reference | Active | Account-level points, 8-bucket public rank computation, ledger writes and read surfaces |
| [CHALLENGE_CONTRACT_IA9.md](CHALLENGE_CONTRACT_IA9.md) | Contrat défis : `response_mode`, `choices`, symétrie | Active | Lot IA9 ; code source `challenge_contract_policy.py` |
| [AUTH_FLOW.md](AUTH_FLOW.md) | Auth reference | Active | Runtime auth flow reference |
| [RECOMMENDATIONS_ALGORITHM.md](RECOMMENDATIONS_ALGORITHM.md) | Algorithme reco exercices + défis | Active | Pré-filtre tier exercices vs score penalty défis — asymétrie documentée |
| [AI_EVAL_HARNESS.md](AI_EVAL_HARNESS.md) | Runbook harness évaluation IA (IA7/IA8) | Active | `app/evaluation/` — modes offline/live/persist, corpus, limites |
| [OPENAI_CIRCUIT_BREAKER.md](OPENAI_CIRCUIT_BREAKER.md) | Circuit breaker OpenAI | Active | `app/utils/circuit_breaker.py` — états CLOSED/OPEN/HALF_OPEN, seuils, exceptions comptées |
| [ANALYTICS_SERVICE.md](ANALYTICS_SERVICE.md) | Service analytics EdTech | Active | `app/services/analytics/` — événements quick_start_click / first_attempt, agrégats admin |
| [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md) | Implemented feature note | Active reference | Daily challenges are implemented |
| [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md) | Implemented feature note | Active reference | Diagnostic is implemented; remaining gaps should also appear in roadmap/backlog |
| [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md) | Implemented feature note | Active reference | Post-F42 runtime truth for adaptive difficulty and legacy compatibility |
| [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md) | Implemented admin analytics note | Active reference | Quick Start analytics instrumentation is implemented |
| [F04_REVISIONS_ESPACEES.md](F04_REVISIONS_ESPACEES.md) | Future feature spec | Active backlog spec | Not implemented |
| ~~NIVEAUX_DIFFICULTE_NORMALISATION.md~~ | Compatibility note | **Archivé** 2026-03-27 | Contenu couvert par DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md + DIFFICULTY_AND_RANKS_MANIFEST.md |
| [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) | Admin security constraints | Active reference | Use before extending admin endpoints |
| [THEMES.md](THEMES.md) | Frontend/theme reference | Reference | Keep as supporting design/system note |
| [I18N.md](I18N.md) | Internationalization reference | Reference | System-level reference; includes `LocaleInitializer` runtime/lang sync note and test coverage |
| [../assets/prototypes/F34_SCIENCES_PROTOTYPE.html](../assets/prototypes/F34_SCIENCES_PROTOTYPE.html) | Prototype asset | Prototype | Not implemented; kept outside the feature corpus because it is a static HTML prototype only |

## Rationalized Usage

### Use first

- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md)
- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)
- [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)
- [AUTH_FLOW.md](AUTH_FLOW.md)
- feature notes already marked implemented when working on the same area

### Historical references

- [../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/README.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/README.md)

Historical feature notes that were previously treated as active references should now be read from the project archives only. Their useful backlog or runtime claims were either absorbed into `ROADMAP_FONCTIONNALITES.md` or replaced by active references.

## Current Rationalization Decisions

1. Already implemented features are not removed from this folder if they still provide useful implementation context.
2. Historical ideation is not deleted, but must be explicitly marked as historical or partially superseded.
3. New backlog items must land in [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md), not in scattered standalone notes only.
4. If a future refactor needs a dedicated spec, that spec must link back to the roadmap item that owns the priority.

## Rationalization Applied on 2026-03-28

The following notes are no longer considered first-class active feature docs:

- `ADMIN_ESPACE_PROPOSITION.md`
- `BADGES_AMELIORATIONS.md`
- `ANALYTICS_PROGRESSION.md`
- `WORKFLOW_EDUCATION_REFACTORING.md`
- `ROADMAP_MVP_CHALLENGE_2026-03.md`

Their useful truths now belong in:

- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) for backlog ownership and feature status
- active runtime/API docs in this folder when a behavior is already shipped
- project archives for historical rationale and older product framing



## Roadmap Maintenance Ritual

After each product lot that changes a feature state:
- update the corresponding roadmap row status (`[DONE]`, `[PARTIAL]`, `[BACKLOG]`)
- keep shipped items visible in roadmap history instead of removing them
- if only technical foundations shipped, add or update the item in section `8.2`
- if a dedicated feature note changed truth status, update that note in the same lot

The roadmap stays motivational only if shipped work remains visible and stale backlog rows are corrected quickly.
