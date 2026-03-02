# Architecture Frontend — Mathakine

> Dernière mise à jour : 22/02/2026  
> Validé contre le code source réel

---

## Stack technique

| Technologie | Usage | Version |
|---|---|---|
| **Next.js** | Framework (App Router) | 16.1.6 |
| **TypeScript** | Langage (strict mode) | 5.x |
| **Tailwind CSS** | Styling | v4 |
| **shadcn/ui** | Composants UI (Radix UI) | — |
| **TanStack Query** | Server state (cache API) | v5 |
| **Zustand** | Client state (thèmes, a11y, locale) | — |
| **Framer Motion** | Animations (avec garde-fous a11y) | — |
| **next-intl** | Internationalisation (FR/EN) | — |
| **Vitest** | Tests unitaires | — |
| **Playwright** | Tests E2E | — |

---

## Structure du projet

```
frontend/
├── app/                          # Next.js App Router
│   ├── admin/                    # Espace admin (rôle archiviste)
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
│   │   ├── challenges/           # generate-ai-stream
│   │   ├── exercises/            # generate-ai-stream
│   │   ├── chat/                 # stream (chatbot)
│   │   └── sentry-status/
│   ├── badges/page.tsx
│   ├── challenge/[id]/page.tsx
│   ├── challenges/page.tsx
│   ├── changelog/page.tsx
│   ├── dashboard/page.tsx
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
│   ├── spatial/                  # SpatialBackground, Starfield, Planet, Particles, DinoFloating
│   ├── theme/                    # ThemeSelector, ThemeSelectorCompact
│   └── ui/                       # shadcn/ui (Button, Card, Dialog, Input, Select…)
│
├── hooks/                        # 35 hooks React Query
│   ├── useAuth.ts                # Authentification (login, logout, register)
│   ├── useExercise(s).ts         # Exercices (liste, détail, pagination)
│   ├── useChallenge(s).ts        # Défis logiques
│   ├── useBadges.ts / useBadgesProgress.ts
│   ├── useUserStats.ts / useProgressStats.ts
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
│   ├── api/client.ts             # Client HTTP (fetch + CSRF + auth)
│   ├── stores/                   # Zustand stores (accessibilityStore, themeStore, localeStore)
│   ├── hooks/                    # Hooks utilitaires (useAccessibleAnimation, useKeyboardNavigation)
│   ├── utils/cn.ts               # clsx + tailwind-merge (source de vérité)
│   ├── utils.ts                  # Re-export de cn (compatibilité)
│   └── validations/              # Schémas de validation (dashboard, exercises…)
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
npm run type-check       # tsc --noEmit

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
NEXT_PUBLIC_API_URL=http://localhost:8000   # Dev
# NEXT_PUBLIC_API_URL=https://mathakine-alpha.onrender.com  # Prod
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
