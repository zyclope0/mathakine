# Technical README - Mathakine

> Updated: 24/03/2026

Visible product train:
- `3.3.0-alpha.2`
- source of truth: `CHANGELOG.md` + `frontend/package.json`
- `pyproject.toml` now carries the equivalent PEP 440 package metadata version: `3.3.0a2`

## Runtime Truth

- **Dev** : `python enhanced_server.py` écoute par défaut sur le port **`10000`** (`PORT` dans `.env`). Le frontend attend la même URL (`NEXT_PUBLIC_API_BASE_URL`, `frontend/lib/api/client.ts`).
- live backend runtime is the Starlette stack under `server/`
- active route truth is `server/routes/`
- active HTTP behavior is implemented by `server/handlers/` delegating to `app/services/`
- runtime/data boundary: `app.core.db_boundary` (run_db_bound, sync_db_session) — services import sync_db_session via db_boundary (G4); data access is selective (2 repositories) and direct ORM in many services — see `docs/00-REFERENCE/ARCHITECTURE.md` § Data-Layer Doctrine
- `app/api/endpoints/*` is archived and not part of the active runtime

## Current Stability Baseline (post–iteration `I` closure, 2026-03-19)

Jalon historique valide ; le dépôt a depuis accumulé d’autres preuves (dont reco **R** ci-dessous). Chiffres = **citations** de clôture documentée ; **re-lancer** les commandes si l’arbre a divergé.

Gate standard backend (`test_admin_auth_stability.py` exclu — test spécial non-bloquant) :
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `962 passed, 3 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- measured local coverage on `app` + `server`: `67.30 %`
- backend CI coverage gate -> `63 %`

## Recommendation Iteration R Closure (2026-03-21)

Chiffres = **citations** de la clôture R7 (pas de nouvelle exécution imposée pour aligner la doc). **Micro-lot R7b** : mise à jour des README racine uniquement, **sans rerun** ; vérité runtime inchangée.

Moteur reco après **R** : règles heuristiques bornées et chemins testés ; **pas** d’apprentissage ML ni personnalisation « intelligente » au sens data-science.

- Clôture gouvernance + réserves + non-revendications : [docs/03-PROJECT/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](docs/03-PROJECT/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md)
- Reco ciblée : `pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` -> **`40 passed`**
- Gate standard backend (même commande que la section post-I) -> **`991 passed, 2 skipped`**
- Frontend (depuis `frontend/`) : Vitest `useRecommendationsReason` -> **`3 passed`** ; `npm run lint`, `npm run format:check`, `npm run build` -> **green**

## Post-AT Hardening Closure (2026-03-24)

Les micro-lots `AT-1` a `AT-4` ont ferme la plupart des findings encore vivants du snapshot `AUDIT_TECHNIQUE_2026-03-22.md` sur le scope traite.

- `AT-1` : correction des edge cases backend challenges (`auto_correct_challenge`, variable morte, semantique `active_only` unifiee entre liste et comptage).
- `AT-2` : optimisations frontend locales (`useCompletedItems` via `Set.has()`, `usePaginatedContent` calcule `hasMore`, recommandations dashboard bornees a 6 items avec toggle local).
- `AT-3` : `get_challenge_stats` passe en requete agregee atomique ; un circuit breaker OpenAI process-local protege des indisponibilites amont sur les workloads pedagogiques SSE.
- `AT-4` : vraies suites de tests pour les routes proxy Next.js et clarification des erreurs auth/CSRF/backend de generation IA cote frontend.

Limite assumee :
- le circuit breaker OpenAI reste local au process. Il ameliore la resilience par worker, mais ne constitue pas une coordination distribuee multi-instance.

## Active Architecture Notes

### Diagnostic

- the diagnostic flow uses a signed `state_token`
- `/api/diagnostic/question` does not expose `correct_answer`
- trusted answer correction is resolved server-side through an opaque `pending_ref`
- the frontend may receive `correct_answer` only after answer submission for feedback

### Runtime boundaries

- `MATH_TRAINER_DEBUG` defaults to `false`
- external JSON error payloads no longer expose traceback or raw exception details
- `MAX_CONTENT_LENGTH` is enforced before JSON/body parsing on the hardened request paths
- `/api/badges/available` is now explicitly bounded (`default=100`, `max=200`)

### Monitoring

- backend Sentry is initialized from `SENTRY_DSN` (fallback `NEXT_PUBLIC_SENTRY_DSN` kept only for backward compatibility)
- backend sends errors, HTTP traces, SQLAlchemy spans, and HTTP metrics
- backend profiling remains disabled by default (`SENTRY_PROFILES_SAMPLE_RATE=0`)
- frontend Sentry sends errors, traces, and Replay through `/monitoring`
- frontend Replay defaults are `0.1` baseline sessions and `1.0` on error
- Sentry release correlation should use the deployed commit via `SENTRY_RELEASE` / `NEXT_PUBLIC_SENTRY_RELEASE`

### AI runtime hardening

- frontend proxy routes (`/api/chat`, `/api/chat/stream`, `/api/exercises/generate-ai-stream`, `/api/challenges/generate-ai-stream`) sont maintenant couverts par des tests de handlers Next.js au niveau route, pas seulement par des tests de helper
- les flux pedagogiques SSE utilisent un circuit breaker process-local partage pour eviter de relancer indefiniment des appels OpenAI manifestement indisponibles
- les erreurs de generation IA cote frontend distinguent maintenant explicitement :
  - CSRF absent
  - session expiree / non authentifiee (`401`)
  - acces refuse (`403`)
  - erreur backend generique

### Rate limiting

- production source of truth is Redis via `RedisRateLimitStore`
- `REDIS_URL` is mandatory in production
- Redis runtime failures are fail-closed on the protected scope
- challenge stream is now aligned on the same distributed backend limiter

## Architecture Clean (Cible A + B — closed)

- **Cible A** : `app/models/` and `app/schemas/` use explicit per-module imports; `all_models.py` and `all_schemas.py` have been removed (A1–A6).
- **Cible B** : `app/services/` is organised by DDD domains (auth, users, badges, exercises, challenges, progress, admin, analytics, communication, core, diagnostic, feedback, recommendation). No business logic file remains at root. See `docs/00-REFERENCE/ARCHITECTURE.md` § app/services/.

## Iteration E + F + G Outcome

The backend is now materially stronger on:
- bounded typed contracts on auth recovery / verification (E) and auth_service (F1)
- decomposition of challenge_service create flow (E) and badge_requirement_engine volume (F2)
- isolated badge requirement validation (E) and admin badge create flow (F3)
- scoped typing (F4) and runtime/data boundary formalization (F5)
- replicability and operability closure (F6)
- lots G: `authenticate_user_with_session` typed result (G1), success_rate cluster in volume (G2), admin exercise create flow (G3), db_boundary imports (G4)

## Explicit Remaining Debt (post-G)

- remaining tuple-shaped auth/admin paths not yet treated
- other clusters in badge_requirement_engine (consecutive, max_time, etc.) not decomposed
- admin mutation paths: put_challenge, other dense admin-content flows
- global strict mypy remains out of scope
- `app/services/core/enhanced_server_adapter.py` remains legacy compatibility
