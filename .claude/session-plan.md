# Plan de session - Mathakine

## Fermeture du sidecar FFI-L19\* (validate-token / rate-limit / proxy trust)

| Lot          | Statut | Résumé                                                                                                                      |
| ------------ | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| **FFI-L19A** | Fermé  | Bucket backend dédié `validate-token` (90/min/IP) ; login/forgot-password stricts (5/min).                                  |
| **FFI-L19B** | Fermé  | Next server : `validateTokenRuntime.ts` - coalescence + micro-cache succès 2,5 s.                                           |
| **FFI-L19C** | Fermé  | Politique IP explicite : `RATE_LIMIT_TRUST_X_FORWARDED_FOR` + `_get_client_ip` documenté (voir rapport §17, `README_TECH`). |

**La séquence FFI-L19\* est terminée.** Ne pas rouvrir ce fil sans nouveau constat produit ou ticket dédié.

### Hors scope documenté (non traité en L19C)

- Headers CDN type `CF-Connecting-IP` sans setting et preuve infra dédiés.
- Liste `TRUSTED_PROXY_IPS` / CIDR pour n'utiliser XFF que si le hop TCP est un proxy connu.
- Re-key rate-limit par utilisateur (backlog produit distinct).

---

## Recentrage actif : roadmap frontend principale

Après clôture FFI-L19\*, la priorité d'exécution revient à la feuille de route frontend, notamment :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` comme snapshot qualité actif
- `docs/03-PROJECT/archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme contexte historique archivé

Les changements backend hors périmètre roadmap frontend doivent rester petits, nommés et reviewables.

### Hiérarchie de vérité documentaire

1. `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` pour la priorité produit active
2. `D:\Mathakine\.claude\session-plan.md` pour l'ordre d'exécution courant
3. `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` pour la dette frontend encore utile
4. `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` comme snapshot qualité actif de la file `QF-*`
5. `docs/03-PROJECT/archives/AUDITS_AND_REVIEWS_2026-03/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme photographie historique, non comme backlog actif

### État réel frontend après FFI-L18B

- la séquence de standardisation structurelle `FFI-L1` à `FFI-L18B` est considérée fermée
- les garde-fous d'architecture restent la protection active contre la rechute en monolithes
- il n'existe plus de dense exception ouverte dans `ALLOWED_DENSE_EXCEPTIONS`
- la suite frontend relève maintenant d'un durcissement ciblé

### Audit frontend d'industrialisation - 2026-04-08

Constat de pilotage :

- modularité globale frontend : bonne mais non terminale
- score de maturité retenu : **7.5/10**
- les lots `FFI-L11` à `FFI-L18B` ont fermé les mega-pages et hotspots explicitement ciblés
- les anciens risques structurels les plus lourds ont été fermés par `FFI-L20A` à `FFI-L20H`

### Avancement FFI-L20

| Lot          | Statut | Résumé                                                                                                                                                         |
| ------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FFI-L20A** | Fermé  | `app/dashboard/page.tsx` ramené à une coque ; runtime déplacé dans `hooks/useDashboardPageController.ts` ; tabs sorties vers `components/dashboard/*`.         |
| **FFI-L20B** | Fermé  | `ExerciseSolver.tsx` façade ; runtime dans `hooks/useExerciseSolverController.ts` ; helpers purs `lib/exercises/exerciseSolverFlow.ts`.                        |
| **FFI-L20C** | Fermé  | `useAuth` allégé ; contrats `lib/auth/types.ts`, helpers `authLoginFlow.ts`, `postLoginRedirect.ts` ; `Providers` segmenté en sous-blocs sync.                 |
| **FFI-L20D** | Fermé  | Contrats badges `lib/badges/types.ts` ; dérivations pures `lib/badges/badgePresentation.ts` ; `BadgeCard` / `BadgeGrid` / `BadgesProgressTabsSection` alignés. |
| **FFI-L20E** | Fermé  | `SettingsSecuritySection` allégée ; `SettingsSessionsList` / `SettingsSessionRow` ; helpers purs `lib/settings/settingsSecurity.ts`.                           |
| **FFI-L20F** | Fermé  | `AdminReadHeavyPageShell` + `AdminStatePanel` ; factorisation des états read-heavy sur `admin` / `analytics` / `ai-monitoring`.                                |
| **FFI-L20G** | Fermé  | `app/about/page.tsx` + `app/privacy/page.tsx` en Server Components avec `getTranslations` ; suppression du `use client` inutile.                               |
| **FFI-L20H** | Fermé  | Polish a11y / états : `role="alert"` / `status`, `LoadingState`, `SaveButton`, confidentialité / sessions, `BadgeCard`, toolbar listes.                        |

---

## Après FFI-L20\* : file active frontend / plateforme

La séquence d'industrialisation structurelle `FFI-L20A -> FFI-L20H` est terminée.
La suite frontend relève de lots ciblés, petits et reviewables, pilotés par risque/coût/solidité plutôt que par un nouveau chantier générique de découpage.

### Constat terrain synthétique - 2026-04-09

- forces confirmées :
  - TypeScript strict fort (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`)
  - guardrails d'architecture actifs et testés
  - Sentry production-grade (tunnel, replay masqué, release)
  - accessibilité structurelle renforcée par `FFI-L20H`
- point à nuancer :
  - le constat historique sur les 7 thèmes CSS n'a pas été revalidé exhaustivement dans cette passe

### File active fermée

1. ~~**CHAT-AUTH-01**~~ - **Fermé (2026-04-06)** - `POST /api/chat` et `POST /api/chat/stream` : barrière JWT côté Starlette (hors whitelist publique) + garde cookie `access_token` sur les routes Next proxy (`chatProxyRequest.ts`) ; relais `Cookie` / `X-CSRF-Token` ; UI drawer + bloc home : invités voient le CTA existant `guestLimitCta` (pas d'envoi).
2. ~~**RQ-PROVIDERS-02**~~ - **Fermé** - `QueryClient` via `useState(() => new QueryClient(...))` dans `Providers.tsx` ; instance stable par montage, mêmes `defaultOptions`.
3. ~~**CHAT-I18N-03**~~ - **Fermé** - chaînes `global-error`, `not-found` (CTA), proxies `app/api/chat/*` externalisées dans `messages/fr|en.json` (`errors.*`, `apiChat.proxy.*`) + `lib/api/chatProxyLocale.ts`.
4. ~~**CHAT-LOG-04**~~ - **Fermé** - `app/api/chat/stream/route.ts` logue uniquement en développement via `lib/utils/logInDevelopment.ts` ; mêmes payloads SSE d'erreur côté utilisateur ; test dédié de non-log en production.
5. ~~**LINT-STRICT-05**~~ - **Fermé** - `@typescript-eslint/no-explicit-any` et `react-hooks/exhaustive-deps` passées en `error` dans `eslint.config.mjs` ; `useDiagnostic` en `Record<string, unknown>` ; `npm run lint` vert.
6. ~~**E2E-CORE-06**~~ - **Fermé (minimal)** - specs Playwright `auth`, `exercises`, `dashboard`, `badges`, `settings`, `admin` ; sans `globalSetup`, sans `storageState` global, sans `request.post` API ; couverture volontairement limitée aux surfaces invitées ; validation locale forgot-password couverte par `ForgotPasswordPage.test.tsx` ; suite exécutée en série (`workers: 1`, `fullyParallel: false`) ; suite admin authentifiée laissée hors périmètre (`describe.skip`).
7. ~~**SSE-DRY-07**~~ - **Fermé** - factorisation des deux proxies SSE pédagogiques dans `frontend/lib/api/sseProxyRequest.ts` ; headers forward partagés via `frontend/lib/api/proxyForwardHeaders.ts` ; routes réduites à une config minimale (`backendPath`, `debugContext`, message SSE invité, label d'erreur dev) ; `body === null` backend transformé en event SSE d'erreur au lieu d'un flux vide ; bruit `console.error` "missing auth cookie" limité au développement.
8. ~~**CSP-HARDEN-08**~~ - **Fermé** - CSP globale extraite dans `frontend/lib/security/buildContentSecurityPolicy.ts` ; production sans `'unsafe-eval'` dans `script-src` ; ajouts `object-src 'none'`, `form-action 'self'`, `frame-src 'none'`, `upgrade-insecure-requests` ; `'unsafe-inline'` gardé hors stratégie nonce/hash.
9. ~~**OG-META-09**~~ - **Fermé** - images sociales **1200x630** via `app/opengraph-image.tsx` et `app/twitter-image.tsx` ; métadonnées globales branchées sur `/opengraph-image` et `/twitter-image` ; rendu commun via `lib/social/renderSocialShareImageResponse.tsx` avec polices explicites `KaTeX Main` (`lib/social/socialShareImageFonts.ts`) et runtime `nodejs` pour fiabiliser `ImageResponse` hors Vercel ; plus d'usage de l'icône `512x512` comme image sociale.

### Ordre d'exécution réel

1. ~~`CHAT-AUTH-01`~~ (fermé)
2. ~~`RQ-PROVIDERS-02`~~ (fermé)
3. ~~`CHAT-I18N-03`~~ (fermé)
4. ~~`CHAT-LOG-04`~~ (fermé)
5. ~~`LINT-STRICT-05`~~ (fermé)
6. ~~`E2E-CORE-06`~~ (fermé, minimal)
7. ~~`SSE-DRY-07`~~ (fermé)
8. ~~`CSP-HARDEN-08`~~ (fermé)
9. ~~`OG-META-09`~~ (fermé)

### État courant

- aucun lot frontend nommé restant dans cette série
- la suite doit repartir d'un nouveau constat terrain
- ne pas rouvrir une nouvelle série `FFI-L20*` par inertie

### QF-01 (2026-04-09) - fermé

- Suppression de `frontend/app/test-sentry` ; Sentry user = `{ id }` dans `useAuth` ; `SECRET_KEY` documenté dans `frontend/.env.example` ; guide `SENTRY_MONITORING.md` + audit 2026-04-09 réalignés.

### QF-02 (2026-04-09) - fermé

- Exports dashboard PDF/Excel : `import()` dynamique dans `lib/utils/exportPDF.ts` et `exportExcel.ts` au clic ; `ExportButton` en `await` ; pas de changement UX volontaire ; audit 2026-04-09 P1-PERF-02 / D7 alignés.

### QF-03 (2026-04-10) - fermé

- i18n route-level : copy des pages admin racines + `offline` externalisée dans `frontend/messages/fr.json` et `en.json` (`adminPages.*`, `offline`) ; `useTranslations` sur chaque page listée ; constantes de labels (exports, filtres audit, etc.) construites dans le composant ; pas de refonte shell/hooks métier ; tests unitaires ciblés + smoke wiring i18n.

### QF-04 (2026-04-10) - fermé

- ESLint : `no-unused-vars` et `no-require-imports` → **error** (0 signalement sur l’arbre linté ; `scripts/**` ignoré).
- `consistent-type-imports` → **error** + `eslint --fix` ; `disallowTypeAnnotations: false` pour les mocks Vitest (`typeof import("…")`).
- `import/no-cycle` : hors périmètre.

### QF-04B (2026-04-10) - fermé

- ESLint **type-aware** (flat config v9) : `projectService: true` + `tsconfigRootDir` sur `**/*.{ts,mts,tsx}` avec ignores `.next`, `out`, `build`, `coverage`, `scripts`, `node_modules` (pas d’activation massive d’autres règles `recommendedTypeChecked`).
- `@typescript-eslint/no-floating-promises` → **error** ; mesure initiale **64** signalements ; corrections **`void`** sur invalidations React Query, imports dynamiques, appels async dans handlers / effets (comportement produit inchangé).
- Vérifs : `npx tsc --noEmit`, `npm run lint`, Prettier sur fichiers touchés → verts.

### QF-04C (2026-04-10) - fermé

- `react-hooks/set-state-in-effect` et `react-hooks/preserve-manual-memoization` → **error** (signal déjà propre : **0** signalement actif avant durcissement ; `preserve-manual-memoization` jamais vu sur l’arbre).
- `useContentListOrderPreference` : hydration préférence tri via **initialiseur paresseux** `useState(() => …)` + `readStoredOrder` (clé stable par instance de hook) — suppression du `useEffect` + du `eslint-disable`.
- `useGuestChatAccess` : **une** suppression locale **conservée** (sync post-hydratation `sessionStorage` / quota invité, commentaire existant).
- Vérifs : `npx tsc --noEmit`, `npm run lint`, Prettier, `vitest` `useContentListPageController.test.tsx` → verts.

### QF-05 (2026-04-10) - fermé

- Playwright : parcours **authentifié réel** (compte seed `ObiWan` / `HelloThere123!` via `lib/constants/demoLogin`) sur **Chromium uniquement** (`test.skip` si `browserName !== "chromium"`) ; **pas** de `globalSetup`, `storageState` global, ni auth partagé.
- Helper `__tests__/e2e/helpers/demoUserAuth.ts` : `loginAsDemoUser`, `completeOnboardingIfNeeded` (classe minimale + submit → `/diagnostic`), `authenticateDemoUserForProtectedPages` ; navigation explicite vers `/dashboard` / `/badges` / `/settings` après session (diagnostic non automatisé).
- Specs : `auth.spec.ts` (login réel + tableau de bord), `dashboard.spec.ts`, `badges.spec.ts`, `settings.spec.ts` — assertions sur **titres `h1` / zones stables** ; invités inchangés sur tous projets.
- **Prérequis E2E** : backend joignable (`NEXT_PUBLIC_API_BASE_URL` / défaut `http://localhost:10000`) ; rate-limit login **5/min/IP** — suite sérielle `workers: 1` OK.
- Vérif : `npx playwright test __tests__/e2e/auth.spec.ts __tests__/e2e/dashboard.spec.ts __tests__/e2e/badges.spec.ts __tests__/e2e/settings.spec.ts --project=chromium` + `npm run lint` + `npx tsc --noEmit`.

### QF-06 (2026-04-10) - fermé

- Vitest : baseline de **couverture frontend figée** via un `coverage.include` explicite dans `frontend/vitest.config.ts` (`*.{ts,tsx}`, `app`, `components`, `hooks`, `i18n`, `lib`, `messages`) afin de stabiliser le dénominateur couvert par la CI sur les surfaces source du frontend.
- Seuils globaux posés au **plancher mesuré** du dépôt sur ce périmètre explicite : **statements 43%** (`3590/8291`), **branches 36%** (`3111/8420`), **functions 39%** (`899/2264`), **lines 44%** (`3423/7718`).
- Objectif : verrouiller la réalité actuelle sans casser la CI par un seuil arbitraire ; prochaine hausse à faire lot par lot après amélioration ciblée des domaines faibles.
- Vérifs : `npm run test:coverage`, `npm run lint`, `npx tsc --noEmit`, Prettier sur fichiers touchés → verts.

### QF-07A (2026-04-10) - fermé

- **CSP production** : retrait de `'unsafe-inline'` sur **`script-src`** au profit de **`'nonce-*'`** par requête ; émission du header **`Content-Security-Policy`** depuis **`frontend/proxy.ts`** (forward sur la requête + réponse) ; **plus de CSP dans `next.config.ts`** pour éviter deux sources de vérité.
- **`buildContentSecurityPolicy({ isDevelopment, scriptNonce })`** + **`generateCspNonce()`** dans `frontend/lib/security/buildContentSecurityPolicy.ts` ; **`style-src 'unsafe-inline'`** volontairement inchangé (inline styles applicatifs).
- **Matcher** proxy élargi aux routes « pages », exclusions explicites (`/api`, `/_next/static`, `/_next/image`, `/monitoring`, favicon / manifest / robots / sitemap, chemins avec extension).
- Tests : `buildContentSecurityPolicy.test.ts`, `middleware.test.ts` ; vérifs `tsc`, `lint`, `build`, `vitest` ciblé, Prettier sur fichiers touchés.

### QF-07B (2026-04-10) - fermé

- **Nonce consommateurs (serveur)** : header interne **`x-nonce`** (`CSP_NONCE_REQUEST_HEADER`) sur la requête forwardée par **`proxy.ts`**, aligné sur le nonce **`script-src`** en prod ; en **dev**, nonce distinct de la CSP scripts (toujours `unsafe-inline` / `unsafe-eval` côté `script-src`).
- **`buildMiddlewareCspBundle`** dans `frontend/lib/security/middlewareCsp.ts` ; **pas** de `RootLayout` async (évite de forcer tout l’arbre en **dynamic**). Consommation : **`headers().get(CSP_NONCE_REQUEST_HEADER)`** dans des layouts/pages async **imbriqués** si besoin. Devtools : inchangés, **`style-src 'unsafe-inline'`** suffit.
- Commentaire dans `instrumentation-client.ts` pour d’éventuels widgets Sentry injectant du inline plus tard.
- Tests : `middlewareCsp.test.ts` ; vérifs `tsc`, `lint`, `build`, vitest ciblé, Prettier.

### CHAT-DEFENSE-01 (2026-04-10) - fermé

- Handlers **`chat_api`** / **`chat_api_stream`** : **`@require_auth`** et **`@require_auth_sse`** (ordre au-dessus de **`@rate_limit_chat`**) dans `server/handlers/chat_handlers.py` ; middleware global **inchangé** ; pas de changement prompts / OpenAI / proxy Next.
- Tests : `tests/api/test_chat_endpoints.py` ; **`tests/unit/test_chat_handlers_auth.py`** (couche handler sans middleware) ; `pytest` ciblé vert.

### OPS-HEALTH-02 (2026-04-10) - fermé

- **Liveness** : `GET /live` → `200` JSON `{"status":"live"}` (aucune dépendance).
- **Readiness** : `GET /ready` → sondes **PostgreSQL** (+ **Redis** si prod + `REDIS_URL`) via `app/utils/readiness_probe.py`, timeout **2s** par étape, `200` / `503` JSON minimal (`not_ready` + `checks`) ; **`GET /health`** = alias readiness.
- **`render.yaml`** : `healthCheckPath: /ready` ; middleware maintenance + auth public : `/live`, `/ready`, `/health` ; Sentry `before_send` étendu aux nouveaux chemins.
- Tests : `tests/unit/test_readiness_probe.py`, `tests/api/test_base_endpoints.py`, `tests/unit/test_auth_middleware.py` ; CI smoke `GET /ready` ; doc `DEPLOYMENT_ENV`, `PRODUCTION_RUNBOOK`, `CICD_DEPLOY`, `README_TECH`.

### Règle de pilotage

- traiter la suite comme :
  - correctifs ciblés
  - dette qualitative mesurable
  - lots compacts et reviewables
- tout nouveau lot structurel frontend devra partir d'un nouveau constat terrain, pas d'une inertie documentaire
