# Admin section implementation — Contexte projet réel

_Exported on 22/02/2026 — Document mis à jour pour refaire le contexte du projet réel (structure code, état technique)._

---

## PARTIE 1 — CONTEXTE PROJET RÉEL

### Vue d'ensemble

**Mathakine** : plateforme éducative mathématique gamifiée (Next.js + Starlette + PostgreSQL + OpenAI). Production sur Render.

### Structure du code (réelle)

```
mathakine/
├── enhanced_server.py       # Point d'entrée backend (Starlette)
├── app/                     # Logique métier (indépendant HTTP)
│   ├── core/                # config, security, logging_config, monitoring, ai_config
│   ├── db/                  # base, init_db, queries, adapter, transaction
│   ├── models/              # SQLAlchemy (all_models, legacy_tables, etc.)
│   ├── services/            # badge_service, badge_requirement_engine, exercise_service...
│   └── utils/               # rate_limit.py, rate_limiter.py, request_utils
├── server/                  # Couche HTTP
│   ├── handlers/            # auth, user, exercise, challenge, admin...
│   ├── middleware.py       # RequestIdMiddleware, CORS, auth deny-by-default
│   ├── auth.py              # get_current_user, require_auth
│   └── routes.py            # Définition des routes API
├── frontend/                # Next.js App Router
├── tests/                   # pytest backend + Vitest frontend
├── migrations/              # Alembic (versions/)
└── docs/                    # docs/INDEX.md = point d'entrée
```

### Fichiers clés

| Rôle | Fichier |
|------|---------|
| Démarrer le serveur | `python enhanced_server.py` |
| Migrations | `alembic upgrade head` |
| Routes API | `server/routes.py` |
| Auth JWT | `server/auth.py`, `app/core/security.py` |
| CI/CD | `.github/workflows/tests.yml` |

### Documentation de référence

Voir `docs/INDEX.md` pour la navigation complète.

---

_Fin du document — Dernière mise à jour : 25/02/2026_
