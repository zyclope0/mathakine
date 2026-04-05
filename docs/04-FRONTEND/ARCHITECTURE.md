# Architecture Frontend â€” Mathakine

> DerniÃ¨re mise Ã  jour : 05/04/2026  
> ValidÃ© contre le code source rÃ©el (post-audit industrialisation)

---

## RÃ©fÃ©rences

- [HOOKS_CATALOGUE.md](HOOKS_CATALOGUE.md) â€” catalogue des 43 hooks React (rÃ´le, dÃ©pendances, couverture tests)
- [COMPONENTS_CATALOGUE.md](COMPONENTS_CATALOGUE.md) â€” 136 composants React (catÃ©gories, rÃ´les, conventions)
- [API_ROUTES.md](API_ROUTES.md) â€” routes Next.js frontend et proxys backend
- [UX_SURFACES.md](UX_SURFACES.md) - surfaces apprenant/adulte, navigation et boundary NI-13

---

## Stack technique

| Technologie        | Usage                                | Version |
| ------------------ | ------------------------------------ | ------- |
| **Next.js**        | Framework (App Router)               | 16.1.6  |
| **TypeScript**     | Langage (strict mode)                | 5.x     |
| **Tailwind CSS**   | Styling                              | v4      |
| **shadcn/ui**      | Composants UI (Radix UI)             | â€”     |
| **TanStack Query** | Server state (cache API)             | v5      |
| **Zustand**        | Client state (thÃ¨mes, a11y, locale) | â€”     |
| **Framer Motion**  | Animations (avec garde-fous a11y)    | â€”     |
| **next-intl**      | Internationalisation (FR/EN)         | â€”     |
| **Vitest**         | Tests unitaires                      | â€”     |
| **Playwright**     | Tests E2E                            | â€”     |

---

## Structure du projet

```
frontend/
â”œâ”€â”€ app/                          # Next.js App Router
â”‚   â”œâ”€â”€ admin/                    # Espace admin (role canonique admin)
â”‚   â”‚   â”œâ”€â”€ layout.tsx            # Layout admin + navigation latÃ©rale
â”‚   â”‚   â”œâ”€â”€ page.tsx              # Vue d'ensemble admin
â”‚   â”‚   â”œâ”€â”€ analytics/            # Analytics EdTech
â”‚   â”‚   â”œâ”€â”€ ai-monitoring/        # Monitoring IA (tokens, qualitÃ©)
â”‚   â”‚   â”œâ”€â”€ audit-log/            # Journal d'audit
â”‚   â”‚   â”œâ”€â”€ config/               # ParamÃ¨tres plateforme
â”‚   â”‚   â”œâ”€â”€ content/              # Gestion contenu
â”‚   â”‚   â”œâ”€â”€ feedback/             # Retours utilisateurs
â”‚   â”‚   â”œâ”€â”€ moderation/           # ModÃ©ration IA
â”‚   â”‚   â””â”€â”€ users/                # Gestion utilisateurs
â”‚   â”œâ”€â”€ api/                      # API Routes Next.js (proxy backend)
â”‚   â”‚   â”œâ”€â”€ auth/                 # sync-cookie, check-cookie
â”‚   â”‚   â”œâ”€â”€ challenges/           # generate-ai-stream (POST JSON â†’ proxy SSE backend)
â”‚   â”‚   â”œâ”€â”€ exercises/            # generate-ai-stream (POST JSON â†’ proxy SSE backend)
â”‚   â”‚   â”œâ”€â”€ chat/                 # stream (chatbot)
â”‚   â”‚   â””â”€â”€ sentry-status/
â”‚   â”œâ”€â”€ badges/page.tsx
â”‚   â”œâ”€â”€ challenge/[id]/page.tsx
â”‚   â”œâ”€â”€ challenges/page.tsx
â”‚   â”œâ”€â”€ changelog/page.tsx
â”‚   â”œâ”€â”€ dashboard/page.tsx        # Surface analytique principale adulte, entree secondaire pour apprenant
â”‚   â”œâ”€â”€ home-learner/page.tsx     # Surface apprenant dediee et point d'entree par defaut (NI-13)
â”‚   â”œâ”€â”€ exercises/page.tsx + [id]/page.tsx
â”‚   â”œâ”€â”€ forgot-password/page.tsx
â”‚   â”œâ”€â”€ leaderboard/page.tsx
â”‚   â”œâ”€â”€ login/page.tsx
â”‚   â”œâ”€â”€ offline/page.tsx
â”‚   â”œâ”€â”€ onboarding/page.tsx
â”‚   â”œâ”€â”€ profile/page.tsx
â”‚   â”œâ”€â”€ register/page.tsx
â”‚   â”œâ”€â”€ reset-password/page.tsx
â”‚   â”œâ”€â”€ settings/page.tsx
â”‚   â”œâ”€â”€ verify-email/page.tsx
â”‚   â”œâ”€â”€ layout.tsx                # Layout racine
â”‚   â”œâ”€â”€ page.tsx                  # Accueil
â”‚   â”œâ”€â”€ error.tsx / global-error.tsx / not-found.tsx
â”‚   â””â”€â”€ globals.css               # Styles globaux + variables thÃ¨mes CSS
â”‚
â”œâ”€â”€ components/
â”‚   â”œâ”€â”€ accessibility/            # AccessibilityToolbar, WCAGAudit (dev)
â”‚   â”œâ”€â”€ admin/                    # Modales CRUD (Exercise, Challenge, Badge)
â”‚   â”œâ”€â”€ auth/                     # ProtectedRoute, EmailVerification
â”‚   â”œâ”€â”€ badges/                   # BadgeCard, BadgeGrid
â”‚   â”œâ”€â”€ challenges/               # ChallengeCard, ChallengeSolver, ChallengeModal
â”‚   â”‚   â””â”€â”€ visualizations/       # Renderers (Pattern, Sequence, Visual, Deductionâ€¦)
â”‚   â”œâ”€â”€ dashboard/                # Widgets dashboard (Stats, Recommendations, Levelâ€¦)
â”‚   â”œâ”€â”€ exercises/                # ExerciseCard, ExerciseSolver, AIGenerator
â”‚   â”œâ”€â”€ feedback/                 # FeedbackFab, FeedbackModal
â”‚   â”œâ”€â”€ home/                     # Hero, QuickStart, features section
â”‚   â”œâ”€â”€ layout/                   # PageLayout, PageHeader, PageSection, PageGrid,
â”‚   â”‚                             # EmptyState, LoadingState, Header, Footer, PageTransition
â”‚   â”œâ”€â”€ locale/                   # LanguageSelector, LocaleInitializer
â”‚   â”œâ”€â”€ providers/                # QueryProvider, ThemeProvider, IntlProvider
â”‚   â”œâ”€â”€ pwa/                      # InstallPrompt
â”‚   â”œâ”€â”€ shared/                   # Composants partagÃ©s cross-domaine
â”‚   â”‚   â””â”€â”€ AIGeneratorBase.tsx   # Base UI partagÃ©e (exercises + challenges AIGenerator)
â”‚   â”œâ”€â”€ spatial/                  # SpatialBackground, Starfield, Planet, Particles, DinoFloating, UnicornFloating
â”‚   â”œâ”€â”€ theme/                    # ThemeSelectorCompact, DarkModeToggle
â”‚   â””â”€â”€ ui/                       # shadcn/ui (Button, Card, Dialog, Input, Selectâ€¦)
â”‚
â”œâ”€â”€ hooks/                        # 43 hooks React (majoritairement React Query)
â”‚   â”œâ”€â”€ chat/                     # useChat, useChatAutoScroll (chatbot home, lot IA13b)
â”‚   â”œâ”€â”€ useAuth.ts                # Authentification (login, logout, register)
â”‚   â”œâ”€â”€ useExercise(s).ts         # Exercices (liste, dÃ©tail, pagination)
â”‚   â”œâ”€â”€ useChallenge(s).ts        # DÃ©fis logiques
â”‚   â”œâ”€â”€ useBadges.ts / useBadgesProgress.ts
â”‚   â”œâ”€â”€ useUserStats.ts / useProgressStats.ts / useNextReview.ts
â”‚   â”œâ”€â”€ useRecommendations.ts
â”‚   â”œâ”€â”€ useLeaderboard.ts
â”‚   â”œâ”€â”€ useChat.ts
â”‚   â”œâ”€â”€ useProfile.ts / useSettings.ts
â”‚   â”œâ”€â”€ useAcademyStats.ts
â”‚   â”œâ”€â”€ useSubmitAnswer.ts / useCompletedItems.ts
â”‚   â”œâ”€â”€ usePaginatedContent.ts
â”‚   â”œâ”€â”€ useChallengeTranslations.ts / useChallengesProgress.ts
â”‚   â””â”€â”€ useAdmin*.ts              # 12 hooks admin (Overview, Users, Exercises,
â”‚                                 # Challenges, Badges, Reports, Moderation,
â”‚                                 # Config, AuditLog, Feedback, EdTechAnalytics,
â”‚                                 # AiStats)
â”‚
â”œâ”€â”€ lib/
â”‚   â”œâ”€â”€ chat/                     # Types + mapping historique API chat (`README.md`)
â”‚   â”œâ”€â”€ api/client.ts             # Client HTTP (fetch + CSRF + auth)
â”‚   â”œâ”€â”€ constants/                # Constantes centralisÃ©es (exercises, challenges, badges)
â”‚   â”œâ”€â”€ stores/                   # Zustand stores (accessibilityStore, themeStore, localeStore)
â”‚   â”œâ”€â”€ spacedReviewSession.ts    # handoff review-safe entre dashboard F04 et solver
â”‚   â”œâ”€â”€ hooks/                    # Hooks utilitaires (useAccessibleAnimation, useKeyboardNavigation)
â”‚   â”œâ”€â”€ utils/
â”‚   â”‚   â”œâ”€â”€ cn.ts                 # clsx + tailwind-merge (source de vÃ©ritÃ© interne)
â”‚   â”‚   â””â”€â”€ format.ts             # Utilitaires formatage (hasAiTag, formatSuccessRate)
â”‚   â”œâ”€â”€ utils.ts                  # Re-export de cn â€” TOUJOURS importer depuis @/lib/utils
â”‚   â””â”€â”€ validation/               # SchÃ©mas de validation (dashboard, exercise, next review F04â€¦)
â”‚
â”œâ”€â”€ messages/
â”‚   â”œâ”€â”€ fr.json                   # Traductions franÃ§aises
â”‚   â””â”€â”€ en.json                   # Traductions anglaises
â”‚
â”œâ”€â”€ types/                        # Types TypeScript partagÃ©s
â”œâ”€â”€ scripts/i18n/                 # Scripts vÃ©rification traductions
â”œâ”€â”€ public/
â”‚   â”œâ”€â”€ manifest.json             # PWA manifest
â”‚   â”œâ”€â”€ icons/                    # IcÃ´nes PWA (Ã  crÃ©er par designer)
â”‚   â””â”€â”€ sw.js                     # Service Worker (gÃ©nÃ©rÃ© au build)
â”‚
â”œâ”€â”€ next.config.ts                # Config Next.js + PWA
â”œâ”€â”€ tailwind.config.js            # Config Tailwind
â”œâ”€â”€ tsconfig.json                 # TypeScript strict
â””â”€â”€ package.json
```

---

## Patterns architecturaux

### Server vs Client components

- **DÃ©faut** : Server Components dans App Router
- **`"use client"`** : Requis pour interactivitÃ© (Ã©tat, hooks, events)
- **Hooks** : Toujours `"use client"`
- Les pages admin utilisent toutes `"use client"` (donnÃ©es dynamiques)

### State management

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ TanStack Query v5 â€” Server state (API data) â”‚
â”‚  cache, invalidation, pagination, mutations  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Zustand â€” Client state (persistÃ© localStorage)â”‚
â”‚  thÃ¨me, locale, prÃ©fÃ©rences accessibilitÃ©    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Client API

`lib/api/client.ts` â€” wrapper centralisÃ© :

- Injection automatique du token Bearer (cookie â†’ header)
- CSRF token (`X-CSRF-Token` depuis cookie `csrf_token`)
- Gestion d'erreurs typÃ©es (`ApiClientError`)
- Refresh automatique du token expirÃ©

### Routing API (proxy)

Les routes sensibles passent par les API Routes Next.js (`app/api/`) pour :

- Ã‰viter d'exposer l'URL backend en CORS direct
- GÃ©rer le streaming SSE (gÃ©nÃ©ration IA) cÃ´tÃ© serveur
- Synchroniser les cookies entre domaines (cross-domain prod)

Le **chat discussionnel** (`lib/api/chat.ts`) appelle en navigateur `POST /api/chat/stream` (mÃªme origine), comme les flux gÃ©nÃ©ration IA â€” sans rÃ©utiliser leurs dispatchers dâ€™Ã©vÃ©nements (schÃ©ma diffÃ©rent). DÃ©tail : `lib/chat/README.md`.

La resolution de l'URL backend pour ces proxies est centralisee dans `lib/api/backendUrl.ts` :

- priorite `NEXT_PUBLIC_API_BASE_URL`
- fallback legacy `NEXT_PUBLIC_API_URL`
- fallback `http://localhost:10000` en developpement uniquement
- en production : erreur explicite si l'URL est absente, mal formee ou locale (`localhost`, `127.0.0.1`, `::1`)

Les handlers de routes Next.js sont maintenant couverts par des tests dedies (`frontend/__tests__/unit/app/api/...`) :

- succes et erreur JSON sur `/api/chat`
- succes SSE et garde config invalide sur `/api/chat/stream`
- succes SSE, refus auth/cookie, et propagation `!ok` sur `/api/exercises/generate-ai-stream`
- idem pour `/api/challenges/generate-ai-stream`

### Convention SSE IA

- `exercises_ai` : `status`, `exercise`, `error`, `done`
- `challenges_ai` : `status`, `warning`, `challenge`, `error`, `done`
- `assistant_chat` : `status`, `chunk`, `image`, `error`, `done`

Pour les exercices, `done` est maintenant emis sur les fins de flux controlees :

- succes nominal
- echec validation metier deja transforme en `error`
- echec persistance deja transforme en `error`

Les exceptions top-level non recuperees restent une fin `error` sans `done`, comme pour les defis.

### Echecs auth / CSRF generation IA

Le client partage `frontend/lib/ai/generation/postAiGenerationSse.ts` execute maintenant un preflight et un mapping d'erreurs stables avant le dispatch SSE :

- `csrf_token_missing`
- `http_401`
- `http_403`
- `http_backend`

Les hooks `useAIExerciseGenerator` et `useAIChallengeGenerator` convertissent ces erreurs en toasts i18n explicites sans exposer de details techniques bruts.

### Boundary de roles et navigation

- Le frontend raisonne sur des roles canoniques :
  - `apprenant`
  - `enseignant`
  - `moderateur`
  - `admin`
- La source de verite frontend est `lib/auth/userRoles.ts`
- `frontend/proxy.ts` porte le premier niveau de boundary serveur sur `/home-learner`, `/dashboard` et `/admin`
- `ProtectedRoute` garde les memes regles comme fallback client avec `allowedRoles`
- `NI-13` impose :
- `/home-learner` comme point d'entree par defaut pour `apprenant`
- `/dashboard` comme surface analytique normale pour les roles adultes
- `/dashboard` peut rester accessible a `apprenant` via une entree discrete du menu profil, sans reprendre le role de home principale
- Les anciens noms Star Wars restent hors de la logique active, sauf compatibilite backend/DB

### F04 review flow

Le flow F04 n'introduit pas de second solver. Il recompose des seams existants :

- `SpacedRepetitionSummaryWidget` expose le CTA `Reviser maintenant`
- `useNextReview.ts` lit `GET /api/users/me/reviews/next`
- `spacedReviewSession.ts` conserve temporairement la prochaine carte review-safe
- `ExerciseSolver.tsx` rehydrate ce payload en `?session=spaced-review`

Contrainte produit importante :

- avant soumission, le flow F04 ne doit jamais recharger un payload exercice classique contenant `correct_answer`, `hint` ou `explanation`
- apres soumission, l'explication peut etre affichee comme feedback pedagogique

---

## Configuration TypeScript (strict)

```json
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "noImplicitOverride": true,
  "exactOptionalPropertyTypes": true
}
```

---

## Scripts disponibles

```bash
# DÃ©veloppement
npm run dev              # Serveur dev (Turbopack)
npm run build            # Build production
npm start                # Serveur production
npm run lint             # ESLint
npm run format           # Prettier --write
npm run format:check     # Prettier --check (CI)
npx tsc --noEmit         # verification TypeScript stricte

# Tests
npm run test             # Vitest (unitaires)
npm run test:coverage    # Vitest + coverage
npm run test:e2e         # Playwright (E2E)

# i18n
npm run i18n:check       # CohÃ©rence clÃ©s FR/EN
npm run i18n:extract     # DÃ©tecter strings hardcodÃ©es
npm run i18n:validate    # Valider structure JSON
```

---

## Variables d'environnement

```env
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000   # Dev (API Starlette)
# NEXT_PUBLIC_API_BASE_URL=https://mathakine-alpha.onrender.com  # Prod
```

---

## DÃ©ploiement (Render.com)

- **Build** : `cd frontend && npm install && npm run build`
- **Start** : `cd frontend && npm start`
- **HTTPS** : Fourni automatiquement par Render
- **PWA** : Service Worker gÃ©nÃ©rÃ© au build (dÃ©sactivÃ© en dev)

---

## RÃ©fÃ©rences

- [Design System](DESIGN_SYSTEM.md) â€” composants layout standardisÃ©s
- [AccessibilitÃ©](ACCESSIBILITY.md) â€” WCAG 2.1 AAA, 5 modes
- [Animations](ANIMATIONS.md) â€” composants spatiaux
- [PWA](PWA.md) â€” configuration Progressive Web App
- [i18n](../02-FEATURES/I18N.md) â€” internationalisation next-intl
- [UX Surfaces](UX_SURFACES.md) - home learner, dashboard, roles et boundaries
