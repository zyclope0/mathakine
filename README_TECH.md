# Technical README - Mathakine

> Updated: 10/04/2026 (lots frontend ciblés fermés jusqu’à QF-07C ; voir puces ci-dessous)

Visible product train:

- `3.6.0-alpha.1`
- source of truth: `CHANGELOG.md` + `frontend/package.json`
- `pyproject.toml` now carries the equivalent PEP 440 package metadata version: `3.6.0a1`

## Runtime Truth

- **Dev** : `python enhanced_server.py` Ã©coute par dÃ©faut sur le port **`10000`** (`PORT` dans `.env`). Le frontend attend la mÃªme URL (`NEXT_PUBLIC_API_BASE_URL`, `frontend/lib/api/client.ts`).
- **Prod Render** : backend dÃ©marrÃ© via **`gunicorn enhanced_server:app`** + **`uvicorn.workers.UvicornWorker`** ; `WEB_CONCURRENCY` pilote le nombre de workers (par dÃ©faut manifest Render : `2`) ; `enhanced_server:app` reste lâ€™entrÃ©e ASGI canonique.
- live backend runtime is the Starlette stack under `server/`
- **OPS-HEALTH-02** : `GET /live` = liveness (JSON `{"status":"live"}`) ; `GET /ready` = readiness (PostgreSQL + Redis when production + `REDIS_URL`) with **2s** bounded checks â†’ `200` / `503` ; `GET /health` aliases readiness ; `render.yaml` `healthCheckPath` = `/ready` (`app/utils/readiness_probe.py`)
- **SEC-HARDEN-01** (backend) : `app/core/logging_config.py` — fichier `uncaught_exceptions.log` avec **`diagnose=False`** en prod-like (évite le dump des variables locales) et **`backtrace=True`** conservé ; `server/middleware.py` — si **`SECURE_HEADERS`**, ajout **`Permissions-Policy: camera=(), microphone=(), geolocation=()`** ; **`Strict-Transport-Security: max-age=31536000; includeSubDomains`** **uniquement** quand **`_is_production()`** (pas en dev/CI). Tests : `tests/unit/test_logging_config_uncaught.py`, `tests/unit/test_secure_headers_middleware.py`, `tests/api/test_base_endpoints.py::test_permissions_policy_header_present`.
- **AUTH-FALLBACK-02** : `recover_refresh_token_from_access_token` — access JWT expiré encore accepté pour récupérer un refresh uniquement dans **`ACCESS_TOKEN_FALLBACK_MAX_AGE_SECONDS`** (**3600** s, avant **7 j**), paramètre **`max_age_seconds`** inchangé pour surcharge ponctuelle ; `recover_refresh_token_fallback` inchangé côté handlers ; tests `tests/unit/test_auth_service.py` (`-k recover_refresh_token_from_access_token`).
- **SEC-PII-LOGS-01** (backend) : `app/services/auth/auth_service.py` — les logs d’auth n’écrivent plus `username` / `email` en clair ; alias stables **`user#` / `email#` + 12 hex** (HMAC-SHA256 tronqué avec **`settings.SECRET_KEY`**, sels de contexte séparés) et **`user_id`** (loguru : placeholders **`{}`**, pas `%s`). JWT / cookies / réponses HTTP inchangés. Tests : `tests/unit/test_auth_service.py` (section SEC-PII-LOGS-01).
- **AUTH-HARDEN-02** : `get_cookie_config()` (`app/core/security.py`) délègue **`_is_production()`** depuis `app/core/config.py` (plus de triplet `os.getenv` dupliqué) ; tuple SameSite/Secure inchangé ; tests `tests/unit/test_security.py`.
- **AUDIT-QUICKWINS-01** : `server/middleware.py` envoie désormais **`X-XSS-Protection: 0`** ; `.dockerignore` garde les versions Alembic dans l’image ; exceptions **`@next/next/no-img-element`** : **`Intentional:`** ou migrées (**PERF-IMG-LOCAL-01** ; **`ACTIF-02-USERAVATAR-01`** / **`ACTIF-02-BADGEICON-01`** — hybride **`next/image`** / **`<img>`** via **`lib/utils/nextImageRemoteSource.ts`** ; **`ACTIF-02-CHATMESSAGES-01`** — **`ChatMessagesView`** : **exception produit** **`<img>`** natif pour URLs SSE / **`blob:`** / **`data:`** et layout intrinsèque, voir composant + **`__tests__/unit/components/chat/ChatMessagesView.test.tsx`**) ; **finding audit ACTIF-02 (D7) fermé**.
- **COMP-BADGECARD-01** (frontend) : `BadgeCard` reste l’entrée publique ; sections extraites dans **`frontend/components/badges/badgeCard/`** (médaille, en-têtes compact/standard, contenu `CardContent`) sans changement de props ni de logique métier.
- **COMP-DIAGNOSTIC-01** (frontend) : **`DiagnosticSolver.tsx`** façade + états par phase + **`DiagnosticSolverPrimitives.tsx`** ; **`useDiagnostic.ts`** inchangé ; tests co-localisés **`components/diagnostic/DiagnosticSolver.test.tsx`** ; **`P3-COMP-01`** fermé (BadgeCard + DiagnosticSolver).
- **TEST-DIAGNOSTIC-HOOK-01** (2026-04-11, closed) : unit tests for **`frontend/hooks/useDiagnostic.ts`** in **`hooks/useDiagnostic.test.ts`** (`api.post` mocked, partial fake timers for the **`session_complete`** / **1800** ms finalize path) ; no product UX change, no hook refactor, no **`vitest.config.ts`** threshold bump ; advances audit **[ACTIF-04]** on this hook only (other critical hooks listed there remain under-covered).
- **TEST-SUBMIT-ANSWER-01** (2026-04-11, closed) : unit tests for **`frontend/hooks/useSubmitAnswer.ts`** in **`hooks/useSubmitAnswer.test.ts`** (`QueryClientProvider`, mocked **`api.post`**, **`sonner`**, **`trackFirstAttempt`**, stable **`useTranslations`**) ; asserts explicit **`refetchQueries`** for **`["completed-exercises"]`** when **`is_correct`** without conflating TanStack Query refetches triggered by **`invalidateQueries`** on unrelated active queries in the test tree ; no **`vitest.config.ts`** threshold bump ; advances **[ACTIF-04]** on this hook only.
- **TEST-COLOCATE-PILOT-01** (2026-04-11, closed) : first **ACTIF-03** pilot — moved **`BadgeCard.test.tsx`**, **`DiagnosticSolver.test.tsx`**, **`useDiagnostic.test.ts`**, **`useSubmitAnswer.test.ts`** from **`__tests__/unit/`** next to their sources ; **`vitest.config.ts`** unchanged ; full repo co-location **not** claimed ; **ACTIF-03** remains open.
- **TEST-IRT-SCORES-01** (2026-04-11, closed) : unit tests for **`frontend/hooks/useIrtScores.ts`** in **`__tests__/unit/hooks/useIrtScores.test.ts`** (`QueryClientProvider`, mocked **`api.get`** on **`/api/diagnostic/status`**, **`useAuth`** via **`vi.hoisted`**) covering direct scores, **`mixte`** / **`fractions`** proxies, profile fallback when **`latest`** is null or type is not IRT-covered, **`has_completed`**, and **`isIrtCovered`** ; no hook refactor, no **`vitest.config.ts`** threshold bump ; advances **[ACTIF-04]** on this hook only.
- **TEST-AI-GENERATOR-01** (2026-04-11, closed) : unit tests for **`frontend/hooks/useAIExerciseGenerator.ts`** in **`__tests__/unit/hooks/useAIExerciseGenerator.test.ts`** (`QueryClientProvider`, partial **`postAiGenerationSse`** mock keeping **`AiGenerationRequestError`** / **`AI_GENERATION_SSE_PATH`**, mocked **`consumeSseJsonEvents`**, real **`dispatchExerciseAiSseEvent`** on the success path, fake timers for the **100 ms** list invalidation) ; **`mockPost.mockReset()`** in **`beforeEach`** to avoid leaking **`mockImplementation`** across cases ; no **`vitest.config.ts`** threshold bump ; advances **[ACTIF-04]** on this hook only.
- **ACTIF-01-TRUTH-01** (2026-04-11, closed) : audit **[ACTIF-01]** closed with per-route proof — **`frontend/app/docs/page.tsx`** is a **Server Component** (`getTranslations` from **`next-intl/server`**, hero animation via Tailwind **`motion-safe:*`** instead of **`useAccessibleAnimation`** on that block only) ; **`frontend/app/changelog/page.tsx`**, **`frontend/app/offline/page.tsx`**, **`frontend/app/contact/page.tsx`** stay **`"use client"`** (**framer-motion** + **`useAccessibleAnimation`**, **`useRouter`** + **`navigator`/`window`**, controlled form + **`window.location.href`** mailto). Details: **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** § ACTIF-01 ; **`.claude/session-plan.md`** § ACTIF-01-TRUTH-01.
- **ACTIF-02-USERAVATAR-01** (2026-04-11, closed) : **`UserAvatar`** — **`resolveNextImageRemoteDelivery`** (**`lib/utils/nextImageRemoteSource.ts`**, aussi exposé via **`userAvatarImageSource.ts`**) ; tests co-localisés **`lib/utils/nextImageRemoteSource.test.ts`** + délégation **`lib/utils/userAvatarImageSource.test.ts`**.
- **ACTIF-02-BADGEICON-01** (2026-04-11, closed) : **`BadgeIcon`** — branche **`icon_url`** : **`next/image`** / **`<img>`** selon le même utilitaire ; erreur de chargement → **`useState`** + emoji ; tests **`__tests__/unit/components/BadgeIcon.test.tsx`**. Audit § ACTIF-02 / D-02 ; **`.claude/session-plan.md`** § ACTIF-02-BADGEICON-01.
- **ACTIF-02-CHATMESSAGES-01** (2026-04-12, closed) : **`ChatMessagesView`** — **pas de `next/image`** : exception **`<img>`** documentée (SSE, schémas **`blob:`** / **`data:`**, **`max-h-64 w-full object-cover`** sans dimensions inventées) ; tests **`__tests__/unit/components/chat/ChatMessagesView.test.tsx`**. **Finding ACTIF-02** clos. Audit § ACTIF-02 / D-02 ; **`.claude/session-plan.md`** § ACTIF-02-CHATMESSAGES-01.
- **ARCH-HOME-LEARNER-01** (frontend) : **`frontend/app/home-learner/page.tsx`** reste la coque route (`ProtectedRoute` seulement) ; le contenu vit dans **`frontend/components/learner/HomeLearnerContent.tsx`** avec sections **`HomeLearnerPageMap`**, **`HomeLearnerReviewsSection`**, **`HomeLearnerActionsSection`**, **`HomeLearnerProgressSection`** (+ **`homeLearnerConstants.ts`**, **`homeLearnerI18n.ts`**) — pas de changement UX ni de logique reco ; premier volet **`P1-ARCH-05`** (home-learner).
- **ARCH-EXERCISES-01** (frontend) : **`frontend/app/exercises/page.tsx`** = coque **`Suspense`** + fallback inchangé ; **`frontend/components/exercises/ExercisesPageContent.tsx`** + **`ExercisesResultsView`** ; helpers **`lib/exercises/buildExercisePageFilters.ts`**, **`exercisePageToolbarLabels.ts`**, **`exercisesPageConstants.ts`** — seams **`useContentListPageController`** / barre filtres / **`ContentListResultsSection`** conservés ; **`P1-ARCH-05`** fermé pour le périmètre home-learner + exercises listés dans l’audit.
- **ARCH-LEADERBOARD-01** (frontend) : **`frontend/app/leaderboard/page.tsx`** = coque **`ProtectedRoute`** + **`LeaderboardPageContent`** ; modules sous **`frontend/components/leaderboard/`** (`LeaderboardList`, `LeaderboardCurrentUserFooter`, `LeaderboardCardState`, rang / points animés / ligne / séparateurs, **`leaderboardPageMotion.ts`**) — hooks **`useLeaderboard`** / **`useMyLeaderboardRank`** inchangés ; **`P1-PERF-01`** (décomposition page) traité sans `useLeaderboardPageController` dédié.
- active route truth is `server/routes/`
- active HTTP behavior is implemented by `server/handlers/` delegating to `app/services/`
- runtime/data boundary: `app.core.db_boundary` (run_db_bound, sync_db_session) â€” services import sync_db_session via db_boundary (G4); data access is selective (2 repositories) and direct ORM in many services â€” see `docs/00-REFERENCE/ARCHITECTURE.md` Â§ Data-Layer Doctrine
- `app/api/endpoints/*` is archived and not part of the active runtime

## Frontend Architecture Truth

- active execution source of truth for frontend industrialization:
  - `.claude/session-plan.md`
  - `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
  - `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` as the active quality snapshot for the post-FFI follow-up train
  - `docs/03-PROJECT/archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` remains historical context only
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
  - **guest (public)**: assistant shell remains discoverable (**global FAB** on most pages, marketing block on home); **no** header Assistant CTA; **sending** requires a session (**CHAT-AUTH-01**): backend JWT + Next proxy gate on cookie `access_token`, with `guestLimitCta` + login/register in the drawer and on the home embedded card; `hooks/chat/useGuestChatAccess.ts` is **no longer wired** to the product chat surfaces (legacy hook + tests retained)
  - **authenticated**: unchanged for connected users (cookies + CSRF on `streamChat`); header Assistant CTA remains
- `FFI-L17A` is now closed (structural guardrails only, no UI/behavior change):
  - `frontend/lib/architecture/frontendGuardrails.ts` is the single source of truth for LOC budgets on FFI-L11â€“L16 thin pages/shells/shared facades/chat shells, named dense exceptions, and required seam files
  - `frontend/__tests__/unit/architecture/frontendGuardrails.test.ts` enforces existence, budgets, and `ChatbotFloatingGlobal` staying under `components/chat/` (not `components/home/` or `components/layout/`)
  - run `npm run architecture:check` from `frontend/` to execute that test alone
  - explicit non-goal in FFI-L17: splitting `ProfileLearningPreferencesSection` or `ChallengeSolverCommandBar` (deferred to **FFI-L18**)
- `FFI-L17B` is now closed (governance only, same module as L17A, no UI/behavior change):
  - `OWNERSHIP_RULE_GROUPS` documents active ownership conventions (constants/helpers, runtime vs view, facades, admin/content-list, pointer to FFI-L18) â€” mirrored in `docs/04-FRONTEND/ARCHITECTURE.md`
  - `REQUIRED_CANONICAL_LIB_FILES` + `collectMissingCanonicalLibFiles` guard shared `lib/` anchors (HTTP client, roles, domain constants, FFI-L11â€“L16 page helpers, content-list, header navigation)
  - forbidden duplicate global chatbot mounts: `FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS` (home + layout)
- `FFI-L18A` is now closed (profile learning preferences): thin `ProfileLearningPreferencesSection` facade + `ProfileLearningPreferences*` subcomponents + `lib/profile/profileLearningPreferences.ts` ; no intentional UX change
- `FFI-L18B` is now closed (challenge solver command bar): thin `ChallengeSolverCommandBar` facade + `ChallengeSolverMcqGrid` / `ChallengeSolverVisualButtons` / order & grid blocks / `ChallengeSolverValidateActions` + `lib/challenges/challengeSolverCommandBar.ts` ; `ALLOWED_DENSE_EXCEPTIONS` is empty ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` for the command bar facade
- `FFI-L20A` is now closed (dashboard shell): `frontend/app/dashboard/page.tsx` is a thin container (~174 LOC) ; runtime lives in `frontend/hooks/useDashboardPageController.ts` ; tabs are split into `frontend/components/dashboard/Dashboard*Section.tsx` + `DashboardTabsNav.tsx` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES`
- `FFI-L20B` is now closed (exercise solver): `frontend/components/exercises/ExerciseSolver.tsx` is a thin facade (~366 LOC) ; runtime lives in `frontend/hooks/useExerciseSolverController.ts` ; pure flow helpers in `frontend/lib/exercises/exerciseSolverFlow.ts` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` + required seams/canonical lib entries
- `FFI-L20C` is now closed (auth + root providers): shared contracts in `frontend/lib/auth/types.ts` ; pure branches in `frontend/lib/auth/authLoginFlow.ts` ; post-login override seam in `frontend/lib/auth/postLoginRedirect.ts` ; `hooks/useAuth.ts` remains the public hook facade ; `components/providers/Providers.tsx` composes `ThemeBootstrap` + `AccessibilityDomSync` + `AccessibilityHotkeys` + existing `AuthSyncProvider` / `AccessScopeSync` ; regrowth guarded via `PROTECTED_FRONTEND_SURFACES` + required seams/canonical lib entries
- **RQ-PROVIDERS-02** (closed): `QueryClient` is created inside `Providers` with `useState(() => new QueryClient({ ... }))` ï¿½ one stable instance per mount, same `defaultOptions` (`staleTime` 60s, `refetchOnWindowFocus: false`, `retry: 1`) ; no module-scope singleton
- **CHAT-I18N-03** (closed): `global-error` uses `createTranslator` + persisted locale (`locale-preferences`) ; `not-found` CTA exercises via `errors.404.ctaExercises` ; chat Next proxies use `apiChat.proxy.*` from `messages/*` with `resolveChatProxyLocale` / `getChatProxyCopy` (`lib/api/chatProxyLocale.ts`) ; `i18n:validate` + `i18n:check` are green for this scope, while repo-wide `i18n:extract` still reports unrelated hardcoded strings outside the lot
- **CHAT-LOG-04** (closed): `app/api/chat/stream/route.ts` uses `lib/utils/logInDevelopment.ts` to gate handled runtime logs to development only ; no production `console.error` noise on handled backend/runtime failures ; SSE fallback payloads unchanged ; dedicated route test covers the production branch
- **LINT-STRICT-05** (closed): `frontend/eslint.config.mjs` sets `@typescript-eslint/no-explicit-any` and `react-hooks/exhaustive-deps` to **error** ; only code change was replacing `Record<string, any>` with `Record<string, unknown>` in `hooks/useDiagnostic.ts` (removed the prior inline disable) ; intentional hook-deps suppressions elsewhere remain documented with `eslint-disable-next-line`
- **SSE-DRY-07** (closed): pedagogical SSE proxies share `frontend/lib/api/sseProxyRequest.ts` plus shared forwarded headers in `frontend/lib/api/proxyForwardHeaders.ts` ; the two Next route handlers are thin facades, missing-auth debug logs are dev-only, and a backend `200` with `body === null` now becomes an explicit SSE error event instead of a silent empty stream
- **CSP-HARDEN-08** (superseded by **QF-07A** + **QF-07B** + **QF-07C**): global `Content-Security-Policy` is built by `frontend/lib/security/buildContentSecurityPolicy.ts` and emitted from **`frontend/proxy.ts`** (Edge middleware), not from `next.config.ts` (only other security headers remain there). **Production** uses per-request **`script-src 'self' 'nonce-*'`** (no `'unsafe-inline'` / no `'unsafe-eval'` in `script-src`). **`QF-07C`**: App Router must render **dynamically** for nonces to apply to framework inline scripts (`self.__next_f.push`, etc.); **`frontend/app/layout.tsx`** exports **`dynamic = "force-dynamic"`**, is **async**, reads **`headers().get(CSP_NONCE_REQUEST_HEADER)`** (`x-nonce`, set by `proxy.ts`), and sets **`nonce`** on **`<html>`** so Next aligns emitted scripts/styles with the CSP. **Trade-off:** essentially no static page optimization for HTML (routes show **Æ’** in `next build` except special static assets like OG images); **higher per-request server work** vs fully static prerender â€” acceptable for correct CSP under strict `script-src`. Middleware still forwards **`Content-Security-Policy`** on the request for Nextâ€™s nonce derivation. **React Query Devtools** remain without `styleNonce`; **`style-src 'unsafe-inline'`** covers their injected styles in dev. **Development** keeps `'unsafe-inline'` and `'unsafe-eval'` in `script-src` for DX. Unit tests: `middleware.test.ts` (CSP + forwarded nonce); `buildContentSecurityPolicy` / `middlewareCsp` helpers covered indirectly via proxy tests.
- **OG-META-09** (closed): default social preview is **1200ï¿½630** from `app/opengraph-image.tsx` and `app/twitter-image.tsx` (`ImageResponse`, shared `lib/social/renderSocialShareImageResponse.tsx`) ; global `metadata.openGraph.images` / `twitter.images` use `lib/social/socialShareImageMeta.ts` (paths `/opengraph-image`, `/twitter-image`) ï¿½ no longer the 512ï¿½512 app icon ; routes run on `runtime = "nodejs"` and load explicit local `KaTeX Main` fonts via `lib/social/socialShareImageFonts.ts` for stable text rendering outside Vercel Edge ; `twitter.card` stays `summary_large_image` ; tests in `__tests__/unit/lib/social/socialShareImageMeta.test.ts` and `__tests__/unit/lib/social/socialShareImageFonts.test.ts`
- **QF-01** (closed): removed `app/test-sentry` (no product test surface) ; `useAuth` sets Sentry user context with **`id` only** (no `username`) ; `frontend/.env.example` documents **`SECRET_KEY`** for Next server JWT/session resolution (`lib/auth/server/routeSession.ts`) ï¿½ not `NEXT_PUBLIC_*` ; see `docs/01-GUIDES/SENTRY_MONITORING.md` for smoke checks without `/test-sentry`
- **QF-02** (closed): dashboard **PDF/Excel** load **`jspdf` / `jspdf-autotable` / `exceljs`** only on export click via `import()` inside `lib/utils/exportPDF.ts` and `exportExcel.ts` (`exportDashboardToPDF` is async) ; `components/dashboard/ExportButton.tsx` unchanged UX, `await` on PDF path ; reduces initial dashboard-related chunk cost
- **QF-03** (closed): route-level **admin** pages (`app/admin/*.tsx` listed in lot) and **`app/offline/page.tsx`** use **`useTranslations`** with copy in **`messages/fr.json`** / **`messages/en.json`** under **`adminPages.*`** (overview, analytics, aiMonitoring, auditLog, config, content, feedback, moderation, users) and root **`offline`** ; `AdminReadHeavyPageShell` / domain hooks unchanged ; deep admin modals and shared hooks (e.g. `useAdminAuditLog` label helper) remain out of scope ; smoke tests under `__tests__/unit/app/admin/adminRoutePagesI18n.smoke.test.tsx` + `__tests__/unit/app/offline/page.test.tsx`
- **QF-03B** (closed): remaining visible i18n debt on the **admin chrome** and **auth toasts** is now aligned: `frontend/app/admin/layout.tsx` uses `adminPages.layout.*` for side navigation labels and `aria-label`, and `frontend/hooks/useAuth.ts` no longer hardcodes the register/forgot-password fallback descriptions (`toasts.auth.registerVerifyEmailDescription`, `forgotPasswordSuccessDescription`, `forgotPasswordErrorDescription`) ; dedicated test `__tests__/unit/app/admin/AdminLayout.test.tsx` + updated `useAuth.test.ts`
- **QF-04** (closed): **`frontend/eslint.config.mjs`** ï¿½ `@typescript-eslint/no-unused-vars` and **`no-require-imports`** set to **error** ; **`consistent-type-imports`** set to **error** with **`disallowTypeAnnotations: false`** (Vitest `import()` type args for mocks) ; autofix applied across API routes, layout components, and hooks (type-only imports split / inlined) ; **`import/no-cycle`** untouched
- **QF-04B** (closed): **type-aware** ESLint on `**/*.{ts,mts,tsx}` via **`parserOptions.projectService: true`** + **`tsconfigRootDir`** (ignores `.next`, `out`, `build`, `coverage`, `scripts`, `node_modules`) ; **`@typescript-eslint/no-floating-promises`** ? **error** ; **64** real violations fixed with explicit **`void`** on intentional fire-and-forget (`invalidateQueries` / `refetchQueries`, dynamic `import()`, async handlers) ï¿½ **no product UX change**
- **QF-04C** (closed): **`react-hooks/set-state-in-effect`** and **`react-hooks/preserve-manual-memoization`** ? **error** ; **`useContentListOrderPreference`** refactored to **lazy `useState`** hydration (removed effect + disable) ; **one** documented **`eslint-disable-next-line`** kept in **`useGuestChatAccess`** for intentional post-hydration guest quota sync ï¿½ **no product UX change**
- **QF-05** (closed): Playwright **authenticated learner path** on **Chromium only** (skip other browsers) using seed demo credentials from **`lib/constants/demoLogin`** ; helper **`__tests__/e2e/helpers/demoUserAuth.ts`** (`loginAsDemoUser`, `completeOnboardingIfNeeded`, `authenticateDemoUserForProtectedPages`) ï¿½ **no** `globalSetup`, **no** shared `storageState` ; **`auth` / `dashboard` / `badges` / `settings`** specs assert real **`h1` / UI chrome** after login ; onboarding minimal then **skip diagnostic** via direct navigation ; **requires** backend reachable for login (default API `http://localhost:10000`) ; login rate limit **5/min/IP** ï¿½ keep **`workers: 1`** for serial E2E
- **QF-06** (closed): **coverage gates** added to **`frontend/vitest.config.ts`** from the measured frontend baseline with an explicit **`coverage.include`** perimeter (`root ts/tsx`, `app`, `components`, `hooks`, `i18n`, `lib`, `messages`) ; global thresholds fixed at conservative floors **statements 43 / branches 36 / functions 39 / lines 44** from the first full run on that perimeter (`3590/8291`, `3111/8420`, `899/2264`, `3423/7718`) ; goal is to freeze todayï¿½s real denominator, not impose an arbitrary target ; `npm run test:coverage`, `npm run lint`, and `npx tsc --noEmit` remain green
- **E2E-CORE-06** (minimal, closed): Playwright sur `frontend/__tests__/e2e/` (`auth.spec.ts`, `exercises.spec.ts`, `dashboard.spec.ts`, `badges.spec.ts`, `settings.spec.ts`, `admin.spec.ts`) ï¿½ **sans** `globalSetup`, **sans** `storageState` global, **sans** `request.post` API dans les specs ; couverture Playwright volontairement limitï¿½e aux surfaces invitï¿½es : rendu des formulaires auth et contrï¿½le d'accï¿½s des pages protï¿½gï¿½es via redirection vers `/login` ; validation locale forgot-password couverte par le test unitaire `__tests__/unit/app/ForgotPasswordPage.test.tsx` ; suite exï¿½cutï¿½e en **sï¿½riel** (`workers: 1`, `fullyParallel: false`) pour ï¿½viter les faux nï¿½gatifs sur les redirections client temporisï¿½es sous `next dev` ; suite admin authentifiï¿½e rï¿½servï¿½e ï¿½ un futur lot (`describe.skip` dans `admin.spec.ts`) ; **prï¿½requis** : `npx playwright install`, `webServer` lance `npm run dev` ; commande cible : `cd frontend && npx playwright test __tests__/e2e/auth.spec.ts __tests__/e2e/exercises.spec.ts __tests__/e2e/dashboard.spec.ts __tests__/e2e/badges.spec.ts __tests__/e2e/settings.spec.ts __tests__/e2e/admin.spec.ts --project=chromium`
- `FFI-L20D` is now closed (badges presentation domain): shared contracts in `frontend/lib/badges/types.ts` ; pure presentation helpers in `frontend/lib/badges/badgePresentation.ts` (medal paths, difficulty/glow, grid sort, locked motivation branches) consumed by `BadgeCard`, `BadgeGrid`, `BadgesProgressTabsSection` ; characterization tests + `PROTECTED_FRONTEND_SURFACES` budgets + `REQUIRED_CANONICAL_LIB_FILES` entries ; no intentional UX change
- `FFI-L20E` is now closed (settings security tab): `frontend/components/settings/SettingsSecuritySection.tsx` composes the privacy card + `SettingsSessionsList` / `SettingsSessionRow` ; pure helpers in `frontend/lib/settings/settingsSecurity.ts` (privacy row model, session location line, show-more count) ; `useSettingsPageController` unchanged ; characterization tests + guardrails ; no intentional UX change
- `FFI-L20F` is now closed (admin read-heavy shell): `frontend/components/admin/AdminReadHeavyPageShell.tsx` + `AdminStatePanel.tsx` deduplicate `PageHeader` / toolbar / error-loading-empty structure for `app/admin/analytics/page.tsx` and `app/admin/ai-monitoring/page.tsx` ; `app/admin/page.tsx` uses `AdminStatePanel` only inside its existing layout ; admin domain hooks unchanged ; characterization tests ; required seams + ownership in `frontendGuardrails.ts` ; no intentional UX change
- `FFI-L20G` is now closed (informative pages RSC): `frontend/app/about/page.tsx` and `frontend/app/privacy/page.tsx` use `getTranslations` (no route-level `use client`) ; no global i18n/proxy rewrite in this lot ; unit tests under `__tests__/unit/app/about|privacy/`
- `FFI-L20H` is now closed (targeted QA/a11y/polish, no structural reopen): `AdminStatePanel` / `LoadingState` / `SaveButton` / settings privacy+sessions / `BadgeCard` progressbar label / `ContentListProgressiveFilterToolbar` overflow guard ; characterization tests updated where touched
- next frontend focus shifts to product backlog / small fixes per audit â€” no open FFI-L20H seam as a named architecture train

## Current Stability Baseline (postâ€“iteration `I` closure, 2026-03-19)

Jalon historique valide ; le dÃ©pÃ´t a depuis accumulÃ© dâ€™autres preuves (dont reco **R** ci-dessous). Chiffres = **citations** de clÃ´ture documentÃ©e ; **re-lancer** les commandes si lâ€™arbre a divergÃ©.

Gate standard backend (`test_admin_auth_stability.py` exclu â€” test spÃ©cial non-bloquant) :

- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `962 passed, 3 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- measured local coverage on `app` + `server`: `67.30 %`
- backend CI coverage gate -> `63 %`

## Recommendation Iteration R Closure (2026-03-21)

Chiffres = **citations** de la clÃ´ture R7 (pas de nouvelle exÃ©cution imposÃ©e pour aligner la doc). **Micro-lot R7b** : mise Ã  jour des README racine uniquement, **sans rerun** ; vÃ©ritÃ© runtime inchangÃ©e.

Moteur reco aprÃ¨s **R** : rÃ¨gles heuristiques bornÃ©es et chemins testÃ©s ; **pas** dâ€™apprentissage ML ni personnalisation Â« intelligente Â» au sens data-science.

- Clï¿½ture gouvernance + rï¿½serves + non-revendications : [docs/03-PROJECT/archives/RECOMMENDATION_ITERATION_R_2026-03/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](docs/03-PROJECT/archives/RECOMMENDATION_ITERATION_R_2026-03/RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md)
- Reco ciblÃ©e : `pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` -> **`40 passed`**
- Gate standard backend (mÃªme commande que la section post-I) -> **`991 passed, 2 skipped`**
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

- **`POST /api/chat`** et **`POST /api/chat/stream`** (Starlette + routes Next `app/api/chat/*`) exigent une session valide (**CHAT-AUTH-01**) : plus de whitelist publique middleware ; le proxy Next refuse sans cookie `access_token` (401 JSON `UNAUTHORIZED`) et relaie `Cookie` + `X-CSRF-Token` lorsque la session est prï¿½sente ; rate-limit chat inchangï¿½ cï¿½tï¿½ backend ; **CHAT-DEFENSE-01**: `require_auth` / `require_auth_sse` on `server/handlers/chat_handlers.py` (defense in depth, same `server.auth` decorators, middleware unchanged).
- frontend proxy routes (`/api/chat`, `/api/chat/stream`, `/api/exercises/generate-ai-stream`, `/api/challenges/generate-ai-stream`) sont couverts par des tests de handlers Next.js au niveau route ; les deux POST SSE pï¿½dagogiques partagent `lib/api/sseProxyRequest.ts` (`proxySseGenerateAiStreamPost`) et `lib/api/proxyForwardHeaders.ts` pour parse JSON, auth cookie, forward headers, garde `body === null` backend et stream
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
- **FFI-L19C â€” client IP for rate-limit keys** (`app/utils/rate_limit.py`): `RATE_LIMIT_TRUST_X_FORWARDED_FOR` (default **false**, conservative). If **true**, first non-empty hop of `X-Forwarded-For` when present; else `request.client.host`. If **false**, **never** trust `X-Forwarded-For` (TCP peer only). Enable `true` only behind a trusted proxy that rewrites/appends XFF. See `.env.example` and [RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md](docs/03-PROJECT/RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md) Â§17.

#### Diagnostics `validate-token` (rafales 429 / attribution)

- **`POST /api/auth/validate-token`** : dÃ©corateur `rate_limit_validate_token`, plafond **`RATE_LIMIT_VALIDATE_TOKEN_MAX` (90/min par IP)**, clÃ© `rate_limit:validate-token:{ip}`. **Login / forgot-password** : `rate_limit_auth`, **`RATE_LIMIT_AUTH_SENSITIVE_MAX` (5/min)**, inchangÃ©.
- Sur **429**, les logs **WARNING** incluent le **bucket** (`validate_token` vs `auth_sensitive`), lâ€™**endpoint** (pour `auth_sensitive`), lâ€™**IP** effective, **User-Agent** et **Referer** tronquÃ©s, dÃ©but de **X-Forwarded-For** brut, et **`X-Mathakine-Validate-Caller`** si prÃ©sent (Next : `routeSession` / `syncCookie` via `buildValidateTokenRequestHeaders` â€” indication seulement, falsifiable).
- Sur **succÃ¨s** de `validate-token`, une ligne **INFO** `auth.validate_token: ok` reprend les mÃªmes indices (aucun token ni en-tÃªte `Authorization` dans les logs).
- **FFI-L19B** : `routeSession` et `sync-cookie` passent par `frontend/lib/auth/server/validateTokenRuntime.ts` â€” une seule requÃªte HTTP concurrente par `(baseUrl, token)` ; rÃ©utilisation dâ€™un **succÃ¨s** backend pendant **2,5 s** seulement (pas de cache des 401 / erreurs).
- RÃ©fÃ©rence : [RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md](docs/03-PROJECT/RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.md) (Â§15â€“Â§17). **FFI-L19\*** **clos** ; prioritÃ© active : roadmap **frontend** principale (voir `.claude/session-plan.md`).

**Rollback aprÃ¨s diagnostic**

1. **Complet** : revert du commit qui touche `app/utils/rate_limit.py` (dont `rate_limit_validate_token` / constantes), `server/handlers/auth_handlers.py`, `frontend/lib/auth/server/validateTokenBackendHeaders.ts`, `frontend/lib/auth/server/validateTokenRuntime.ts`, les appels dans `routeSession` / `sync-cookie`, `README_TECH.md`, et les tests associÃ©s ; redÃ©ployer.
2. **CiblÃ©** : retirer uniquement le `logger.info` dans `api_validate_token` si le volume INFO gÃªne ; garder le WARNING enrichi sur 429 pour les autres endpoints auth.
3. **Sans redÃ©ployer le frontend** : le backend ignore lâ€™absence du header ; seule lâ€™attribution `validate_caller` redevient `-` dans les logs.

## Architecture Clean (Cible A + B â€” closed)

- **Cible A** : `app/models/` and `app/schemas/` use explicit per-module imports; `all_models.py` and `all_schemas.py` have been removed (A1â€“A6).
- **Cible B** : `app/services/` is organised by DDD domains (auth, users, badges, exercises, challenges, progress, admin, analytics, communication, core, diagnostic, feedback, recommendation). No business logic file remains at root. See `docs/00-REFERENCE/ARCHITECTURE.md` Â§ app/services/.

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
