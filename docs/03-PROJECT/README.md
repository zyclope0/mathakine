# Gestion projet Mathakine

> Index maitre projet
> Mise a jour : 13/03/2026

## A lire en premier

| Document | Role |
|---|---|
| [../../CHANGELOG.md](../../CHANGELOG.md) | release produit et versioning |
| [../../README_TECH.md](../../README_TECH.md) | reference technique vivante |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | protocole quality-first pour les lots backend |
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | recapitulatif actif Runtime + Contracts |

## Etat projet reel

- `exercise/auth/user` : cloture
- `challenge/admin/badge` : cloture
- `Runtime Truth` : cloturee
- `Contracts / Hardening` : cloturee

Baseline locale de reference:
- full suite hors faux gate : `823 passed, 2 skipped`
- `black --check` vert
- `isort --check-only --diff` vert
- coverage CI backend : `62 %`

## References actives

| Document | Role |
|---|---|
| [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](./BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) | bilan iteration `exercise/auth/user` |
| [BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](./BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) | bilan iteration `challenge/admin/badge` |
| [BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](./BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) | recapitulatif actif Runtime + Contracts |
| [CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md](./CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md) | protocole de validation |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | CI/CD, coverage et typing gates |

## Notes actives par theme

| Document | Role |
|---|---|
| [ENDPOINTS_NON_INTEGRES.md](./ENDPOINTS_NON_INTEGRES.md) | endpoints encore non relies ou volontairement hors scope |
| [IMPLEMENTATION_F07_TIMELINE.md](./IMPLEMENTATION_F07_TIMELINE.md) | note d implementation timeline |
| [IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) | note fonctionnelle session entrelacee |
| [IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) | tracabilite redaction logs DB |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md) | politique PII / logs |
| [REFACTOR_DASHBOARD_2026-03.md](./REFACTOR_DASHBOARD_2026-03.md) | note active sur le refactor dashboard |

## Ce qui reste a peaufiner

Le recapitulatif actif liste les sujets hors scope restant a traiter via lots dedies:
- legacy encore actif
- extension du typing strict au-dela des ilots actuels
- hausse du coverage gate au-dela de `62 %`
- gros services encore denses (`auth_service`, `exercise_service`, `challenge_service`, `challenge_validator`, `admin_content_service`, `badge_requirement_engine`)

## Archives

- [archives/README.md](./archives/README.md)
- [archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](./archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md](./archives/HISTORIQUE_PRE_REFACTOR_2026-03-13/README.md)
- [AUDITS_ET_RAPPORTS_ARCHIVES/README.md](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
- [AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md)
