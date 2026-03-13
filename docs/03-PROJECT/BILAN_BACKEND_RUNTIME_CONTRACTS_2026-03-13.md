# Bilan Backend Runtime + Contracts

> Date: 13/03/2026
> Statut: reference active
> Portee: recapitulatif unique des iterations `Runtime Truth` et `Contracts / Hardening`

## 1. Statut global

| Iteration | Statut | Preuve de cloture |
|---|---|---|
| `exercise/auth/user` | cloturee | bilan et delta 09/03/2026 |
| `challenge/admin/badge` | cloturee | bilan et delta 11/03/2026 |
| `Runtime Truth` | cloturee | full suite hors faux gate verte, `black` vert, `isort` vert |
| `Contracts / Hardening` | cloturee | lots `B1` a `B5` executes et valides |

Baseline locale retenue au 13/03/2026:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py` -> `823 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> vert
- `isort app/ server/ --check-only --diff` -> vert
- CI backend coverage gate -> `--cov-fail-under=62`

## 2. Ce que Runtime a apporte

Decision d architecture fermee:
- handlers HTTP `async`
- services / facades / repositories `sync`
- acces DB sync via `sync_db_session()`
- appels DB depuis les handlers via `await run_db_bound(...)`
- sous-appels DB des flows SSE/LLM isoles en sync

Resultats fermes sur le scope traite:
- fin du faux async sur les verticales refactorees
- plus de DB possedee par les handlers du scope runtime traite
- generation exercice active alignee sur le modele runtime
- facades admin / badge / user / challenge homogenisees en sync
- `settings_reader` et reliquats runtime fermes

## 3. Ce que Contracts a apporte

### B1 - Challenge use cases
- contrats types sur les tentatives challenge
- preparation SSE challenge explicitee
- handlers challenge limites a la couche HTTP

### B2 - Admin / badge contracts
- tuples faibles masques derriere des boundaries explicites
- mapping erreurs admin/badge clarifie
- preuve API completee sur les endpoints admin challenge detail

### B3 - Hotspot decomposition
- `BadgeService` transforme en facade
- decomposition de `badge_award_service.py`
- fallback badge par code passe en dispatch explicite
- `admin_stats_service.py` decoupe par responsabilite
- `challenge_validator.py` clarifie par dispatch, analyzers extraits, famille `PATTERN` / `SEQUENCE` extraite

### B4 - SQL / performance
- suppression du chemin principal `ORDER BY RANDOM()` dans `challenge_service.py`
- suppression de deux hotspots `query-in-loop` dans `recommendation_service.py`
- preservation des contrats publics recommendation / challenge

### B5 - CI / typing
- gate coverage CI explicite a `62 %`
- exclusion formelle du faux gate `tests/api/test_admin_auth_stability.py`
- ilots mypy plus stricts sur:
  - badge
  - auth session / recovery
  - exercise generation / query
  - challenge query / stream

## 4. Ce qui reste hors scope ou a peaufiner

Ce document cloture `Runtime` et `Contracts` sur leur scope cible. Il reste cependant des sujets non bloquants, a traiter seulement via nouveaux lots dedies:

### Legacy / compatibilite
- `app/services/enhanced_server_adapter.py` reste actif sur certains chemins legacy
- `app/utils/db_utils.py::db_session()` reste present pour compatibilite legacy
- `app/api/endpoints/` existe encore physiquement mais n est pas une source de verite runtime

### Typing / CI
- le mypy global du projet reste permissif
- les ilots stricts existent, mais pas encore de durcissement global sur `app/` et `server/`
- le seuil coverage CI est a `62 %`; les seuils `65 %` puis `70 %` demandent encore un chantier tests cible

### Hotspots encore gros
- `app/services/auth_service.py`
- `app/services/user_service.py`
- `app/services/exercise_service.py`
- `app/services/challenge_service.py`
- `app/services/challenge_validator.py`
- `app/services/admin_content_service.py`
- `app/services/badge_requirement_engine.py`

### Performance / donnees
- `challenge_service.py` et `recommendation_service.py` ont eu leurs hotspots principaux traites, mais pas un audit exhaustif
- aucun chantier index / migration SQL n a ete ouvert dans ces iterations

## 5. Source de verite documentaire active

Documents actifs a lire pour la suite:
- `README_TECH.md`
- `docs/INDEX.md`
- `docs/00-REFERENCE/ARCHITECTURE.md`
- `docs/01-GUIDES/TESTING.md`
- `docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`
- ce document

## 6. Archives

Les details lot par lot `Runtime` et `Contracts` ont ete archives ici:
- `docs/03-PROJECT/archives/BACKEND_RUNTIME_CONTRACTS_DETAIL_2026-03-13/`

Ils restent utiles pour l historique, mais ne sont plus la reference active.
