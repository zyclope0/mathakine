# Architecture - Mathakine

> Reference architecture globale
> Mise a jour : 13/03/2026

## 1. Vue systeme

Mathakine est structure en trois zones actives:

1. `frontend/` : Next.js 16, React 19, TypeScript, React Query, Zustand
2. `server/` : Starlette, routes, handlers, auth, middleware, SSE
3. `app/` : logique metier, services applicatifs, repositories, generateurs, models, schemas

Flux principal:

```text
Browser -> frontend/ -> server/routes + server/handlers -> app/services -> app/repositories -> PostgreSQL
```

## 2. Principes d'architecture

- handler HTTP mince: parse, validation transport, mapping response
- logique metier et orchestration dans `app/services/`
- acces DB isole dans des services synchrones ou repositories
- contrats HTTP stables: pas de drift volontaire des routes, cookies ou payloads publics
- le code actif prime sur la documentation historique

## 3. Mode d'execution backend reel

Le modele runtime applique sur le scope refactore est:
- handlers HTTP `async`
- services / facades / repositories `sync`
- acces DB sync via `sync_db_session()`
- execution depuis les handlers via `await run_db_bound(...)`
- SSE/LLM conserves en `async`, mais avec sous-appels DB sync isoles

Etat au 13/03/2026:
- l'iteration Runtime est cloturee
- l'iteration Contracts / Hardening est cloturee sur son scope cible
- preuve locale de reference:
  - full suite hors faux gate : `823 passed, 2 skipped`
  - `black --check` vert
  - `isort --check-only --diff` vert

## 4. Couches backend

### `server/`

- `routes/` : source de verite des routes actives
- `handlers/` : couche HTTP
- `auth.py` : auth runtime et decorators
- `middleware.py` : middleware applicatifs
- `app.py` : creation de l'application Starlette via `get_routes()`

### `app/`

- `models/` : ORM SQLAlchemy
- `schemas/` : schemas Pydantic
- `services/` : use cases, facades et logique metier
- `repositories/` : acces data isole sur les zones qui ont deja adopte cette convention
- `generators/` : source de verite backend pour la generation d'exercices
- `db/` : engine, session, transactions, adapter
- `utils/` : helpers transverses

## 5. Domains refactores et stabilises

Clotures:
- `exercise/auth/user`
- `challenge/admin/badge`
- `Runtime Truth`
- `Contracts / Hardening`

Durcissements notables sur le scope ferme:
- contracts challenge types
- boundaries admin/badge explicites
- decomposition ciblee des hotspots badge, admin stats et challenge validator
- corrections SQL ciblees sur `challenge_service.py` et `recommendation_service.py`
- CI coverage gate a `62 %`
- ilots mypy plus stricts sur plusieurs scopes stables

## 6. Legacy et compatibilite

Legacy encore actif:
- `app/services/enhanced_server_adapter.py`
- `app/utils/db_utils.py::db_session()` pour compatibilite legacy

Legacy non monte runtime:
- `app/api/endpoints/`

Compatibilite generateur:
- `server/exercise_generator.py`
- `server/exercise_generator_helpers.py`
- `server/exercise_generator_validators.py`

Ces fichiers servent de re-export. La source de verite reste dans `app/generators/` et `app/utils/`.

## 7. References canoniques

- [README_TECH racine](../../README_TECH.md)
- [docs/INDEX](../INDEX.md)
- [API_QUICK_REFERENCE](../02-FEATURES/API_QUICK_REFERENCE.md)
- [AUTH_FLOW](../02-FEATURES/AUTH_FLOW.md)
- [README projet](../03-PROJECT/README.md)
- [Bilan Runtime + Contracts](../03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
