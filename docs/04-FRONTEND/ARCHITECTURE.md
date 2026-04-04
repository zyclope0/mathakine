# Architecture Frontend — Mathakine

> Dernière mise à jour : 04/04/2026  
> Validé contre le code source réel (post-audit industrialisation)

---

## Références

- [HOOKS_CATALOGUE.md](HOOKS_CATALOGUE.md) — catalogue des 41 hooks React (rôle, dépendances, couverture tests)
- [COMPONENTS_CATALOGUE.md](COMPONENTS_CATALOGUE.md) — 126 composants React (catégories, rôles, conventions)
- [API_ROUTES.md](API_ROUTES.md) — 7 routes API Next.js (proxy, auth, SSE)

---

## Stack technique

| Technologie        | Usage                               | Version |
| ------------------ | ----------------------------------- | ------- |
| **Next.js**        | Framework (App Router)              | 16.1.6  |
| **TypeScript**     | Langage (strict mode)               | 5.x     |
| **Tailwind CSS**   | Styling                             | v4      |
| **shadcn/ui**      | Composants UI (Radix UI)            | —       |
| **TanStack Query** | Server state (cache API)            | v5      |
| **Zustand**        | Client state (thèmes, a11y, locale) | —       |
| **Framer Motion**  | Animations (avec garde-fous a11y)   | —       |
| **next-intl**      | Internationalisation (FR/EN)        | —       |
| **Vitest**         | Tests unitaires                     | —       |
| **Playwright**     | Tests E2E                           | —       |

---

## Structure du projet

```
frontend/
├── app/                          # Next.js App Router
│   ├── admin/                    # Espace admin (role canonique admin)
│   │   ├── layout.tsx            # Layout admin + navigation latérale
│   │   ├── page.tsx              # Vue d'ensemble admin
│   │   ├── analytics/            # Analytics EdTech
│   │   ├── ai-monitoring/        # Monitoring IA (tokens, qualité)
│   │   ├── audit-log/            # Journal d'audit
│   │   ├── config/               # Paramètres plateforme
│   │   ├── content/              # Gestion contenu
│   │   ├── feedback/             # Retours utilisateurs
│   │   ├── moderation/           # Modération IA
│   │   └── users/                # Gestion utilisateurs
│   ├── api/                      # API Routes Next.js (proxy backend)
│   │   ├── auth/                 # sync-cookie, check-cookie
│   │   ├── challenges/           # generate-ai-stream (POST JSON → proxy SSE backend)
│   │   ├── exercises/            # generate-ai-stream (POST JSON → proxy SSE backend)
│   │   ├── chat/                 # stream (chatbot)
│   │   └── sentry-status/
│   ├── badges/page.tsx
│   ├── challenge/[id]/page.tsx
│   ├── challenges/page.tsx
│   ├── changelog/page.tsx
│   ├── dashboard/page.tsx        # Surface analytique principale adulte, entree secondaire pour apprenant
│   ├── home-learner/page.tsx     # Surface apprenant dediee et point d'entree par defaut (NI-13)
│   ├── exercises/page.tsx + [id]/page.tsx
│   ├── forgot-password/page.tsx
│   ├── leaderboard/page.tsx
│   ├── login/page.tsx
│   ├── offline/page.tsx
│   ├── onboarding/page.tsx
│   ├── profile/page.tsx
│   ├── register/page.tsx
│   ├── reset-password/page.tsx
│   ├── settings/page.tsx
│   ├── verify-email/page.tsx
│   ├── layout.tsx                # Layout racine
│   ├── page.tsx                  # Accueil
│   ├── error.tsx / global-error.tsx / not-found.tsx
│   └── globals.css               # Styles globaux + variables thèmes CSS
│
├── components/
│   ├── accessibility/            # AccessibilityToolbar, WCAGAudit (dev)
│   ├── admin/                    # Modales CRUD (Exercise, Challenge, Badge)
│   ├── auth/                     # ProtectedRoute, EmailVerification
│   ├── badges/                   # BadgeCard, BadgeGrid
│   ├── challenges/               # ChallengeCard, ChallengeSolver, ChallengeModal
│   │   └── visualizations/       # Renderers (Pattern, Sequence, Visual, Deduction…)
│   ├── dashboard/                # Widgets dashboard (Stats, Recommendations, Level…)
│   ├── exercises/                # ExerciseCard, ExerciseSolver, AIGenerator
│   ├── feedback/                 # FeedbackFab, FeedbackModal
│   ├── home/                     # Hero, QuickStart, features section
│   ├── layout/                   # PageLayout, PageHeader, PageSection, PageGrid,
│   │                             # EmptyState, LoadingState, Header, Footer, PageTransition
│   ├── locale/                   # LanguageSelector, LocaleInitializer
│   ├── providers/                # QueryProvider, ThemeProvider, IntlProvider
│   ├── pwa/                      # InstallPrompt
│   ├── shared/                   # Composants partagés cross-domaine
│   │   └── AIGeneratorBase.tsx   # Base UI partagée (exercises + challenges AIGenerator)
│   ├── spatial/                  # SpatialBackground, Starfield, Planet, Particles, DinoFloating
│   ├── theme/                    # ThemeSelector, ThemeSelectorCompact
│   └── ui/                       # shadcn/ui (Button, Card, Dialog, Input, Select…)
│
├── hooks/                        # 41 hooks React (majoritairement React Query)
│   ├── chat/                     # useChat, useChatAutoScroll (chatbot home, lot IA13b)
│   ├── useAuth.ts                # Authentification (login, logout, register)
│   ├── useExercise(s).ts         # Exercices (liste, détail, pagination)
│   ├── useChallenge(s).ts        # Défis logiques
│   ├── useBadges.ts / useBadgesProgress.ts
│   ├── useUserStats.ts / useProgressStats.ts / useNextReview.ts
│   ├── useRecommendations.ts
│   ├── useLeaderboard.ts
│   ├── useChat.ts
│   ├── useProfile.ts / useSettings.ts
│   ├── useAcademyStats.ts
│   ├── useSubmitAnswer.ts / useCompletedItems.ts
│   ├── usePaginatedContent.ts
│   ├── useChallengeTranslations.ts / useChallengesProgress.ts
│   └── useAdmin*.ts              # 12 hooks admin (Overview, Users, Exercises,
│                                 # Challenges, Badges, Reports, Moderation,
│                                 # Config, AuditLog, Feedback, EdTechAnalytics,
│                                 # AiStats)
│
├── lib/
│   ├── chat/                     # Types + mapping historique API chat (`README.md`)
│   ├── api/client.ts             # Client HTTP (fetch + CSRF + auth)
│   ├── constants/                # Constantes centralisées (exercises, challenges, badges)
│   ├── stores/                   # Zustand stores (accessibilityStore, themeStore, localeStore)
│   ├── spacedReviewSession.ts    # handoff review-safe entre dashboard F04 et solver
│   ├── hooks/                    # Hooks utilitaires (useAccessibleAnimation, useKeyboardNavigation)
│   ├── utils/
│   │   ├── cn.ts                 # clsx + tailwind-merge (source de vérité interne)
│   │   └── format.ts             # Utilitaires formatage (hasAiTag, formatSuccessRate)
│   ├── utils.ts                  # Re-export de cn — TOUJOURS importer depuis @/lib/utils
│   └── validation/               # Schémas de validation (dashboard, exercise, next review F04…)
│
├── messages/
│   ├── fr.json                   # Traductions françaises
│   └── en.json                   # Traductions anglaises
│
├── types/                        # Types TypeScript partagés
├── scripts/i18n/                 # Scripts vérification traductions
├── public/
│   ├── manifest.json             # PWA manifest
│   ├── icons/                    # Icônes PWA (à créer par designer)
│   └── sw.js                     # Service Worker (généré au build)
│
├── next.config.ts                # Config Next.js + PWA
├── tailwind.config.js            # Config Tailwind
├── tsconfig.json                 # TypeScript strict
└── package.json
```

---

## Patterns architecturaux

### Server vs Client components

- **Défaut** : Server Components dans App Router
- **`"use client"`** : Requis pour interactivité (état, hooks, events)
- **Hooks** : Toujours `"use client"`
- Les pages admin utilisent toutes `"use client"` (données dynamiques)

### State management

```
┌─────────────────────────────────────────────┐
│ TanStack Query v5 — Server state (API data) │
│  cache, invalidation, pagination, mutations  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Zustand — Client state (persisté localStorage)│
│  thème, locale, préférences accessibilité    │
└─────────────────────────────────────────────┘
```

### Client API

`lib/api/client.ts` — wrapper centralisé :

- Injection automatique du token Bearer (cookie → header)
- CSRF token (`X-CSRF-Token` depuis cookie `csrf_token`)
- Gestion d'erreurs typées (`ApiClientError`)
- Refresh automatique du token expiré

### Routing API (proxy)

Les routes sensibles passent par les API Routes Next.js (`app/api/`) pour :

- Éviter d'exposer l'URL backend en CORS direct
- Gérer le streaming SSE (génération IA) côté serveur
- Synchroniser les cookies entre domaines (cross-domain prod)

Le **chat discussionnel** (`lib/api/chat.ts`) appelle en navigateur `POST /api/chat/stream` (même origine), comme les flux génération IA — sans réutiliser leurs dispatchers d’événements (schéma différent). Détail : `lib/chat/README.md`.

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
- `ProtectedRoute` porte les gardes de role avec `allowedRoles`
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
# Développement
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
npm run i18n:check       # Cohérence clés FR/EN
npm run i18n:extract     # Détecter strings hardcodées
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

## Déploiement (Render.com)

- **Build** : `cd frontend && npm install && npm run build`
- **Start** : `cd frontend && npm start`
- **HTTPS** : Fourni automatiquement par Render
- **PWA** : Service Worker généré au build (désactivé en dev)

---

## Références

- [Design System](DESIGN_SYSTEM.md) — composants layout standardisés
- [Accessibilité](ACCESSIBILITY.md) — WCAG 2.1 AAA, 5 modes
- [Animations](ANIMATIONS.md) — composants spatiaux
- [PWA](PWA.md) — configuration Progressive Web App
- [i18n](../02-FEATURES/I18N.md) — internationalisation next-intl
- [Thèmes](../02-FEATURES/THEMES.md) — 7 thèmes, themeStore
