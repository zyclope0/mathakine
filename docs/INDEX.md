# Documentation Mathakine

> Point d'entree unique - Mise a jour au 11/03/2026 (iterations backend `exercise/auth/user` et `challenge/admin/badge` cloturees, release `3.1.0-alpha.8`)

---

## Demarrage rapide

1. [README racine](../README.md) - vue d'ensemble et installation
2. [README_TECH](../README_TECH.md) - reference technique vivante
3. [GETTING_STARTED](00-REFERENCE/GETTING_STARTED.md) - installation pas a pas

## References principales

| Besoin | Document |
|--------|----------|
| Architecture globale | [00-REFERENCE/ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md) |
| API active | [02-FEATURES/API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) |
| Flux auth | [02-FEATURES/AUTH_FLOW.md](02-FEATURES/AUTH_FLOW.md) |
| Roadmap metier | [02-FEATURES/ROADMAP_FONCTIONNALITES.md](02-FEATURES/ROADMAP_FONCTIONNALITES.md) |
| Gestion projet | [03-PROJECT/README.md](03-PROJECT/README.md) |
| Changelog produit | [../CHANGELOG.md](../CHANGELOG.md) |

## Iterations backend cloturees

| Iteration | Bilan | Delta |
|-----------|-------|-------|
| `exercise/auth/user` | [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) | [DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md](03-PROJECT/DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md) |
| `challenge/admin/badge` | [BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) | [DELTA_RESTANT_POST_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](03-PROJECT/DELTA_RESTANT_POST_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) |

## Archives

- [03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
- [03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md)

## Vigilance

- `tests/api/test_admin_auth_stability.py` ne doit pas etre utilise comme gate standard tant qu'il lance `pytest` dans `pytest` avec couverture.
- La verite terrain reste le code active dans `server/` et `app/`, pas les anciens pilotages archives.
