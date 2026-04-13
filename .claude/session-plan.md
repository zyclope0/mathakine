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

### ACTIF-03-CHAT-COMPONENTS-COLOCATE-01 (2026-04-12) - fermé

- Déplacement de **`ChatMessagesView.test.tsx`**, **`ChatbotFloating.test.tsx`**, **`ChatbotFloatingGlobal.test.tsx`** de **`frontend/__tests__/unit/components/chat/`** vers **`frontend/components/chat/`** (imports **`@/`** inchangés).
- Aucun changement des composants sources, pas de modification de **`vitest.config.ts`**, pas de réécriture de la logique des tests.
- Vérifs : `npm run lint`, `npx tsc --noEmit`, `npx vitest run` sur les trois fichiers, Prettier ; audit **[ACTIF-03]** reste ouvert ; lot documenté **`README_TECH.md`** + **`AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`**.

### ACTIF-03-VISUALIZATION-COLOCATE-01 (2026-04-12) - fermé

- Déplacement de **`VisualizationRenderers.test.tsx`** et **`VisualRenderer.symmetry.test.tsx`** de **`frontend/__tests__/unit/components/`** vers **`frontend/components/challenges/visualizations/`** (imports **`@/`** inchangés).
- Aucun changement des renderers sources, pas de modification de **`vitest.config.ts`**, pas de réécriture de la logique des tests.
- Vérifs : `npm run lint`, `npx tsc --noEmit`, `npx vitest run` sur les deux fichiers, Prettier ; audit **[ACTIF-03]** reste ouvert ; lot documenté **`README_TECH.md`** + **`AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`**.

### ACTIF-07-COLORMAP-01 (2026-04-12) - fermé

- **`frontend/components/challenges/visualizations/_colorMap.ts`** : **`VISUALIZATION_COLOR_MAP`** canonique FR/EN → hex (incl. **`brown` / `marron`**), **`resolveVisualizationColor`**, **`findVisualizationColorInText`**.
- **`VisualRenderer.tsx`** / **`ProbabilityRenderer.tsx`** : suppression des maps inline ; import du module partagé ; alignement blanc/noir sur les hex déjà utilisés dans **`VisualRenderer`** ; **`ProbabilityRenderer`** conserve les fallbacks (`colorName.toLowerCase()`, **`#6b7280`**).
- Tests : **`components/challenges/visualizations/_colorMap.test.ts`**.
- Vérifs : `npm run lint`, `npx tsc --noEmit`, `npx vitest run` (ciblés), Prettier sur fichiers touchés.

### QF-06B-VITEST-ALIGN-01 (2026-04-13) - fermé

- **`frontend/package.json`** : alignement de la famille **Vitest** sur la résolution réelle du lockfile après le bump **`@vitest/ui`** : **`vitest`**, **`@vitest/ui`**, **`@vitest/coverage-v8`** en **`^4.1.4`**.
- **`frontend/vitest.config.ts`** : inchangé volontairement ; aucun usage des features **browser screenshot**, **`experimental.matchesTags`**, **`experimental.vcsProvider`** ni besoin de revoir **`setupFiles`**.
- Backlog utile uniquement : réévaluer les workarounds défensifs des suites **mock-heavy** quand on les retouche (fix séquentiel **mock/unmock**), et refaire une **mesure CI** avant tout futur bump **ACTIF-04**.

### ACTIF-06-AI-MONITORING-01 (2026-04-12) - fermé

- **`frontend/hooks/useAdminAiMonitoringPageController.ts`** : état `days` (1 / 7 / 30), agrégation **`useAdminAiStats`** / **`useAdminGenerationMetrics`** / **`useAdminAiEvalHarnessRuns`** (**`HARNESS_RUNS_LIMIT`** 25), dérivés tableaux, **`formatWorkloadLabel`**, **`daysOptions`**, **`handleDaysChange`**.
- **`frontend/app/admin/ai-monitoring/page.tsx`** : coque vue + toolbar **`Select`** + formatters **`formatCost`** / **`formatRate`** / **`formatDuration`** inchangés ; pas de changement UX ni de clés i18n.
- Tests : **`hooks/useAdminAiMonitoringPageController.test.tsx`** ; **`__tests__/unit/app/admin/AdminAiMonitoringPage.test.tsx`** (mocks hooks inchangés).
- Vérifs : `npm run lint`, `npx tsc --noEmit`, `npx vitest run` (ciblés), Prettier sur fichiers touchés.

### QF-03B (2026-04-10) - fermé

- i18n de la **navigation admin** restante : `frontend/app/admin/layout.tsx` lit `adminPages.layout.*` (`navAriaLabel`, libellés latéraux) via `useTranslations` ; `aria-current="page"` ajouté sur le lien actif.
- i18n des **descriptions de toasts auth** encore inline dans `frontend/hooks/useAuth.ts` : création des clés `toasts.auth.registerVerifyEmailDescription`, `forgotPasswordSuccessDescription`, `forgotPasswordErrorDescription`.
- Tests : `frontend/__tests__/unit/app/admin/AdminLayout.test.tsx` + mise à jour de `frontend/hooks/useAuth.test.ts`.

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

### SEC-HARDEN-01 (2026-04-10) - fermé

- **Logs** (`app/core/logging_config.py`) : sink fichier `uncaught_exceptions.log` — **`diagnose=False`** en environnement **production-like** (mêmes signaux que `config._is_production`, via `os.getenv` uniquement — pas d’import `config` pour éviter le cycle) ; **`backtrace=True`** conservé ; hors prod, **`diagnose=True`** pour le debug fichier.
- **Headers** (`server/middleware.py`, si `SECURE_HEADERS`) : **`Permissions-Policy`** minimal (`camera=(), microphone=(), geolocation=()`) ; **`Strict-Transport-Security: max-age=31536000; includeSubDomains`** **uniquement** si **`_is_production()`** (pas en dev/CI locale).
- **Tests** : `tests/unit/test_logging_config_uncaught.py`, `tests/unit/test_secure_headers_middleware.py`, `test_permissions_policy_header_present` dans `tests/api/test_base_endpoints.py`.
- **Vérifs** : `pytest` ciblé, `black` / `isort` / `flake8` (E9,F63,F7,F82) / `mypy` sur fichiers touchés ; `README_TECH.md` + ce fichier.

### SEC-PII-LOGS-01 (2026-04-10) - fermé

- **Logs auth** (`app/services/auth/auth_service.py`) : plus de `username` / `email` en clair ; alias stables **`user#` / `email#` + 12 hex** (HMAC-SHA256 tronqué avec **`settings.SECRET_KEY`**, sels de contexte séparés) et **`user_id=`** lorsque l’utilisateur est résolu en base ; contrats JWT, cookies et réponses HTTP inchangés.
- **Tests** : `tests/unit/test_auth_service.py` — helpers de pseudonymisation (stabilité, cas distincts, email normalisé, chaînes vides), caplog sur `authenticate_user` (succès + utilisateur inexistant) sans fuite du username brut.
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (finding M5 + ligne ROI n°1), ce fichier.

### AUTH-FALLBACK-02 (2026-04-10) - fermé

- **Fallback refresh** (`recover_refresh_token_from_access_token` dans `app/services/auth/auth_service.py`) : fenêtre de grâce sur **access JWT expiré** réduite de **7 jours** à **3600 s** (constante **`ACCESS_TOKEN_FALLBACK_MAX_AGE_SECONDS`**) ; même signature publique, paramètre **`max_age_seconds`** toujours surchargeable ; pas de changement d’endpoints ; `recover_refresh_token_fallback` documenté dans `auth_session_service.py`.
- **Logging** : refus pour JWT invalide en **`debug`** sans **`exc_info`** (pas de stack brute).
- **Tests** : `tests/unit/test_auth_service.py` — accepté si expiré &lt; 1h, refus si &gt; 1h, sans `exp` / sans `sub`, user absent ou inactif, override `max_age_seconds` ; ancien scénario « très vieux token » conservé. Docstring `tests/integration/test_auth_no_fallback.py` réalignée (flux body `refresh_token` vs fallback cookie).
- **Vérifs** : `pytest -k recover_refresh_token_from_access_token`, `black` / `isort` / `flake8` (E9,F63,F7,F82), `mypy` sur `app/services/auth/auth_service.py` + `auth_session_service.py` ; `README_TECH.md` + ce fichier.

### AUTH-HARDEN-02 (2026-04-10) - fermé

- **Cookies auth** : `get_cookie_config()` dans `app/core/security.py` s’appuie sur **`_is_production()`** (`app/core/config.py`) au lieu de relire `os.getenv` en local — même tuple **`("none", True)`** / **`("lax", False)`**, même signature ; pas de cycle d’import (`config` n’importe pas `security`).
- **Tests** : `tests/unit/test_security.py` — mock de **`app.core.security._is_production`**.
- **Vérifs** : `pytest tests/unit/test_security.py`, `black` / `isort` / `flake8` (E9,F63,F7,F82), `mypy` sur fichiers touchés ; `README_TECH.md` + ce fichier.

### AUDIT-QUICKWINS-01 (2026-04-10) - fermé

- **Headers** : `server/middleware.py` remplace **`X-XSS-Protection: 1; mode=block`** par **`X-XSS-Protection: 0`** (valeur moderne défendable, cohérente OWASP ; la protection réelle repose sur CSP et les autres headers).
- **Docker** : `.dockerignore` n’exclut plus `migrations/versions/*` ; les versions Alembic restent dans l’image pour que `alembic upgrade head` fonctionne en build/runtime Docker.
- **Frontend images** : les 5 suppressions `@next/next/no-img-element` encore présentes portent maintenant une justification **`Intentional:`** adjacente (`UserAvatar`, `BadgesProgressTabsSection`, `BadgeIcon`, `BadgeCard`, `ChatMessagesView`) ; pas de migration forcée vers `next/image` tant que les contraintes runtime (URLs dynamiques, fallback DOM, petits SVG décoratifs) ne sont pas traitées proprement.
- **Vérifs** : `pytest tests/unit/test_secure_headers_middleware.py tests/api/test_base_endpoints.py::test_permissions_policy_header_present`, `black` sur `server/middleware.py`, `prettier --check` sur les 5 composants frontend touchés.

### PERF-IMG-LOCAL-01 (2026-04-10) - fermé

- **Cible** : médailles SVG **locales** (`resolveMedalSvgPath` → `/public/badges/svg/*.svg`) dans **`frontend/components/badges/BadgeCard.tsx`** et **`BadgesProgressTabsSection.tsx`** → **`next/image`** (`width` / `height` / `sizes`, `alt=""`, `aria-hidden` inchangé côté accessibilité décorative).
- **Hors scope confirmé** : `UserAvatar`, `BadgeIcon`, `ChatMessagesView` ; pas de migration repo-wide ; pas de changement métier badges.
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (bloc **P1-PERF-03** partiellement avancé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run` sur les deux tests unitaires badges listés par le lot, `prettier --check` sur les fichiers touchés.

### COMP-BADGECARD-01 (2026-04-11) - fermé

- **Refactor** : `frontend/components/badges/BadgeCard.tsx` reste l’API publique (`BadgeCard`, `BadgeCardProps`) ; sections denses extraites dans **`frontend/components/badges/badgeCard/`** — **`BadgeCardDifficultyMedal`**, **`BadgeCardCompactEarnedHeader`**, **`BadgeCardStandardHeader`**, **`BadgeCardCardContent`** (motivation / progressbar / pied verrouillé inclus).
- **Inchangé** : props, i18n, règles `badgePresentation`, animations motion, shimmer ; périmètre limité à `BadgeCard` et ses sous-composants locaux.
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (**P3-COMP-01**), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run components/badges/BadgeCard.test.tsx`, `prettier --check` sur les fichiers touchés.

### ARCH-HOME-LEARNER-01 (2026-04-11) - fermé

- **Refactor** : `frontend/app/home-learner/page.tsx` = coque **`ProtectedRoute`** + **`HomeLearnerContent`** ; sections **`HomeLearnerPageMap`**, **`HomeLearnerReviewsSection`**, **`HomeLearnerActionsSection`**, **`HomeLearnerProgressSection`** sous **`frontend/components/learner/`** ; **`homeLearnerConstants.ts`**, **`homeLearnerI18n.ts`** pour découplage typé sans nouveau hook métier.
- **Inchangé** : hooks existants (`useAuth`, `useProgressStats`, `useUserStats`, `useRecommendations`), ordre conditionnel révisions / actions, ancres `#section-*`, CTA et `recordOpen`, widgets dashboard non refactorés en profondeur.
- **Suite** : **`ARCH-EXERCISES-01`** ferme le sous-cas `app/exercises/page.tsx` (**P1-ARCH-05** complet).
- **Tests** : `frontend/__tests__/unit/app/home-learner/HomeLearnerPage.test.tsx` (smoke sections + ordre ancres / DOM).
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (**P1-ARCH-05**), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run __tests__/unit/app/home-learner/HomeLearnerPage.test.tsx`, `prettier --check` sur les fichiers touchés.

### ARCH-LEADERBOARD-01 (2026-04-11) - fermé

- **Refactor** : `frontend/app/leaderboard/page.tsx` = coque **`ProtectedRoute`** + **`LeaderboardPageContent`** ; **`frontend/components/leaderboard/`** — **`LeaderboardPageContent`** (hooks, période, flags `inTop` / `showMyRankFooter`), **`LeaderboardCardState`** (error / loading / empty / success), **`LeaderboardList`** + **`LeaderboardCurrentUserFooter`**, **`LeaderboardRow`** + **`LeaderboardRankBadge`** + **`LeaderboardAnimatedPoints`** + **`LeaderboardSectionSeparator`**, **`leaderboardPageMotion.ts`** (variants inchangés).
- **Inchangé** : **`useLeaderboard`**, **`useMyLeaderboardRank`**, **`useAuth`**, i18n, **`UserAvatar`**, règles `progressionRankLabel` / `canonicalProgressionRankBucket`, **`useCountUp`**, structure podium / top10 / rest / footer « votre rang ».
- **Hors lot** : pas de **`useLeaderboardPageController`** (gain non requis pour fermer la dette découpage) ; redesign / refonte animation stratégique.
- **Tests** : `frontend/__tests__/unit/app/leaderboard/LeaderboardPage.test.tsx` (inchangé, toujours vert).
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (**P1-PERF-01**), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run __tests__/unit/app/leaderboard/LeaderboardPage.test.tsx`, `prettier --check` sur fichiers touchés.

### ARCH-EXERCISES-01 (2026-04-11) - fermé

- **Refactor** : `frontend/app/exercises/page.tsx` = coque **`Suspense`** + fallback (`ProtectedRoute` + `PageLayout` + `ExercisesListLoadingShell`) ; **`frontend/components/exercises/ExercisesPageContent.tsx`** (hooks **`useContentListPageController`**, **`useExercises`**, effet `generated=true`, toolbar, générateur, modal lazy) ; **`ExercisesResultsView`** pour le shell liste/grille ; helpers **`lib/exercises/buildExercisePageFilters.ts`**, **`exercisePageToolbarLabels.ts`**, **`exercisesPageConstants.ts`**.
- **Inchangé** : clés React Query, invalidations, filtres / ordre / pagination, **`ExerciseCard`**, **`UnifiedExerciseGenerator`**, **`ExerciseModal`** (lazy), i18n.
- **Hors lot** : `app/exercises/interleaved/page.tsx`, nouveau gros hook métier, refonte cartes / générateur.
- **Tests** : `__tests__/unit/app/exercises/ExercisesPage.test.tsx`, `__tests__/unit/lib/exercises/buildExercisePageFilters.test.ts`.
- **Garde-fous** : budget LOC `app/exercises/page.tsx` réduit dans **`frontendGuardrails.ts`** (coque courte).
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (**P1-ARCH-05** résolu), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run __tests__/unit/app/exercises/ExercisesPage.test.tsx __tests__/unit/lib/exercises/buildExercisePageFilters.test.ts __tests__/unit/architecture/frontendGuardrails.test.ts`, `prettier --check` sur fichiers touchés.

### COMP-DIAGNOSTIC-01 (2026-04-11) - fermé

- **Refactor** : `frontend/components/diagnostic/DiagnosticSolver.tsx` = façade par phase ; **`DiagnosticIdleState`**, **`DiagnosticLoadingState`**, **`DiagnosticErrorState`**, **`DiagnosticResultsState`**, **`DiagnosticQuestionState`** ; **`DiagnosticSolverPrimitives.tsx`** (`DiagnosticFocusBoard`, `DiagnosticProgressBar`, **`DiagnosticScoreCard`**).
- **Inchangé** : **`useDiagnostic.ts`** (dont **`setTimeout(..., 1800)`**), props publiques **`DiagnosticSolverProps`**, i18n, CTA, **`MathText`** / **`GrowthMindsetHint`**, endpoints `/api/diagnostic/*`, `app/diagnostic/page.tsx`.
- **Tests** : `frontend/components/diagnostic/DiagnosticSolver.test.tsx` (idle, error, results, question, feedback, `onComplete`).
- **Doc** : `README_TECH.md`, `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (**P3-COMP-01** résolu), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run components/diagnostic/DiagnosticSolver.test.tsx`, `prettier --check` sur fichiers touchés.

### TEST-DIAGNOSTIC-HOOK-01 (2026-04-11) - fermé

- **Objectif** : couverture unitaire du hook critique **`frontend/hooks/useDiagnostic.ts`** (flux idle / loading / question / feedback / results / error, appels **`/api/diagnostic/start|question|answer|complete`**, délai **`1800`** ms avant finalisation quand **`session_complete`**).
- **Inchangé** : comportement métier du hook, signatures publiques, **`setTimeout(..., 1800)`**, UI diagnostic, seuils **`vitest.config.ts`**.
- **Tests** : **`frontend/hooks/useDiagnostic.test.ts`** — mock **`@/lib/api/client`**, **`vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] })`** sur la branche finale (éviter **`waitFor`** bloqué par timers entièrement fake) ; assertion **`setTimeout(..., 1800)`** via spy.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-04** avancé, pas clôture globale coverage), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useDiagnostic.test.ts`, `prettier --check` sur les fichiers touchés.

### TEST-SUBMIT-ANSWER-01 (2026-04-11) - fermé

- **Objectif** : couverture unitaire de **`frontend/hooks/useSubmitAnswer.ts`** (POST **`/api/exercises/{id}/attempt`**, **`trackFirstAttempt`**, invalidations / refetch React Query, toasts badges / progression / erreur).
- **Inchangé** : hook, clés **`queryKey`**, copy **`next-intl`**, analytics, seuils **`vitest.config.ts`**, **`useExerciseSolverController`**.
- **Tests** : **`frontend/hooks/useSubmitAnswer.test.ts`** — **`QueryClientProvider`**, mock **`api.post`**, **`sonner`**, **`trackFirstAttempt`**, **`useTranslations`** ; assertion **`refetchQueries`** explicite pour **`["completed-exercises"]`** distincte des refetch induits par **`invalidateQueries`** sur l’arbre de test.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-04** avancé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useSubmitAnswer.test.ts`, `prettier --check` sur les fichiers touchés.

### TEST-IRT-SCORES-01 (2026-04-11) - fermé

- **Objectif** : couverture unitaire de **`frontend/hooks/useIrtScores.ts`** (GET **`/api/diagnostic/status`**, scores directs, proxies **`mixte`** / **`fractions`**, fallback profil, seuil **`GRAND_MAITRE`**, **`has_completed`**).
- **Inchangé** : hook, règles IRT, **`useExerciseSolverController`**, seuils **`vitest.config.ts`**.
- **Tests** : **`frontend/hooks/useIrtScores.test.ts`** — **`QueryClientProvider`**, mock **`api.get`**, **`useAuth`** via **`vi.hoisted`** ; pas de snapshot ; co-localisation structurelle : lot **`ACTIF-03-USEIRT-COLOCATE-01`** (2026-04-12).
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-04** avancé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useIrtScores.test.ts`, `prettier --check` sur les fichiers touchés.

### TEST-AI-GENERATOR-01 (2026-04-11) - fermé

- **Objectif** : couverture unitaire de **`frontend/hooks/useAIExerciseGenerator.ts`** (auth, validations, **`postAiGenerationSse`** + **`consumeSseJsonEvents`**, dispatch exercice réel, toasts erreurs, **`invalidateQueries(["exercises"])`** après **100 ms**, cancel / unmount / garde **`isGenerating`**).
- **Inchangé** : hook, chemins SSE, délai **100 ms**, **`vitest.config.ts`**, UI générateur.
- **Tests** : **`frontend/hooks/useAIExerciseGenerator.test.ts`** — **`QueryClientProvider`**, mocks ciblés (**`postAiGenerationSse`**, **`consumeSseJsonEvents`**, **`useAuth`**, **`next/navigation`**, **`next-intl`**, **`sonner`**) ; **`beforeEach`** avec **`mockPost.mockReset()`** pour ne pas laisser d’implémentation **`mockImplementation`** résiduelle entre cas ; co-localisation structurelle : lot **`ACTIF-03-USEAI-COLOCATE-01`** (2026-04-12).
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-04** avancé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useAIExerciseGenerator.test.ts`, `prettier --check` sur les fichiers touchés.

### TEST-COLOCATE-PILOT-01 (2026-04-11) - fermé

- **Objectif** : premier pilote **`ACTIF-03`** — co-localiser **4** tests actifs auprès du code source, sans changer leur logique ni **`vitest.config.ts`**.
- **Fichiers** : **`components/badges/BadgeCard.test.tsx`**, **`components/diagnostic/DiagnosticSolver.test.tsx`**, **`hooks/useDiagnostic.test.ts`**, **`hooks/useSubmitAnswer.test.ts`** (suppression des doublons sous **`__tests__/unit/`**).
- **Inchangé** : assertions, mocks **`@/`**, comportement produit ; pas de migration de masse.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier (chemins **`vitest`** des lots **COMP-BADGECARD-01**, **COMP-DIAGNOSTIC-01**, **TEST-DIAGNOSTIC-HOOK-01**, **TEST-SUBMIT-ANSWER-01** alignés).
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run components/badges/BadgeCard.test.tsx components/diagnostic/DiagnosticSolver.test.tsx hooks/useDiagnostic.test.ts hooks/useSubmitAnswer.test.ts`, `prettier --check` sur les quatre fichiers co-localisés.

### ACTIF-01-TRUTH-01 (2026-04-11) - fermé

- **Objectif** : clôturer l’audit **[ACTIF-01]** sur les quatre pages signalées (docs, changelog, offline, contact) avec décision explicite par fichier et preuve code — pas de conversion forcée.
- **Implémentation** : **`frontend/app/docs/page.tsx`** → Server Component (`getTranslations`, suppression de `use client` ; animation hero via **`motion-safe:*`** à la place de `useAccessibleAnimation` sur ce bloc uniquement). **`changelog`**, **`offline`**, **`contact`** restent **`"use client"`** (framer-motion / router+navigator+window / formulaire contrôlé + mailto).
- **Doc** : `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md` (section ACTIF-01 + sprint A + tableau résolus), `README_TECH.md`, ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx prettier --check` sur les fichiers touchés (pas de test page-level dédié à `docs`).

### ACTIF-02-USERAVATAR-01 (2026-04-11) - fermé

- **Objectif** : premier sous-lot **[ACTIF-02]** — industrialiser **`frontend/components/ui/UserAvatar.tsx`** sans changement UX ni props.
- **Implémentation** : **`next/image`** avec **`width` / `height` / `sizes`** (pixels **28 / 40 / 64** selon **`sm` / `md` / `lg`**) lorsque **`resolveNextImageRemoteDelivery`** (`lib/utils/nextImageRemoteSource.ts`, délégué par **`userAvatarImageSource.ts`**) aligne l’URL sur **`images.remotePatterns`** de **`next.config.ts`** (chemins **`/`**, **`http://localhost`**, **`https://*.render.com`**, **`https://*.onrender.com`**) ; sinon **`<img>`** + **`eslint-disable`** ciblé (URL DB arbitraire hors liste). Ajout **`**.onrender.com`** dans **`next.config.ts`\*\* pour coller aux déploiements Render réels.
- **Tests** : **`frontend/lib/utils/nextImageRemoteSource.test.ts`**, **`frontend/lib/utils/userAvatarImageSource.test.ts`** (délégation).
- **Doc** : **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (ACTIF-02, D-02, sprint B, §5 résolus), **`README_TECH.md`**, ce fichier.
- **Vérifs** : **`npm run lint`**, **`npx tsc --noEmit`**, **`npx vitest run lib/utils/nextImageRemoteSource.test.ts lib/utils/userAvatarImageSource.test.ts`**, **`npx prettier --check`** sur les fichiers touchés.

### ACTIF-02-BADGEICON-01 (2026-04-11) - fermé

- **Objectif** : deuxième sous-lot **[ACTIF-02]** — supprimer le fallback DOM impératif sur **`BadgeIcon`** (`icon_url` HTTP) tout en gardant le rendu visuel.
- **Implémentation** : sous-composant **`BadgeIconRemoteHttp`** avec **`useState`** pour échec de chargement ; **`next/image`** ou **`<img>`** selon **`resolveNextImageRemoteDelivery`** (`lib/utils/nextImageRemoteSource.ts`) ; **`key={dbUrl}`** pour réinitialiser l’état si l’URL change.
- **Tests** : **`frontend/__tests__/unit/components/BadgeIcon.test.tsx`** (local mask, remote onrender → mock **`next/image`**, CDN → **`<img>`**, erreur → emoji, sans URL → emoji).
- **Doc** : **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (ACTIF-02, D-02, sprint B, §5), **`README_TECH.md`**, ce fichier.
- **Vérifs** : **`npm run lint`**, **`npx tsc --noEmit`**, **`npx vitest run __tests__/unit/components/BadgeIcon.test.tsx`**, **`npx prettier --check`** sur les fichiers touchés ; pas de changement **`next.config.ts`** dans ce lot.

### ACTIF-02-CHATMESSAGES-01 (2026-04-12) - fermé

- **Objectif** : dernier sous-lot **[ACTIF-02]** — trancher **`ChatMessagesView`** avec vérité terrain (pas de migration **`next/image`** forcée).
- **Décision** : **exception délibérée** **`<img>`** natif — `message.imageUrl` non contraint (SSE), **`blob:`** / **`data:`** possibles, layout **`max-h-64 w-full object-cover`** dépend des dimensions intrinsèques ; **`next/image`** exigerait tailles fictives ou conteneur **`fill`** non équivalent. Pas de changement **`nextImageRemoteSource.ts`** ni **`next.config.ts`**.
- **Implémentation** : commentaire **`eslint-disable`** renforcé in **`ChatMessagesView.tsx`**.
- **Tests** : **`frontend/components/chat/ChatMessagesView.test.tsx`** (loader + placeholder masqué, image seule, texte + image + **`mb-3`**, HTTPS hors allowlist, **`blob:`**, **`data:`**, KaTeX, rôle **`alert`** sur erreur, parité **`embedded`** / **`drawer`**).
- **Doc** : **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (§4 ~~ACTIF-02~~ fermé, §5, D-02, sprint B), **`README_TECH.md`**, ce fichier.
- **Vérifs** : **`npm run lint`**, **`npx tsc --noEmit`**, **`npx vitest run components/chat/ChatMessagesView.test.tsx`**, **`npx prettier --check`** sur les fichiers touchés ; pas de **`npm run build`** (pas de branche **`next/image`** produit).

### ACTIF-03-USEAUTH-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test critique **`useAuth`** auprès de **`frontend/hooks/useAuth.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useAuth.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useAuth.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, comportement produit, **`useAuth.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useAuth.test.ts`, `npx prettier --check hooks/useAuth.test.ts`.

### ACTIF-03-BUILDCSP-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`buildContentSecurityPolicy`** auprès de **`frontend/lib/security/buildContentSecurityPolicy.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher à l’utilitaire source ; chemin Git durable (évite **`__tests__/unit/lib/...`** fragile vs **`.gitignore`**).
- **Fichiers** : **`frontend/lib/security/buildContentSecurityPolicy.test.ts`** (déplacement depuis **`frontend/__tests__/unit/lib/security/buildContentSecurityPolicy.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, import **`@/lib/security/buildContentSecurityPolicy`**, **`buildContentSecurityPolicy.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run lib/security/buildContentSecurityPolicy.test.ts`, `npx prettier --check lib/security/buildContentSecurityPolicy.test.ts`.

### ACTIF-03-MIDDLEWARECSP-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`middlewareCsp`** auprès de **`frontend/lib/security/middlewareCsp.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher à l’utilitaire source ; alignement avec **`lib/security/buildContentSecurityPolicy.test.ts`**.
- **Fichiers** : **`frontend/lib/security/middlewareCsp.test.ts`** (déplacement depuis **`frontend/__tests__/unit/lib/security/middlewareCsp.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, imports **`@/lib/security/*`**, **`middlewareCsp.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run lib/security/middlewareCsp.test.ts`, `npx prettier --check lib/security/middlewareCsp.test.ts`.

### ACTIF-03-USEIRT-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useIrtScores`** auprès de **`frontend/hooks/useIrtScores.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source ; alignement avec **`hooks/useAuth.test.ts`**, **`useDiagnostic.test.ts`**, **`useSubmitAnswer.test.ts`**.
- **Fichiers** : **`frontend/hooks/useIrtScores.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useIrtScores.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useIrtScores.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useIrtScores.test.ts`, `npx prettier --check hooks/useIrtScores.test.ts`.

### ACTIF-03-USEAI-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useAIExerciseGenerator`** auprès de **`frontend/hooks/useAIExerciseGenerator.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useAIExerciseGenerator.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useAIExerciseGenerator.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useAIExerciseGenerator.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useAIExerciseGenerator.test.ts`, `npx prettier --check hooks/useAIExerciseGenerator.test.ts`.

### ACTIF-03-USESETTINGS-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useSettingsPageController`** auprès de **`frontend/hooks/useSettingsPageController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useSettingsPageController.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useSettingsPageController.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useSettingsPageController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useSettingsPageController.test.ts`, `npx prettier --check hooks/useSettingsPageController.test.ts`.

### ACTIF-03-USEBADGES-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useBadgesPageController`** auprès de **`frontend/hooks/useBadgesPageController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source (FFI-L12).
- **Fichiers** : **`frontend/hooks/useBadgesPageController.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useBadgesPageController.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useBadgesPageController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useBadgesPageController.test.ts`, `npx prettier --check hooks/useBadgesPageController.test.ts`.

### ACTIF-03-DASHBOARD-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useDashboardPageController`** auprès de **`frontend/hooks/useDashboardPageController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useDashboardPageController.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useDashboardPageController.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useDashboardPageController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useDashboardPageController.test.ts`, `npx prettier --check hooks/useDashboardPageController.test.ts`.

### ACTIF-03-CONTENTLIST-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useContentListPageController`** auprès de **`frontend/hooks/useContentListPageController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useContentListPageController.test.tsx`** (déplacement depuis **`frontend/__tests__/unit/hooks/useContentListPageController.test.tsx`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useContentListPageController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useContentListPageController.test.tsx`, `npx prettier --check hooks/useContentListPageController.test.tsx`.

### ACTIF-03-CHALLENGESOLVER-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useChallengeSolverController`** auprès de **`frontend/hooks/useChallengeSolverController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useChallengeSolverController.test.tsx`** (déplacement depuis **`frontend/__tests__/unit/hooks/useChallengeSolverController.test.tsx`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useChallengeSolverController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useChallengeSolverController.test.tsx`, `npx prettier --check hooks/useChallengeSolverController.test.tsx`.

### ACTIF-03-EXERCISESOLVER-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useExerciseSolverController`** auprès de **`frontend/hooks/useExerciseSolverController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/useExerciseSolverController.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useExerciseSolverController.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/`**, **`useExerciseSolverController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useExerciseSolverController.test.ts`, `npx prettier --check hooks/useExerciseSolverController.test.ts`.

### ACTIF-03-MICROHOOKS-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser **5** tests hooks légers sous **`frontend/hooks/`** sans réécrire la logique ni modifier **`vitest.config.ts`**, sans toucher aux hooks sources (dont **`useAccessibleAnimation`** implémenté sous **`lib/hooks/`**, test déplacé sous **`hooks/`** selon périmètre lot).
- **Fichiers** : **`useAdminContentPageController.test.ts`**, **`useChallengesStats.test.tsx`**, **`useChallengeTranslations.test.tsx`**, **`useRecommendationsReason.test.ts`**, **`useAccessibleAnimation.test.ts`** (depuis **`frontend/__tests__/unit/hooks/`** ; suppressions des anciens chemins).
- **Inchangé** : assertions, mocks **`@/`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useAdminContentPageController.test.ts hooks/useChallengesStats.test.tsx hooks/useChallengeTranslations.test.tsx hooks/useRecommendationsReason.test.ts hooks/useAccessibleAnimation.test.ts`, `npx prettier --check` sur les 5 fichiers.

### ACTIF-03-PROGRESS-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser **3** tests hooks progression / liste sous **`frontend/hooks/`** sans réécrire la logique ni modifier **`vitest.config.ts`**, sans toucher aux hooks sources.
- **Fichiers** : **`useCompletedItems.test.tsx`**, **`usePaginatedContent.test.tsx`**, **`useProgressTimeline.test.tsx`** (depuis **`frontend/__tests__/unit/hooks/`** ; suppressions des anciens chemins).
- **Inchangé** : assertions, mocks **`@/`** (**`@tanstack/react-query`**, **`api`**, **`localeStore`** selon fichiers).
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useCompletedItems.test.tsx hooks/usePaginatedContent.test.tsx hooks/useProgressTimeline.test.tsx`, `npx prettier --check` sur les 3 fichiers.

### ACTIF-03-USECHAT-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useChat`** auprès de **`frontend/hooks/chat/useChat.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source (lot borné, hook plus couplé que les micro-hooks).
- **Fichiers** : **`frontend/hooks/chat/useChat.test.tsx`** (déplacement depuis **`frontend/__tests__/unit/hooks/useChat.test.tsx`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`@/lib/api/chat`** (**`streamChat`**), **`useChat.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/chat/useChat.test.tsx`, `npx prettier --check hooks/chat/useChat.test.tsx`.

### ACTIF-03-GUESTCHATACCESS-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useGuestChatAccess`** auprès de **`frontend/hooks/chat/useGuestChatAccess.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source.
- **Fichiers** : **`frontend/hooks/chat/useGuestChatAccess.test.tsx`** (déplacement depuis **`frontend/__tests__/unit/hooks/chat/useGuestChatAccess.test.tsx`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, imports **`@/lib/chat/guestChatSession`**, **`useGuestChatAccess.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/chat/useGuestChatAccess.test.tsx`, `npx prettier --check hooks/chat/useGuestChatAccess.test.tsx`.

### ACTIF-03-USEPROFILE-COLOCATE-01 (2026-04-12) - fermé

- **Objectif** : co-localiser le test **`useProfilePageController`** auprès de **`frontend/hooks/useProfilePageController.ts`** sans réécrire la logique du test ni modifier **`vitest.config.ts`**, sans toucher au hook source ; dernier test hook sous **`__tests__/unit/hooks/`** — périmètre hooks historique **quasi soldé** (voir audit).
- **Fichiers** : **`frontend/hooks/useProfilePageController.test.ts`** (déplacement depuis **`frontend/__tests__/unit/hooks/useProfilePageController.test.ts`** ; suppression de l’ancien chemin).
- **Inchangé** : assertions, mocks **`useProfile`**, **`themeStore`**, **`useAgeGroupDisplay`**, **`useProfilePageController.ts`**.
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-03** avancé, **non** clôturé), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useProfilePageController.test.ts`, `npx prettier --check hooks/useProfilePageController.test.ts`.

### ACTIF-04-COVERAGE-01 (2026-04-12) - fermé

- **Objectif** : mesurer la couverture Vitest réelle du frontend puis remonter les **seuils** dans **`frontend/vitest.config.ts`** uniquement si la mesure le justifie, sans changer le code produit ni le périmètre **`coverage.include` / exclude**.
- **Mesure autoritative** : baseline **CI GitHub Actions frontend** (`ubuntu-latest`, Node **20**, `npx vitest --coverage --reporter=junit --outputFile=./junit.xml --run`) — agrégat **All files** : **44.57 %** stmts, **37.22 %** branches, **41.47 %** funcs, **45.68 %** lines.
- **Nuance** : les runs locaux Windows/Node 20 observés sur la machine de dev restent plus hauts (~**47.9 / 39.93 / 43.3 / 49.14**), mais ne servent plus de baseline tant qu’ils divergent de la CI.
- **Seuils** : **43 / 36 / 40 / 44** (**`floor(mesure CI %) − 1`** par axe ; anciens **39 / 33 / 37 / 40**).
- **Inchangé** : code applicatif ; **[ACTIF-04]** (audit) reste **ouvert** pour la suite progressive (nouveaux tests + nouvelle mesure avant tout bump suivant).
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`**, ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, **`npx vitest run --coverage`** (local) + reproduction exacte sous **Node 20** locale, `npx prettier --check vitest.config.ts`.

### ACTIF-06-ADMIN-USERS-01 (2026-04-12) - fermé

- **Objectif** : extraire **`useAdminUsersPageController`** depuis **`frontend/app/admin/users/page.tsx`** — état filtres / pagination / modales, handlers async, orchestration toasts, wiring **`useAdminUsers`** + **`useAuth`** ; page = coque JSX uniquement ; pas de changement UX intentionnel, pas de modification de **`useAdminUsers`** ni i18n.
- **Fichiers** : **`frontend/hooks/useAdminUsersPageController.ts`**, refactor **`frontend/app/admin/users/page.tsx`**, tests **`frontend/hooks/useAdminUsersPageController.test.tsx`**.
- **Inchangé** : contrat **`AdminUser`**, **`normalizeUserRole`**, clés toasts / messages, **`PAGE_SIZE`** (= **20**, exporté depuis le controller).
- **Doc** : **`README_TECH.md`**, **`docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`** (**ACTIF-06** avancé, **non** clôturé — reste **ai-monitoring**), ce fichier.
- **Vérifs** : `npm run lint`, `npx tsc --noEmit`, `npx vitest run hooks/useAdminUsersPageController.test.tsx __tests__/unit/app/admin/adminRoutePagesI18n.smoke.test.tsx`, `npx prettier --check` sur les fichiers touchés.

### RÃ¨gle de pilotage

- traiter la suite comme :
  - correctifs ciblÃ©s
  - dette qualitative mesurable
  - lots compacts et reviewables
- tout nouveau lot structurel frontend devra partir d'un nouveau constat terrain, pas d'une inertie documentaire
