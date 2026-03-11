# Gestion projet Mathakine

> Index maitre - audits, pilotages, bilans et rapports projet
> Derniere mise a jour : 11/03/2026 (iteration backend `challenge/admin/badge` cloturee et archivee, release `3.1.0-alpha.8`)

---

## Documents actifs a lire en premier

| Document | Date | Role |
|----------|------|------|
| [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](./BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) | 09/03/2026 | Bilan final iteration backend `exercise/auth/user` |
| [DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md](./DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md) | 09/03/2026 | Delta post-iteration `exercise/auth/user` |
| [BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](./BILAN_FINAL_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) | 11/03/2026 | Bilan final iteration backend `challenge/admin/badge` |
| [DELTA_RESTANT_POST_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md](./DELTA_RESTANT_POST_ITERATION_BACKEND_CHALLENGE_ADMIN_BADGE_2026-03-11.md) | 11/03/2026 | Delta post-iteration `challenge/admin/badge` |
| [CHANGELOG racine](../../CHANGELOG.md) | vivant | Historique produit, version courante `3.1.0-alpha.8` |

## References projet

| Document | Date | Role |
|----------|------|------|
| [POINT_SITUATION_2026-02-18.md](./POINT_SITUATION_2026-02-18.md) | 18/02/2026 | Point de situation produit |
| [CICD_DEPLOY.md](./CICD_DEPLOY.md) | Fev. 2026 | CI/CD, smoke tests, rollback |
| [POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md) | 22/02/2026 | Regles PII et secrets dans les logs |
| [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md) | 03/2026 | Audit architecture backend de reference |

## Iterations archivees

Les documents de pilotage lot par lot et de versioning interne des iterations cloturees ont ete deplaces dans `AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/`.

| Iteration | Archive |
|-----------|---------|
| `exercise/auth/user` | [RAPPORTS_TEMPORAIRES/INDEX.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md) |
| `challenge/admin/badge` | [RAPPORTS_TEMPORAIRES/INDEX.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md) |

## Signaux utiles

- `tests/api/test_admin_auth_stability.py` est un faux gate tant qu'il lance `pytest` dans `pytest` avec couverture.
- Les reliquats techniques ouverts sont suivis dans les documents `DELTA_*` plutot que dans les pilotages archives.

## Navigation

- [Index documentation](../INDEX.md)
- [Roadmap metier](../02-FEATURES/ROADMAP_FONCTIONNALITES.md)
- [README_TECH racine](../../README_TECH.md)
- [README archives](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
