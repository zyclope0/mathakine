# Documentation Mathakine

> Point d'entree documentaire
> Mise a jour : 13/03/2026

## Lire d'abord

1. [README racine](../README.md)
2. [README_TECH](../README_TECH.md)
3. [Architecture](00-REFERENCE/ARCHITECTURE.md)
4. [API active](02-FEATURES/API_QUICK_REFERENCE.md)
5. [Gestion projet](03-PROJECT/README.md)

## Etat documentaire reel

- release produit visible: `3.1.0-alpha.8`
- iterations backend cloturees:
  - `exercise/auth/user`
  - `challenge/admin/badge`
  - `Runtime Truth`
  - `Contracts / Hardening`
- baseline locale de reference:
  - full suite hors faux gate: `823 passed, 2 skipped`
  - `black --check` vert
  - `isort --check-only --diff` vert

## References principales

| Besoin | Document |
|---|---|
| Installation | [00-REFERENCE/GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) |
| Architecture globale | [00-REFERENCE/ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md) |
| Guide tests | [01-GUIDES/TESTING.md](01-GUIDES/TESTING.md) |
| Troubleshooting | [01-GUIDES/TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) |
| API active | [02-FEATURES/API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) |
| Flux auth | [02-FEATURES/AUTH_FLOW.md](02-FEATURES/AUTH_FLOW.md) |
| Projet / pilotage | [03-PROJECT/README.md](03-PROJECT/README.md) |
| Recap Runtime + Contracts | [03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) |
| Changelog produit | [../CHANGELOG.md](../CHANGELOG.md) |

## Iterations backend

| Iteration | Statut | Reference |
|---|---|---|
| `exercise/auth/user` | cloturee | [03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) |
| `challenge/admin/badge` | cloturee | [03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) |
| `Runtime Truth` | cloturee | [03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) |
| `Contracts / Hardening` | cloturee | [03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md](03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md) |

## Regles de lecture

- la verite terrain est le code actif dans `server/` et `app/`
- `server/routes/` est la source de verite des endpoints actifs
- `app/api/endpoints/` n'est pas une source de verite runtime
- les details lot par lot `Runtime` et `Contracts` sont archives; le recapitulatif actif fait foi
- `tests/api/test_admin_auth_stability.py` ne doit pas etre utilise comme gate standard

## Archives

- [03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md](03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/README.md)
- [03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
- [03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md)
