# Plan de session - Mathakine

## Fermeture du sidecar FFI-L19\* (validate-token / rate-limit / proxy trust)

| Lot          | Statut | RÃ©sumÃ©                                                                                                                      |
| ------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **FFI-L19A** | FermÃ© | Bucket backend dÃ©diÃ© `validate-token` (90/min/IP) ; login/forgot-password stricts (5/min).                                  |
| **FFI-L19B** | FermÃ© | Next server : `validateTokenRuntime.ts` - coalescence + micro-cache succÃ¨s 2,5 s.                                            |
| **FFI-L19C** | FermÃ© | Politique IP explicite : `RATE_LIMIT_TRUST_X_FORWARDED_FOR` + `_get_client_ip` documentÃ© (voir rapport Â§17, `README_TECH`). |

**La sÃ©quence FFI-L19\* est terminÃ©e.** Ne pas rouvrir ce fil sans nouveau constat produit ou ticket dÃ©diÃ©.

### Hors scope documentÃ© (non traitÃ© en L19C)

- Headers CDN type `CF-Connecting-IP` sans setting et preuve infra dÃ©diÃ©s.
- Liste `TRUSTED_PROXY_IPS` / CIDR pour n'utiliser XFF que si le hop TCP est un proxy connu.
- Re-key rate-limit par utilisateur (backlog produit distinct).

---

## Recentrage actif : roadmap frontend principale

AprÃ¨s clÃ´ture FFI-L19\*, la prioritÃ© d'exÃ©cution revient Ã  la feuille de route frontend, notamment :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` comme snapshot qualitÃ© actif
- `docs/03-PROJECT/archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme contexte historique archivÃ©

Les changements backend hors pÃ©rimÃ¨tre roadmap frontend doivent rester petits, nommÃ©s et reviewables.

### HiÃ©rarchie de vÃ©ritÃ© documentaire

1. `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` pour la prioritÃ© produit active
2. `D:\Mathakine\.claude\session-plan.md` pour l'ordre d'exÃ©cution courant
3. `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` pour la dette frontend encore utile
4. `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` comme snapshot qualitÃ© actif de la file `QF-*`
5. `docs/03-PROJECT/archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme photographie historique, non comme backlog actif

### Ã‰tat rÃ©el frontend aprÃ¨s FFI-L18B

- la sÃ©quence de standardisation structurelle `FFI-L1` Ã  `FFI-L18B` est considÃ©rÃ©e fermÃ©e
- les garde-fous d'architecture restent la protection active contre la rechute en monolithes
- il n'existe plus de dense exception ouverte dans `ALLOWED_DENSE_EXCEPTIONS`
- la suite frontend relÃ¨ve maintenant d'un durcissement ciblÃ©

### Audit frontend d'industrialisation - 2026-04-08

Constat de pilotage :

- modularitÃ© globale frontend : bonne mais non terminale
- score de maturitÃ© retenu : **7.5/10**
- les lots `FFI-L11` Ã  `FFI-L18B` ont fermÃ© les mega-pages et hotspots explicitement ciblÃ©s
- les anciens risques structurels les plus lourds ont Ã©tÃ© fermÃ©s par `FFI-L20A` Ã  `FFI-L20H`

### Avancement FFI-L20

| Lot          | Statut | RÃ©sumÃ©                                                                                                                                                         |
| ------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FFI-L20A** | FermÃ© | `app/dashboard/page.tsx` ramenÃ© Ã  une coque ; runtime dÃ©placÃ© dans `hooks/useDashboardPageController.ts` ; tabs sorties vers `components/dashboard/*`.       |
| **FFI-L20B** | FermÃ© | `ExerciseSolver.tsx` faÃ§ade ; runtime dans `hooks/useExerciseSolverController.ts` ; helpers purs `lib/exercises/exerciseSolverFlow.ts`.                         |
| **FFI-L20C** | FermÃ© | `useAuth` allÃ©gÃ© ; contrats `lib/auth/types.ts`, helpers `authLoginFlow.ts`, `postLoginRedirect.ts` ; `Providers` segmentÃ© en sous-blocs sync.                |
| **FFI-L20D** | FermÃ© | Contrats badges `lib/badges/types.ts` ; dÃ©rivations pures `lib/badges/badgePresentation.ts` ; `BadgeCard` / `BadgeGrid` / `BadgesProgressTabsSection` alignÃ©s. |
| **FFI-L20E** | FermÃ© | `SettingsSecuritySection` allÃ©gÃ©e ; `SettingsSessionsList` / `SettingsSessionRow` ; helpers purs `lib/settings/settingsSecurity.ts`.                           |
| **FFI-L20F** | FermÃ© | `AdminReadHeavyPageShell` + `AdminStatePanel` ; factorisation des Ã©tats read-heavy sur `admin` / `analytics` / `ai-monitoring`.                                 |
| **FFI-L20G** | FermÃ© | `app/about/page.tsx` + `app/privacy/page.tsx` en Server Components avec `getTranslations` ; suppression du `use client` inutile.                                 |
| **FFI-L20H** | FermÃ© | Polish a11y / Ã©tats : `role="alert"` / `status`, `LoadingState`, `SaveButton`, confidentialitÃ© / sessions, `BadgeCard`, toolbar listes.                        |

---

## AprÃ¨s FFI-L20\* : file active frontend / plateforme

La sÃ©quence d'industrialisation structurelle `FFI-L20A -> FFI-L20H` est terminÃ©e.
La suite frontend relÃ¨ve de lots ciblÃ©s, petits et reviewables, pilotÃ©s par risque/coÃ»t/soliditÃ© plutÃ´t que par un nouveau chantier gÃ©nÃ©rique de dÃ©coupage.

### Constat terrain synthÃ©tique - 2026-04-09

- forces confirmÃ©es :
  - TypeScript strict fort (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`)
  - guardrails d'architecture actifs et testÃ©s
  - Sentry production-grade (tunnel, replay masquÃ©, release)
  - accessibilitÃ© structurelle renforcÃ©e par `FFI-L20H`
- point Ã  nuancer :
  - le constat historique sur les 7 thÃ¨mes CSS n'a pas Ã©tÃ© revalidÃ© exhaustivement dans cette passe

### File active fermÃ©e

1. ~~**CHAT-AUTH-01**~~ - **FermÃ© (2026-04-06)** - `POST /api/chat` et `POST /api/chat/stream` : barriÃ¨re JWT cÃ´tÃ© Starlette (hors whitelist publique) + garde cookie `access_token` sur les routes Next proxy (`chatProxyRequest.ts`) ; relais `Cookie` / `X-CSRF-Token` ; UI drawer + bloc home : invitÃ©s voient le CTA existant `guestLimitCta` (pas d'envoi).
2. ~~**RQ-PROVIDERS-02**~~ - **FermÃ©** - `QueryClient` via `useState(() => new QueryClient(...))` dans `Providers.tsx` ; instance stable par montage, mÃªmes `defaultOptions`.
3. ~~**CHAT-I18N-03**~~ - **FermÃ©** - chaÃ®nes `global-error`, `not-found` (CTA), proxies `app/api/chat/*` externalisÃ©es dans `messages/fr|en.json` (`errors.*`, `apiChat.proxy.*`) + `lib/api/chatProxyLocale.ts`.
4. ~~**CHAT-LOG-04**~~ - **FermÃ©** - `app/api/chat/stream/route.ts` logue uniquement en dÃ©veloppement via `lib/utils/logInDevelopment.ts` ; mÃªmes payloads SSE d'erreur cÃ´tÃ© utilisateur ; test dÃ©diÃ© de non-log en production.
5. ~~**LINT-STRICT-05**~~ - **FermÃ©** - `@typescript-eslint/no-explicit-any` et `react-hooks/exhaustive-deps` passÃ©es en `error` dans `eslint.config.mjs` ; `useDiagnostic` en `Record<string, unknown>` ; `npm run lint` vert.
6. ~~**E2E-CORE-06**~~ - **FermÃ© (minimal)** - specs Playwright `auth`, `exercises`, `dashboard`, `badges`, `settings`, `admin` ; sans `globalSetup`, sans `storageState` global, sans `request.post` API ; couverture volontairement limitÃ©e aux surfaces invitÃ©es ; validation locale forgot-password couverte par `ForgotPasswordPage.test.tsx` ; suite exÃ©cutÃ©e en sÃ©rie (`workers: 1`, `fullyParallel: false`) ; suite admin authentifiÃ©e laissÃ©e hors pÃ©rimÃ¨tre (`describe.skip`).
7. ~~**SSE-DRY-07**~~ - **FermÃ©** - factorisation des deux proxies SSE pÃ©dagogiques dans `frontend/lib/api/sseProxyRequest.ts` ; headers forward partagÃ©s via `frontend/lib/api/proxyForwardHeaders.ts` ; routes rÃ©duites Ã  une config minimale (`backendPath`, `debugContext`, message SSE invitÃ©, label d'erreur dev) ; `body === null` backend transformÃ© en event SSE d'erreur au lieu d'un flux vide ; bruit `console.error` "missing auth cookie" limitÃ© au dÃ©veloppement.
8. ~~**CSP-HARDEN-08**~~ - **FermÃ©** - CSP globale extraite dans `frontend/lib/security/buildContentSecurityPolicy.ts` ; production sans `'unsafe-eval'` dans `script-src` ; ajouts `object-src 'none'`, `form-action 'self'`, `frame-src 'none'`, `upgrade-insecure-requests` ; `'unsafe-inline'` gardÃ© hors stratÃ©gie nonce/hash.
9. ~~**OG-META-09**~~ - **FermÃ©** - images sociales **1200x630** via `app/opengraph-image.tsx` et `app/twitter-image.tsx` ; mÃ©tadonnÃ©es globales branchÃ©es sur `/opengraph-image` et `/twitter-image` ; rendu commun via `lib/social/renderSocialShareImageResponse.tsx` avec polices explicites `KaTeX Main` (`lib/social/socialShareImageFonts.ts`) et runtime `nodejs` pour fiabiliser `ImageResponse` hors Vercel ; plus d'usage de l'icÃ´ne `512x512` comme image sociale.

### Ordre d'exÃ©cution rÃ©el

1. ~~`CHAT-AUTH-01`~~ (fermÃ©)
2. ~~`RQ-PROVIDERS-02`~~ (fermÃ©)
3. ~~`CHAT-I18N-03`~~ (fermÃ©)
4. ~~`CHAT-LOG-04`~~ (fermÃ©)
5. ~~`LINT-STRICT-05`~~ (fermÃ©)
6. ~~`E2E-CORE-06`~~ (fermÃ©, minimal)
7. ~~`SSE-DRY-07`~~ (fermÃ©)
8. ~~`CSP-HARDEN-08`~~ (fermÃ©)
9. ~~`OG-META-09`~~ (fermÃ©)

### Ã‰tat courant

- aucun lot frontend nommÃ© restant dans cette sÃ©rie
- la suite doit repartir d'un nouveau constat terrain
- ne pas rouvrir une nouvelle sÃ©rie `FFI-L20*` par inertie

### QF-01 (2026-04-09) - fermÃ©

- Suppression de `frontend/app/test-sentry` ; Sentry user = `{ id }` dans `useAuth` ; `SECRET_KEY` documentÃ© dans `frontend/.env.example` ; guide `SENTRY_MONITORING.md` + audit 2026-04-09 rÃ©alignÃ©s.

### QF-02 (2026-04-09) - fermÃ©

- Exports dashboard PDF/Excel : `import()` dynamique dans `lib/utils/exportPDF.ts` et `exportExcel.ts` au clic ; `ExportButton` en `await` ; pas de changement UX volontaire ; audit 2026-04-09 P1-PERF-02 / D7 alignÃ©s.

### QF-03 (2026-04-10) - fermÃ©

- i18n route-level : copy des pages admin racines + `offline` externalisÃ©e dans `frontend/messages/fr.json` et `en.json` (`adminPages.*`, `offline`) ; `useTranslations` sur chaque page listÃ©e ; constantes de labels (exports, filtres audit, etc.) construites dans le composant ; pas de refonte shell/hooks mÃ©tier ; tests unitaires ciblÃ©s + smoke wiring i18n.

### QF-03B (2026-04-10) - fermé

- i18n de la **navigation admin** restante : `frontend/app/admin/layout.tsx` lit `adminPages.layout.*` (`navAriaLabel`, libellés latéraux) via `useTranslations` ; `aria-current="page"` ajouté sur le lien actif.
- i18n des **descriptions de toasts auth** encore inline dans `frontend/hooks/useAuth.ts` : création des clés `toasts.auth.registerVerifyEmailDescription`, `forgotPasswordSuccessDescription`, `forgotPasswordErrorDescription`.
- Tests : `frontend/__tests__/unit/app/admin/AdminLayout.test.tsx` + mise à jour de `frontend/__tests__/unit/hooks/useAuth.test.ts`.

### QF-04 (2026-04-10) - fermÃ©

- ESLint : `no-unused-vars` et `no-require-imports` â†’ **error** (0 signalement sur lâ€™arbre lintÃ© ; `scripts/**` ignorÃ©).
- `consistent-type-imports` â†’ **error** + `eslint --fix` ; `disallowTypeAnnotations: false` pour les mocks Vitest (`typeof import("â€¦")`).
- `import/no-cycle` : hors pÃ©rimÃ¨tre.

### QF-04B (2026-04-10) - fermÃ©

- ESLint **type-aware** (flat config v9) : `projectService: true` + `tsconfigRootDir` sur `**/*.{ts,mts,tsx}` avec ignores `.next`, `out`, `build`, `coverage`, `scripts`, `node_modules` (pas dâ€™activation massive dâ€™autres rÃ¨gles `recommendedTypeChecked`).
- `@typescript-eslint/no-floating-promises` â†’ **error** ; mesure initiale **64** signalements ; corrections **`void`** sur invalidations React Query, imports dynamiques, appels async dans handlers / effets (comportement produit inchangÃ©).
- VÃ©rifs : `npx tsc --noEmit`, `npm run lint`, Prettier sur fichiers touchÃ©s â†’ verts.

### QF-04C (2026-04-10) - fermÃ©

- `react-hooks/set-state-in-effect` et `react-hooks/preserve-manual-memoization` â†’ **error** (signal dÃ©jÃ  propre : **0** signalement actif avant durcissement ; `preserve-manual-memoization` jamais vu sur lâ€™arbre).
- `useContentListOrderPreference` : hydration prÃ©fÃ©rence tri via **initialiseur paresseux** `useState(() => â€¦)` + `readStoredOrder` (clÃ© stable par instance de hook) â€” suppression du `useEffect` + du `eslint-disable`.
- `useGuestChatAccess` : **une** suppression locale **conservÃ©e** (sync post-hydratation `sessionStorage` / quota invitÃ©, commentaire existant).
- VÃ©rifs : `npx tsc --noEmit`, `npm run lint`, Prettier, `vitest` `useContentListPageController.test.tsx` â†’ verts.

### QF-05 (2026-04-10) - fermÃ©

- Playwright : parcours **authentifiÃ© rÃ©el** (compte seed `ObiWan` / `HelloThere123!` via `lib/constants/demoLogin`) sur **Chromium uniquement** (`test.skip` si `browserName !== "chromium"`) ; **pas** de `globalSetup`, `storageState` global, ni auth partagÃ©.
- Helper `__tests__/e2e/helpers/demoUserAuth.ts` : `loginAsDemoUser`, `completeOnboardingIfNeeded` (classe minimale + submit â†’ `/diagnostic`), `authenticateDemoUserForProtectedPages` ; navigation explicite vers `/dashboard` / `/badges` / `/settings` aprÃ¨s session (diagnostic non automatisÃ©).
- Specs : `auth.spec.ts` (login rÃ©el + tableau de bord), `dashboard.spec.ts`, `badges.spec.ts`, `settings.spec.ts` â€” assertions sur **titres `h1` / zones stables** ; invitÃ©s inchangÃ©s sur tous projets.
- **PrÃ©requis E2E** : backend joignable (`NEXT_PUBLIC_API_BASE_URL` / dÃ©faut `http://localhost:10000`) ; rate-limit login **5/min/IP** â€” suite sÃ©rielle `workers: 1` OK.
- VÃ©rif : `npx playwright test __tests__/e2e/auth.spec.ts __tests__/e2e/dashboard.spec.ts __tests__/e2e/badges.spec.ts __tests__/e2e/settings.spec.ts --project=chromium` + `npm run lint` + `npx tsc --noEmit`.

### QF-06 (2026-04-10) - fermÃ©

- Vitest : baseline de **couverture frontend figÃ©e** via un `coverage.include` explicite dans `frontend/vitest.config.ts` (`*.{ts,tsx}`, `app`, `components`, `hooks`, `i18n`, `lib`, `messages`) afin de stabiliser le dÃ©nominateur couvert par la CI sur les surfaces source du frontend.
- Seuils globaux posÃ©s au **plancher mesurÃ©** du dÃ©pÃ´t sur ce pÃ©rimÃ¨tre explicite : **statements 43%** (`3590/8291`), **branches 36%** (`3111/8420`), **functions 39%** (`899/2264`), **lines 44%** (`3423/7718`).
- Objectif : verrouiller la rÃ©alitÃ© actuelle sans casser la CI par un seuil arbitraire ; prochaine hausse Ã  faire lot par lot aprÃ¨s amÃ©lioration ciblÃ©e des domaines faibles.
- VÃ©rifs : `npm run test:coverage`, `npm run lint`, `npx tsc --noEmit`, Prettier sur fichiers touchÃ©s â†’ verts.

### QF-07A (2026-04-10) - fermÃ©

- **CSP production** : retrait de `'unsafe-inline'` sur **`script-src`** au profit de **`'nonce-*'`** par requÃªte ; Ã©mission du header **`Content-Security-Policy`** depuis **`frontend/proxy.ts`** (forward sur la requÃªte + rÃ©ponse) ; **plus de CSP dans `next.config.ts`** pour Ã©viter deux sources de vÃ©ritÃ©.
- **`buildContentSecurityPolicy({ isDevelopment, scriptNonce })`** + **`generateCspNonce()`** dans `frontend/lib/security/buildContentSecurityPolicy.ts` ; **`style-src 'unsafe-inline'`** volontairement inchangÃ© (inline styles applicatifs).
- **Matcher** proxy Ã©largi aux routes Â« pages Â», exclusions explicites (`/api`, `/_next/static`, `/_next/image`, `/monitoring`, favicon / manifest / robots / sitemap, chemins avec extension).
- Tests : `buildContentSecurityPolicy.test.ts`, `middleware.test.ts` ; vÃ©rifs `tsc`, `lint`, `build`, `vitest` ciblÃ©, Prettier sur fichiers touchÃ©s.

### QF-07B (2026-04-10) - fermÃ©

- **Nonce consommateurs (serveur)** : header interne **`x-nonce`** (`CSP_NONCE_REQUEST_HEADER`) sur la requÃªte forwardÃ©e par **`proxy.ts`**, alignÃ© sur le nonce **`script-src`** en prod ; en **dev**, nonce distinct de la CSP scripts (toujours `unsafe-inline` / `unsafe-eval` cÃ´tÃ© `script-src`).
- **`buildMiddlewareCspBundle`** dans `frontend/lib/security/middlewareCsp.ts`. _(HypothÃ¨se QF-07B partiellement rÃ©visÃ©e par **QF-07C** : le root layout **doit** participer au flux nonce + dynamic pour les scripts inline Next en prod.)_
- Commentaire dans `instrumentation-client.ts` pour dâ€™Ã©ventuels widgets Sentry injectant du inline plus tard.
- Tests : `middleware.test.ts` (CSP + nonce forward) ; vÃ©rifs `tsc`, `lint`, `build`, vitest ciblÃ©, Prettier.

### QF-07C (2026-04-10) - fermé

- **CSP nonce + App Router (terrain)** : en prod, les scripts inline du framework (`self.__next_f.push`, etc.) **sans** nonce Ã©taient bloquÃ©s sous `script-src 'nonce-*'` malgrÃ© une CSP injectÃ©e par **`proxy.ts`**.
- **Correctif** : `frontend/app/layout.tsx` â€” **`export const dynamic = "force-dynamic"`**, layout racine **async**, **`headers().get(CSP_NONCE_REQUEST_HEADER)`** â†’ **`nonce`** sur **`<html>`** ; alignÃ© avec la doc Next (rendu par requÃªte requis pour nonces). **Pas** de retour Ã  `unsafe-inline` sur `script-src` prod ; **`style-src`** inchangÃ© dans ce lot.
- **ConsÃ©quence hÃ©bergement** : pages App Router **dynamiques** (build : **Æ’** quasi partout) ; moins / pas dâ€™optimisation statique HTML ; coÃ»t CPU/latence serveur plus Ã©levÃ© quâ€™en full SSG â€” assumÃ© pour compatibilitÃ© CSP stricte.
- **VÃ©rifs** : `npm run build` (routes **Æ’**), `npm run lint`, `npx tsc --noEmit`, Prettier sur fichiers touchÃ©s ; `next start` + HTML `/login` avec `nonce=` sur scripts inline ; pas de rÃ©gression **`proxy.ts`** / auth.
- Doc : `README_TECH.md` (paragraphe CSP), ce fichier, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`.

### CHAT-DEFENSE-01 (2026-04-10) - fermÃ©

- Handlers **`chat_api`** / **`chat_api_stream`** : **`@require_auth`** et **`@require_auth_sse`** (ordre au-dessus de **`@rate_limit_chat`**) dans `server/handlers/chat_handlers.py` ; middleware global **inchangÃ©** ; pas de changement prompts / OpenAI / proxy Next.
- Tests : `tests/api/test_chat_endpoints.py` ; **`tests/unit/test_chat_handlers_auth.py`** (couche handler sans middleware) ; `pytest` ciblÃ© vert.

### OPS-HEALTH-02 (2026-04-10) - fermÃ©

- **Liveness** : `GET /live` â†’ `200` JSON `{"status":"live"}` (aucune dÃ©pendance).
- **Readiness** : `GET /ready` â†’ sondes **PostgreSQL** (+ **Redis** si prod + `REDIS_URL`) via `app/utils/readiness_probe.py`, timeout **2s** par Ã©tape, `200` / `503` JSON minimal (`not_ready` + `checks`) ; **`GET /health`** = alias readiness.
- **`render.yaml`** : `healthCheckPath: /ready` ; middleware maintenance + auth public : `/live`, `/ready`, `/health` ; Sentry `before_send` Ã©tendu aux nouveaux chemins.
- Tests : `tests/unit/test_readiness_probe.py`, `tests/api/test_base_endpoints.py`, `tests/unit/test_auth_middleware.py` ; CI smoke `GET /ready` ; doc `DEPLOYMENT_ENV`, `PRODUCTION_RUNBOOK`, `CICD_DEPLOY`, `README_TECH`.

### OPS-ASGI-03 (2026-04-10) - fermÃ©

- **Prod Render** : backend dÃ©marrÃ© via **`gunicorn enhanced_server:app`** + **`uvicorn.workers.UvicornWorker`** ; **`WEB_CONCURRENCY`** explicite dans `render.yaml` (`2` par dÃ©faut) ; `Procfile` alignÃ© sur le mÃªme modÃ¨le.
- **Dev local** : inchangÃ©, `python enhanced_server.py` reste le point d'entrÃ©e pratique ; `enhanced_server:app` devient la vÃ©ritÃ© ASGI explicite pour les process managers.
- **CI / docs** : smoke `gunicorn --check-config` dans `.github/workflows/tests.yml` ; guides `DEPLOYMENT_ENV`, `PRODUCTION_RUNBOOK`, `SCRIPTS_UTILITIES`, `CICD_DEPLOY`, `README_TECH` rÃ©alignÃ©s ; correction d'une incohÃ©rence active dans `PRODUCTION_RUNBOOK` qui disait encore Ã  tort que le chat Ã©tait public.

### SEC-HARDEN-01 (2026-04-06) - fermé

- **Logs** (`app/core/logging_config.py`) : sink fichier `uncaught_exceptions.log` — **`diagnose=False`** en environnement **production-like** (mêmes signaux que `config._is_production`, via `os.getenv` uniquement — pas d’import `config` pour éviter le cycle) ; **`backtrace=True`** conservé ; hors prod, **`diagnose=True`** pour le debug fichier.
- **Headers** (`server/middleware.py`, si `SECURE_HEADERS`) : **`Permissions-Policy`** minimal (`camera=(), microphone=(), geolocation=()`) ; **`Strict-Transport-Security: max-age=31536000; includeSubDomains`** **uniquement** si **`_is_production()`** (pas en dev/CI locale).
- **Tests** : `tests/unit/test_logging_config_uncaught.py`, `tests/unit/test_secure_headers_middleware.py`, `test_permissions_policy_header_present` dans `tests/api/test_base_endpoints.py`.
- **Vérifs** : `pytest` ciblé, `black` / `isort` / `flake8` (E9,F63,F7,F82) / `mypy` sur fichiers touchés ; `README_TECH.md` + ce fichier.

### RÃ¨gle de pilotage

- traiter la suite comme :
  - correctifs ciblÃ©s
  - dette qualitative mesurable
  - lots compacts et reviewables
- tout nouveau lot structurel frontend devra partir d'un nouveau constat terrain, pas d'une inertie documentaire
