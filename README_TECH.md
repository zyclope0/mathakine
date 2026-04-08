# Technical README - Mathakine

> Updated: 08/04/2026 (FFI-L19A–C : validate-token 90/min IP, Next `validateTokenRuntime`, `RATE_LIMIT_TRUST_X_FORWARDED_FOR`)

Visible product train:

- `3.6.0-alpha.1`
- source of truth: `CHANGELOG.md` + `frontend/package.json`
- `pyproject.toml` now carries the equivalent PEP 440 package metadata version: `3.6.0a1`

## Runtime Truth

- **Dev** : `python enhanced_server.py` écoute par défaut sur le port **`10000`** (`PORT` dans `.env`). Le frontend attend la même URL (`NEXT_PUBLIC_API_BASE_URL`, `frontend/lib/api/client.ts`).
- live backend runtime is the Starlette stack under `server/`
- active route truth is `server/routes/`
- active HTTP behavior is implemented by `server/handlers/` delegating to `app/services/`
- runtime/data boundary: `app.core.db_boundary` (run_db_bound, sync_db_session) — services import sync_db_session via db_boundary (G4); data access is selective (2 repositories) and direct ORM in many services — see `docs/00-REFERENCE/ARCHITECTURE.md` § Data-Layer Doctrine
- `app/api/endpoints/*` is archived and not part of the active runtime

## Frontend Architecture Truth

- active execution source of truth for frontend industrialization:
  - `.claude/session-plan.md`
  - `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
  - `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` remains historical context only
- `FFI-L10` is now closed:
  - `frontend/components/challenges/ChallengeSolver.tsx` is reduced to a thin orchestrator
  - runtime logic lives in `frontend/hooks/useChallengeSolverController.ts`
  - answer rendering lives in `frontend/components/challenges/ChallengeSolverCommandBar.tsx`
  - pure solver derivation lives in `frontend/lib/challenges/challengeSolver.ts`
- `FFI-L11` is now closed:
  - `frontend/app/profile/page.tsx` is reduced to a thin orchestrator
  - runtime profile state lives in `frontend/hooks/useProfilePageController.ts`
  - pure profile helpers live in `frontend/lib/profile/profilePage.ts`
  - profile sections live in `frontend/components/profile/`
- `FFI-L12` is now closed:
  - `frontend/app/badges/page.tsx` is reduced to a thin badges container
  - runtime badges page state lives in `frontend/hooks/useBadgesPageController.ts`
  - pure badges page helpers live in `frontend/lib/badges/badgesPage.ts`
  - badges sections live in `frontend/components/badges/`
- `FFI-L13` is now closed:
  - `frontend/app/settings/page.tsx` is reduced to a thin settings container (~133 LOC)
  - runtime settings page state lives in `frontend/hooks/useSettingsPageController.ts` (including derived `visibleSessions` for progressive session disclosure)
  - pure settings helpers live in `frontend/lib/settings/settingsPage.ts`
  - settings sections live in `frontend/components/settings/`
- `FFI-L14` is now closed **for frontend architecture** (not a claim of final product truth on admin exercise difficulty):
  - `frontend/app/admin/content/page.tsx` is a thin shell (~50 LOC) with `useAdminContentPageController` and `lib/admin/content/adminContentPage.ts`
  - domains live in `frontend/components/admin/content/*` (tabs, exercises, challenges, badges)
  - admin exercise list difficulty uses **transitional** neutral labels (`Niveau 1..5` from legacy `difficulty`, `Palier n` when `difficulty_tier` is present on the list payload); Star Wars wording is not promoted as visible product vocabulary
  - **Known contract/product gap**: final alignment on F42 `difficulty_tier` for the admin exercise list depends on the admin list API exposing that field reliably; exercise edit/create modals still use legacy `ADMIN_DIFFICULTIES` strings for API compatibility
- `FFI-L15` is now closed:
  - `frontend/hooks/useContentListPageController.ts` centralizes shared list runtime state for exercises/challenges
  - `frontend/components/shared/ContentListResultsHeader.tsx` and `ContentListResultsSection.tsx` centralize the shared results shell
  - `frontend/components/shared/ContentListProgressiveFilterToolbar.tsx` is now a stable facade split into smaller subcomponents
  - exercises/challenges keep domain-specific generators, cards, modals, and route behavior
- `FFI-L16` is now closed (frontend architecture):
  - `frontend/components/layout/Header.tsx` is a thin shell facade orchestrating `HeaderDesktopNav`, `HeaderUserMenu`, and `HeaderMobileMenu`
  - global floating chatbot ownership lives under `frontend/components/chat/` (`ChatbotFloating.tsx`, `ChatbotFloatingGlobal.tsx`)
  - **guest (public)**: assistant remains available; **no** header Assistant CTA; entry via the **global FAB**; **5 messages per browser session** enforced client-side via `useGuestChatAccess` (sessionStorage), complementary to existing **server-side** chat rate limiting (authoritative)
  - **authenticated**: unchanged; header Assistant CTA remains
  - explicit follow-up (not required to close FFI-L16): optional future server-aligned guest quota (cookie / IP / dedicated key)
- `FFI-L17A` is now closed (structural guardrails only, no UI/behavior change):
  - `frontend/lib/architecture/frontendGuardrails.ts` is the single source of truth for LOC budgets on FFI-L11–L16 thin pages/shells/shared facades/chat shells, named dense exceptions, and required seam files
  - `frontend/__tests__/unit/architecture/frontendGuardrails.test.ts` enforces existence, budgets, and `ChatbotFloatingGlobal` staying under `components/chat/` (not `components/home/` or `components/layout/`)
  - run `npm run architecture:check` from `frontend/` to execute that test alone
  - explicit non-goal in FFI-L17: splitting `ProfileLearningPreferencesSection` or `ChallengeSolverCommandBar` (deferred to **FFI-L18**)
- `FFI-L17B` is now closed (governance only, same module as L17A, no UI/behavior change):
  - `OWNERSHIP_RULE_GROUPS` documents active ownership conventions (constants/helpers, runtime vs view, facades, admin/content-list, pointer to FFI-L18) — mirrored in `docs/04-FRONTEND/ARCHITECTURE.md`
  - `REQUIRED_CANONICAL_LIB_FILES` + `collectMissingCanonicalLibFiles` guard shared `lib/` anchors (HTTP client, roles, domain constants, FFI-L11–L16 page helpers, content-list, header navigation)
  - forbidden duplicate global chatbot mounts: `FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS` (home + layout)
- `FFI-L18A` is now closed (profile learning preferences): thin `ProfileLearningPreferencesSection` facade + `ProfileLearningPreferences*` subcomponents + `lib/profile/profileLearningPreferences.ts` ; no intentional UX change
- `FFI-L18B` is now closed (challenge solver command bar): thin `ChallengeSolverCommandBar` facade + `ChallengeSolverMcqGrid` / `ChallengeSolverVisualButtons` / order & grid blocks / `ChallengeSolverValidateActions` + `lib/challenges/challengeSolverCommandBar.ts` ; `ALLOWED_DENSE_EXCEPTIONS` is empty ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` for the command bar facade
- `FFI-L20A` is now closed (dashboard shell): `frontend/app/dashboard/page.tsx` is a thin container (~174 LOC) ; runtime lives in `frontend/hooks/useDashboardPageController.ts` ; tabs are split into `frontend/components/dashboard/Dashboard*Section.tsx` + `DashboardTabsNav.tsx` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES`
- `FFI-L20B` is now closed (exercise solver): `frontend/components/exercises/ExerciseSolver.tsx` is a thin facade (~366 LOC) ; runtime lives in `frontend/hooks/useExerciseSolverController.ts` ; pure flow helpers in `frontend/lib/exercises/exerciseSolverFlow.ts` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` + required seams/canonical lib entries
- `FFI-L20C` is now closed (auth + root providers): shared contracts in `frontend/lib/auth/types.ts` ; pure branches in `frontend/lib/auth/authLoginFlow.ts` ; post-login override seam in `frontend/lib/auth/postLoginRedirect.ts` ; `hooks/useAuth.ts` remains the public hook facade ; `components/providers/Providers.tsx` composes `ThemeBootstrap` + `AccessibilityDomSync` + `AccessibilityHotkeys` + existing `AuthSyncProvider` / `AccessScopeSync` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` + required seams/canonical lib entries
- `FFI-L20D` is now closed (badges presentation domain): shared contracts in `frontend/lib/badges/types.ts` ; pure presentation helpers in `frontend/lib/badges/badgePresentation.ts` (medal paths, difficulty/glow, grid sort, locked motivation branches) consumed by `BadgeCard`, `BadgeGrid`, `BadgesProgressTabsSection` ; characterization tests + `PROTECTED_FRONTEND_SURFACES` budgets + `REQUIRED_CANONICAL_LIB_FILES` entries ; no intentional UX change
- next frontend architecture focus: remaining dense secondary views (e.g. `SettingsSecuritySection`, admin read-heavy shells per audit) and polish tracks — no open FFI-L20\* seam

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
- **FFI-L19C — client IP for rate-limit keys** (`app/utils/rate_limit.py`): `RATE_LIMIT_TRUST_X_FORWARDED_FOR` (default **false**, conservative). If **true**, first non-empty hop of `X-Forwarded-For` when present; else `request.client.host`. If **false**, **never** trust `X-Forwarded-For` (TCP peer only). Enable `true` only behind a trusted proxy that rewrites/appends XFF. See `.env.example` and [RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md](docs/03-PROJECT/RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md) §17.

#### Diagnostics `validate-token` (rafales 429 / attribution)

- **`POST /api/auth/validate-token`** : décorateur `rate_limit_validate_token`, plafond **`RATE_LIMIT_VALIDATE_TOKEN_MAX` (90/min par IP)**, clé `rate_limit:validate-token:{ip}`. **Login / forgot-password** : `rate_limit_auth`, **`RATE_LIMIT_AUTH_SENSITIVE_MAX` (5/min)**, inchangé.
- Sur **429**, les logs **WARNING** incluent le **bucket** (`validate_token` vs `auth_sensitive`), l’**endpoint** (pour `auth_sensitive`), l’**IP** effective, **User-Agent** et **Referer** tronqués, début de **X-Forwarded-For** brut, et **`X-Mathakine-Validate-Caller`** si présent (Next : `routeSession` / `syncCookie` via `buildValidateTokenRequestHeaders` — indication seulement, falsifiable).
- Sur **succès** de `validate-token`, une ligne **INFO** `auth.validate_token: ok` reprend les mêmes indices (aucun token ni en-tête `Authorization` dans les logs).
- **FFI-L19B** : `routeSession` et `sync-cookie` passent par `frontend/lib/auth/server/validateTokenRuntime.ts` — une seule requête HTTP concurrente par `(baseUrl, token)` ; réutilisation d’un **succès** backend pendant **2,5 s** seulement (pas de cache des 401 / erreurs).
- Référence : [RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md](docs/03-PROJECT/RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md) (§15–§17). **FFI-L19\*** **clos** ; priorité active : roadmap **frontend** principale (voir `.claude/session-plan.md`).

**Rollback après diagnostic**

1. **Complet** : revert du commit qui touche `app/utils/rate_limit.py` (dont `rate_limit_validate_token` / constantes), `server/handlers/auth_handlers.py`, `frontend/lib/auth/server/validateTokenBackendHeaders.ts`, `frontend/lib/auth/server/validateTokenRuntime.ts`, les appels dans `routeSession` / `sync-cookie`, `README_TECH.md`, et les tests associés ; redéployer.
2. **Ciblé** : retirer uniquement le `logger.info` dans `api_validate_token` si le volume INFO gêne ; garder le WARNING enrichi sur 429 pour les autres endpoints auth.
3. **Sans redéployer le frontend** : le backend ignore l’absence du header ; seule l’attribution `validate_caller` redevient `-` dans les logs.

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
