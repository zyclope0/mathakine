# Audit Frontend â€” Industrialisation, Design System & UX Premium

**Date :** 03/03/2026
**Type :** Audit exhaustif (Architecture, DRY, Design System, UX EdTech, QualitÃ© visuelle, AccessibilitÃ©)
**PÃ©rimÃ¨tre :** photographie historique `frontend/` â€” 101 composants, 32 hooks, 7 thÃ¨mes, ~15 000 lignes TSX
**MÃ©thode :** Inspection systÃ©matique composant par composant, analyse cross-cutting des patterns
**Statut :** âœ… AUDIT HISTORIQUE TERMINÃ‰ (03/03/2026) â€” ne plus utiliser ce fichier comme plan d'exÃ©cution actif

**ComplÃ©mentaire Ã  :** [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md) (backend â€” terminÃ©)

> **Mise Ã  jour 2026-04-06**
> Ce document reste utile comme photographie de la dette initiale, mais il ne doit plus etre
> utilise comme plan d'execution actif.
>
> Sources de verite actuelles :
>
> 1. [D:\\Mathakine\\.claude\\session-plan.md](../../.claude/session-plan.md)
> 2. [AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md](./AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md)
>
> Verite terrain actuelle :
>
> - `FFI-L1` a `FFI-L12` sont livres
> - `NI-13` est structurel cote serveur + client (`proxy.ts` + `ProtectedRoute`)
> - le tree frontend courant est a `158` composants, `49` hooks et `8` themes visibles
> - la duplication AIGenerator brute n'est plus le seam principal
> - la coherence end-user des defis (`challenge_type` vs `response_mode`) reste un **sidecar produit** documente dans `ROADMAP_FONCTIONNALITES.md` (`F44`), hors sequence FFI active
>
> Seams architecture encore prioritaires :
>
> - `app/settings/page.tsx`
> - `app/admin/content/page.tsx`
> - `components/profile/ProfileLearningPreferencesSection.tsx`
> - `ChallengeSolverCommandBar.tsx`
> - `Header.tsx`
> - la plateforme shared de listes contenu
>
> Ordre actif recommande :
> `FFI-L13` modulariser `settings`,
> `FFI-L14` decouper `admin/content`,
> `FFI-L15` standardiser la plateforme content-list,
> `FFI-L16` split shell/navigation,
> `FFI-L17` garde-fous architecture.
>
> Le detail de cet audit conserve volontairement la photographie du `03/03/2026`.
> Plusieurs constats du corps du document sont donc des **constats d'origine** et non
> des verites terrain encore actives. Pour l'execution courante, suivre le `session-plan`
> puis l'audit de standardisation.

---

## Sommaire

1. [RÃ©sumÃ© exÃ©cutif](#1-rÃ©sumÃ©-exÃ©cutif)
2. [Axe 1 â€” Architecture, Code QualitÃ© & DRY](#2-axe-1--architecture-code-qualitÃ©--dry)
3. [Axe 2 â€” ThÃ¨mes & Design System](#3-axe-2--thÃ¨mes--design-system)
4. [Axe 3 â€” UI/UX & Best Practices EdTech](#4-axe-3--uiux--best-practices-edtech)
5. [Axe 4 â€” QualitÃ© Graphique & Rendu Premium](#5-axe-4--qualitÃ©-graphique--rendu-premium)
6. [Axe 5 â€” AccessibilitÃ© & Performances](#6-axe-5--accessibilitÃ©--performances)
7. [Plan d'implÃ©mentation priorisÃ©](#7-plan-dimplÃ©mentation-priorisÃ©)
8. [Matrice rÃ©capitulative](#8-matrice-rÃ©capitulative)

---

## 1. RÃ©sumÃ© exÃ©cutif

| Axe                     | ðŸ”´ Critical | ðŸŸ¡ AmÃ©liorations | ðŸŸ¢ Acquis | Total  |
| ----------------------- | ------------- | ------------------- | ----------- | ------ |
| Architecture & DRY      | 5             | 5                   | 8           | **18** |
| ThÃ¨mes & Design System | 3             | 3                   | 3           | **9**  |
| UI/UX EdTech            | 2             | 4                   | 5           | **11** |
| QualitÃ© visuelle       | 4             | 4                   | 4           | **12** |
| AccessibilitÃ©          | 0             | 3                   | 5           | **8**  |
| **Total**               | **14**        | **19**              | **25**      | **58** |

**Verdict global :** Le frontend a une base solide (shadcn/ui, Zustand, React Query, 8 themes, AccessibilityToolbar AAA). Mais il reste un palier d'industrialisation Ã  franchir pour passer de "bon projet" Ã  "premium" : duplications de constantes, couleurs hardcodÃ©es ignorant les thÃ¨mes, charts non thÃ©matisÃ©s, raw inputs hors design system.

---

## 2. Axe 1 â€” Architecture, Code QualitÃ© & DRY

### ðŸ”´ Constats critiques

#### A1 â€” Constantes admin dupliquÃ©es âœ…

**SÃ©vÃ©ritÃ© :** Critical â€” risque de divergence entre les sources

| Fichier                                               | Constantes dupliquÃ©es                            |
| ----------------------------------------------------- | ------------------------------------------------- |
| `components/admin/ExerciseCreateModal.tsx` (L25â€“44) | EXERCISE_TYPES, DIFFICULTIES, AGE_GROUPS          |
| `components/admin/ExerciseEditModal.tsx` (L41â€“53)   | EXERCISE_TYPES, DIFFICULTIES                      |
| `components/admin/ChallengeCreateModal.tsx` (L39)     | AGE_GROUPS                                        |
| `components/admin/ChallengeEditModal.tsx` (L59)       | AGE_GROUPS                                        |
| `components/admin/BadgeCreateModal.tsx` (L27)         | DIFFICULTIES (bronze/silver/gold/legendary)       |
| `components/admin/BadgeEditModal.tsx` (L28)           | DIFFICULTIES                                      |
| `app/admin/content/page.tsx` (L42â€“74)               | EXERCISE_TYPES, CHALLENGE_TYPES, BADGE_CATEGORIES |

**Source centrale existante mais ignorÃ©e :** `lib/constants/exercises.ts`, `lib/constants/challenges.ts`

**Action :** Importer depuis `lib/constants/` et supprimer les dÃ©finitions locales.

---

#### A2 â€” AIGenerator dupliquÃ© (~800 lignes Ã— 2) âœ…

| Fichier                                 | Lignes | MÃ©thode streaming     |
| --------------------------------------- | ------ | ---------------------- |
| `components/exercises/AIGenerator.tsx`  | ~372   | EventSource (SSE)      |
| `components/challenges/AIGenerator.tsx` | ~416   | fetch + ReadableStream |

**Duplication ~60% :** MÃªme layout (Card, Selects type/Ã¢ge, textarea prompt, streaming UI, cancel).
**DiffÃ©rences :** Endpoint, validation (exercices valident, challenges non), affichage succÃ¨s.

**Action :** Extraire `AIGeneratorBase` avec endpoint/options/streaming configurables. Garder les variantes domaine-spÃ©cifiques lÃ©gÃ¨res.

---

#### A3 â€” Logique `hasAiTag` dupliquÃ©e âœ…

**Fichier :** `components/challenges/ChallengeCard.tsx` (L48â€“55 et L84â€“95)

MÃªme bloc complexe apparaÃ®t 2 fois :

```typescript
challenge.tags &&
  (Array.isArray(challenge.tags)
    ? challenge.tags.includes("ai")
    : challenge.tags === "ai" ||
      challenge.tags
        .split(",")
        .map((t) => t.trim())
        .includes("ai"));
```

**Action :** Extraire `hasAiTag(tags: unknown): boolean` dans `lib/utils/`.

---

#### A4 â€” Validation duplique les constantes âœ…

> Note : P1.4 a unifiÃ© `lib/validations/` â†’ `lib/validation/` (A5 partiellement traitÃ© aussi).

**Fichiers :** `lib/validation/exercise.ts` (L11â€“24) vs `lib/constants/exercises.ts`

`VALID_EXERCISE_TYPES` et `VALID_AGE_GROUPS` sont des copies de ce qui existe dans `lib/constants/`.

**Action :** DÃ©river les tableaux de validation depuis les constantes centrales.

---

#### A5 â€” Dossier naming incohÃ©rent âœ…

- `lib/validation/` (singulier) â€” `exercise.ts`
- `lib/validations/` (pluriel) â€” `dashboard.ts`

**Action :** Standardiser sur `lib/validation/` et dÃ©placer `dashboard.ts`.

---

### ðŸŸ¡ Points d'amÃ©lioration

| #   | Constat                                      | DÃ©tail                                                                                                                                                                                   |
| --- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A6  | **LoadingState sous-utilisÃ©**               | ~10 composants utilisent `Loader2` + `animate-spin` inline au lieu du `LoadingState` partagÃ© (ExerciseModal, ExerciseSolver, ChallengeModal, ChallengeSolver, ProtectedRoute, BadgeGrid) |
| A7  | **BadgeCard n'utilise pas ContentCardBase**  | ExerciseCard et ChallengeCard l'utilisent ; BadgeCard implÃ©mente sa propre Card + motion                                                                                                 |
| A8  | **Import `cn` incohÃ©rent**                  | Certains composants importent depuis `@/lib/utils`, d'autres depuis `@/lib/utils/cn`                                                                                                      |
| A9  | **ExerciseGenerator vs AIGenerator overlap** | ExerciseGenerator (non-streaming) et AIGenerator (SSE) ont une UI similaire sans distinction claire                                                                                       |
| A10 | **Skeletons dashboard ad-hoc**               | StreakWidget, LeaderboardWidget, ChallengesProgressWidget, CategoryAccuracyChart, AverageTimeWidget utilisent chacun un pattern `animate-pulse` diffÃ©rent                                |

---

### ðŸŸ¢ Bonnes pratiques en place

| #   | Acquis                                                                                              |
| --- | --------------------------------------------------------------------------------------------------- |
| âœ… | **ContentCardBase** â€” DRY cartes exercices/dÃ©fis (motion + badge "RÃ©solu")                      |
| âœ… | **usePaginatedContent** â€” pagination centralisÃ©e, utilisÃ©e par useExercises et useChallenges    |
| âœ… | **API client unique** (`lib/api/client.ts`) â€” CSRF, refresh 401, mÃ©thodes typÃ©es                |
| âœ… | **Zustand stores ciblÃ©s** â€” themeStore, localeStore, accessibilityStore (separation of concerns) |
| âœ… | **ZÃ©ro `any` dans les props** â€” interfaces bien dÃ©finies partout (ExerciseCardProps, etc.)      |
| âœ… | **useChallenge/useExercise symÃ©triques** â€” mÃªme pattern (query, invalidation, return shape)     |
| âœ… | **shadcn/ui + Radix + cva** â€” composants UI abstraits, pas de styles inline                       |
| âœ… | **43 hooks custom** â€” couverture complÃ¨te (auth, badges, challenges, admin, stats)               |

---

## 3. Axe 2 â€” ThÃ¨mes & Design System

### ðŸ”´ Constats critiques

#### T1 â€” Couleurs hardcodÃ©es ignorant le thÃ¨me (~25+ occurrences) â¬œ

| Fichier                              | Valeurs hardcodÃ©es                                      | Contexte                    |
| ------------------------------------ | -------------------------------------------------------- | --------------------------- |
| `ProgressChart.tsx` (L68â€“86)       | `#7c3aed`, `rgba(124,58,237,0.2)`, `rgba(18,18,26,0.95)` | Courbe, tooltip             |
| `DailyExercisesChart.tsx` (L42â€“98) | `rgba(255,206,86,...)`, `#a0a0a0`, `rgba(18,18,26,0.95)` | Barres, axes, tooltip       |
| `ChatbotFloating.tsx` (L214â€“215)   | `rgba(59,130,246,0.5)`                                   | Glow bleu (pas theme-aware) |
| `ChessRenderer.tsx` (L289â€“398)     | `#1e3a5f`, `#e8e8e8`, multiples `rgba`                   | PiÃ¨ces, cases              |
| `GraphRenderer.tsx` (L217â€“238)     | `#fbbf24`, `#f59e0b`, `#1e293b`                          | NÅ“uds SVG                  |
| `Planet.tsx` (L54â€“183)             | Multiples `rgba`                                         | Gradients planÃ¨te          |
| `Starfield.tsx` (L41â€“47)           | Multiples `rgba`                                         | Couleurs Ã©toiles           |
| `Particles.tsx` (L40â€“49)           | `rgba(139,92,246,0.3)` etc.                              | Couleurs particules         |
| `AccessibilityToolbar.tsx` (L195)    | `text-violet-600 ring-violet-600`                        | Badge theme-specific        |

---

#### T2 â€” Variables CSS rÃ©fÃ©rencÃ©es mais non dÃ©finies âœ…

| Variable                   | RÃ©fÃ©rencÃ©e dans            | DÃ©finie | Impact                         |
| -------------------------- | ----------------------------- | -------- | ------------------------------ |
| `--sidebar-*` (6 vars)     | `@theme inline` (globals.css) | âŒ       | Sidebar potentiellement cassÃ© |
| `--chart-1` Ã  `--chart-5` | `@theme inline` (globals.css) | âŒ       | Charts sans tokens             |

**Action :** DÃ©finir ces 11 variables dans chaque bloc thÃ¨me de `globals.css`.

---

#### T3 â€” Usages `dark:` avec couleurs fixes (~30+ occurrences) â¬œ

Nombreux composants utilisent le pattern `text-yellow-600 dark:text-yellow-400` ou `border-slate-400 dark:border-slate-600` au lieu de tokens sÃ©mantiques. Ces couleurs ignorent le `data-theme` actif.

**Exemples :** pages auth (verify-email, login, forgot-password), PerformanceByType, banners, exercises/challenges.

**Action :** CrÃ©er des tokens sÃ©mantiques (`--warning`, `--success`, `--info`) et les utiliser.

---

### ðŸŸ¡ Points d'amÃ©lioration

| #   | Constat                                   | DÃ©tail                                                                                                                                                                    |
| --- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T4  | **Spacing arbitraire** (~40+ occurrences) | `min-h-[60px]`, `w-[400px]`, `min-h-[200px]` etc. au lieu de la scale Tailwind                                                                                             |
| T5  | **Accessibility vs theme conflit**        | `accessibility.css` dÃ©finit `--surface`, `--text-primary` ; `globals.css` utilise `--background`, `--foreground` â€” noms diffÃ©rents, risque de conflit en high-contrast |
| T6  | **WCAG hardcoded**                        | `globals.css` L641â€“648 : `#6d28d9`, `#525252` pour minimalist, bypass le systÃ¨me de variables                                                                           |

### ðŸŸ¢ Bonnes pratiques en place

| #   | Acquis                                                                                                    |
| --- | --------------------------------------------------------------------------------------------------------- |
| âœ… | **8 themes complets** (spatial, minimalist, ocean, dune, forest, aurora, dino, unicorn) avec light + dark |
| âœ… | **`@theme inline` natif Tailwind v4** â€” tokens sÃ©mantiques via CSS variables                           |
| âœ… | **themeStore Zustand** â€” persistence, migration (`neutral` â†’ `dune`)                                  |

---

## 4. Axe 3 â€” UI/UX & Best Practices EdTech

### ðŸ”´ Constats critiques

#### U1 â€” Page Badges : pas de gestion d'erreur âœ…

**Fichier :** `app/badges/page.tsx` (L63â€“74)

`useBadges()` retourne `error` mais il n'est jamais affichÃ©. Pas de `EmptyState` ni de retry.

**Action :** Ajouter un `EmptyState` avec retry comme sur les autres pages.

---

#### U2 â€” Home : lazy components avec placeholder vide âœ…

**Fichier :** `app/page.tsx`

`AcademyStatsWidget` et `ChatbotFloating` utilisent `dynamic()` avec `loading: () => null`. L'utilisateur voit un espace vide pendant le chargement.

**Action :** Remplacer `null` par un skeleton ou un placeholder dimensionnÃ©.

---

### ðŸŸ¡ Points d'amÃ©lioration

| #   | Constat                                | DÃ©tail                                                                                                                               |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| U3  | **Skeletons dashboard hÃ©tÃ©rogÃ¨nes** | `StatsCard` a un skeleton dÃ©diÃ© (`StatsCardSkeleton`), mais StreakWidget/LeaderboardWidget/etc. utilisent du `animate-pulse` ad-hoc |
| U4  | **Labels i18n manquants**              | "Vue grille", "Vue liste" hardcodÃ©s en franÃ§ais dans exercises/challenges au lieu de `t()`                                          |
| U5  | **Leaderboard error non standard**     | Custom error card au lieu du `EmptyState` partagÃ© ; pas de retry                                                                     |
| U6  | **Badge icons `alt=""`**               | `BadgeCard.tsx` (L165â€“167) et `badges/page.tsx` (L492â€“494) â€” `alt=""` au lieu du nom du badge                                   |

### ðŸŸ¢ Bonnes pratiques en place

| #   | Acquis                                                                                        |
| --- | --------------------------------------------------------------------------------------------- |
| âœ… | **Layout cohÃ©rent** : `PageLayout` â†’ `PageHeader` â†’ `PageSection` â†’ `PageGrid`         |
| âœ… | **EmptyState partagÃ©** avec icÃ´ne, description, action                                      |
| âœ… | **Suspense + LoadingState** sur exercices/challenges                                          |
| âœ… | **Dashboard 4 onglets** â€” hiÃ©rarchie claire (Overview, Recommendations, Progress, Details) |
| âœ… | **QuickStartActions** â€” CTAs clairs en haut du dashboard                                    |

---

## 5. Axe 4 â€” QualitÃ© Graphique & Rendu Premium

### ðŸ”´ Constats critiques

#### V1 â€” DefaultRenderer : rendu JSON brut â¬œ

**Fichier :** `components/challenges/visualizations/DefaultRenderer.tsx`

JSON affichÃ© dans un `<pre>` sans Card, sans coloration syntaxique. C'est le composant le plus "cheap" du projet.

**Action :** Wrapper dans une Card, ajouter un minimum de formatage typographique.

---

#### V2 â€” Raw `<input>` Ã— 4 hors design system âœ…

| Fichier                       | Ã‰lÃ©ment                    |
| ----------------------------- | ---------------------------- |
| `PatternRenderer.tsx` (L172)  | `<input type="text">` custom |
| `SequenceRenderer.tsx` (L130) | `<input type="text">` custom |
| `Chatbot.tsx` (L160)          | `<input type="text">` custom |
| `ChatbotFloating.tsx` (L179)  | `<input type="text">` custom |

Le composant `Input` (`components/ui/input.tsx`) existe mais n'est pas utilisÃ©.

---

#### V3 â€” ChatbotFloating button hors thÃ¨me âœ…

**Fichier :** `ChatbotFloating.tsx` (L218â€“224)

`bg-blue-600`, `border-4 border-white/50`, `shadow-[0_0_20px_rgba(59,130,246,0.5)]` â€” couleur bleue fixe au lieu de `bg-primary` + `shadow-primary/30`.

---

#### V4 â€” GraphRenderer couleurs hardcodÃ©es â¬œ

**Fichier :** `GraphRenderer.tsx` (L217â€“238)

SVG avec `#fbbf24`, `#f59e0b`, `#1e293b` au lieu de tokens. Pas d'animation.

---

### ðŸŸ¡ Points d'amÃ©lioration

| #   | Constat                             | DÃ©tail                                                                                         |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------- |
| V5  | **Ombres non systÃ©matisÃ©es**      | `shadow-sm`, `shadow-lg`, `shadow-2xl`, `shadow-[custom]` utilisÃ©s sans Ã©chelle d'Ã©lÃ©vation |
| V6  | **Charts sans animation d'entrÃ©e** | Recharts supporte `isAnimationActive` mais non exploitÃ©                                        |
| V7  | **Feature cards Home**              | Pas de hover ni de `card-spatial-depth` (utilisÃ© ailleurs)                                     |
| V8  | **VisualRenderer flip**             | `<span>â†”</span>` au lieu de l'icÃ´ne Lucide `FlipHorizontal`                                  |

### ðŸŸ¢ Bonnes pratiques en place

| #   | Acquis                                                                                          |
| --- | ----------------------------------------------------------------------------------------------- |
| âœ… | **Gradients hero/footer cohÃ©rents** â€” `from-primary via-accent to-primary`                   |
| âœ… | **Visualisations challenges** â€” framer-motion, drag-and-drop (Puzzle), chess, coding          |
| âœ… | **Spatial background performant** â€” Canvas, `requestAnimationFrame`, cleanup, z-index correct |
| âœ… | **`card-spatial-depth`** â€” dÃ©fini dans globals.css, utilisÃ© sur StatsCard et badges         |

---

## 6. Axe 5 â€” AccessibilitÃ© & Performances

### ðŸ”´ Constats critiques

Aucun constat critique â€” l'accessibilitÃ© est sÃ©rieusement traitÃ©e dans ce projet.

### ðŸŸ¡ Points d'amÃ©lioration

| #   | Constat                                          | DÃ©tail                                                                                                                                              |
| --- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC1 | **`alt=""` sur badges**                          | Devrait Ãªtre le nom du badge quand il est informatif (pas dÃ©coratif)                                                                               |
| AC2 | **Visualisations sans `useAccessibleAnimation`** | DeductionRenderer, GraphRenderer n'utilisent pas le hook (pas de respect reduced-motion)                                                             |
| AC3 | **High-contrast conflit**                        | `globals.css` et `accessibility.css` dÃ©finissent des overrides high-contrast avec des noms de variables diffÃ©rents (`--background` vs `--surface`) |

### ðŸŸ¢ Bonnes pratiques en place

| #   | Acquis                                                                                                                          |
| --- | ------------------------------------------------------------------------------------------------------------------------------- |
| âœ… | **AccessibilityToolbar AAA** â€” 5 modes (contraste, texte agrandi, animations, dyslexie, focus), bouton 44Ã—44px, ARIA complet |
| âœ… | **`prefers-reduced-motion`** â€” CSS + JS + composants spatiaux                                                                 |
| âœ… | **`useAccessibleAnimation` centralisÃ©** â€” motion + reducedMotion + focusMode                                                 |
| âœ… | **Skip link** dans le Header                                                                                                    |
| âœ… | **`sr-only`** sur les loaders                                                                                                   |

---

## 7. Plan d'implÃ©mentation priorisÃ©

### Phase 0 â€” Quick wins (risque zÃ©ro, ~3h) âœ… TERMINÃ‰E (03/03/2026)

| #        | Action                                                                                                                                                                                                                     | Fichiers                                                                   | Effort |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------ |
| âœ… P0.1 | Centraliser constantes admin â€” `ADMIN_EXERCISE_TYPES`, `ADMIN_DIFFICULTIES`, `ADMIN_CHALLENGE_TYPE_OPTIONS`, `ADMIN_CHALLENGE_AGE_GROUP_OPTIONS`, `BADGE_CATEGORIES`, `BADGE_DIFFICULTIES` crÃ©Ã©s dans `lib/constants/` | 6 modales admin + `content/page.tsx` + `lib/constants/badges.ts` (nouveau) | ~1h    |
| âœ… P0.2 | DÃ©finir `--chart-1`â†’`--chart-5` + `--sidebar-*` dans chaque thÃ¨me                                                                                                                                                      | `globals.css` â€” blocs per-thÃ¨me + catch-all sidebar                     | ~1h    |
| âœ… P0.3 | Remplacer raw `<input>` par `Input` du design system                                                                                                                                                                       | PatternRenderer, SequenceRenderer, Chatbot, ChatbotFloating                | ~30min |
| âœ… P0.4 | Ajouter gestion erreur page Badges avec `EmptyState` + retry                                                                                                                                                               | `app/badges/page.tsx` + clÃ©s i18n fr/en                                   | ~15min |
| âœ… P0.5 | Extraire `hasAiTag()` dans `lib/utils/format.ts`                                                                                                                                                                           | ChallengeCard.tsx                                                          | ~15min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Comportement identique, pas de nouveau test requis.

---

### Phase 1 â€” Industrialisation Design System (~4h) âœ… TERMINÃ‰E (03/03/2026)

| #        | Action                                                                                                                                                                                                                                         | Fichiers                   | Effort |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------ |
| âœ… P1.1 | `DashboardWidgetSkeleton` ajoutÃ© dans `DashboardSkeletons.tsx` â€” 5 widgets migrÃ©s (StreakWidget, LeaderboardWidget, AverageTimeWidget, ChallengesProgressWidget, CategoryAccuracyChart)                                                    | 6 fichiers dashboard       | ~1h    |
| âœ… P1.2 | ChatbotFloating thÃ©matisÃ© â€” `bg-primary` + shadow via `color-mix(in srgb, var(--color-primary) 40%)`                                                                                                                                       | ChatbotFloating.tsx        | ~30min |
| âœ… P1.3 | Tokens `--warning`, `--success`, `--info` + foreground dans `globals.css` â€” `@theme inline` + catch-all light/dark. RemplacÃ© dans `feedback.tsx`, `login/page.tsx`, `verify-email/page.tsx` (catÃ©gories/types laissÃ©s intentionnellement) | globals.css + 3 composants | ~2h    |
| âœ… P1.4 | `lib/validations/dashboard.ts` dÃ©placÃ© â†’ `lib/validation/dashboard.ts`, dossier `validations/` supprimÃ©, 3 imports + 1 test mis Ã  jour                                                                                                   | 5 fichiers                 | ~30min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Comportement identique.

---

### Phase 2 â€” DRY & Refactoring (~4h) âœ… TERMINÃ‰E (03/03/2026)

| #        | Action                                                                                                                                                                                                                                                                                                                            | Fichiers                                                                   | Effort |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------ |
| âœ… P2.1 | `AIGeneratorBase` extrait dans `components/shared/` â€” UI partagÃ©e (Card, Selects, Textarea, streaming indicator, rÃ©sultat, bandeau auth). Chaque variante reste thin wrapper (~130 lignes vs ~400) avec sa logique de streaming intacte (EventSource / fetch+ReadableStream). `Textarea` shadcn remplace le `<textarea>` raw. | `components/shared/AIGeneratorBase.tsx` (nouveau) + 2 variantes rÃ©Ã©crits | ~3h    |
| âœ… P2.2 | Import `cn` unifiÃ© sur `@/lib/utils` â€” batch replace sur tous les `.ts/.tsx`, `lib/utils.ts` commentaire mis Ã  jour                                                                                                                                                                                                           | ~37 fichiers                                                               | ~15min |
| âœ… P2.3 | `VALID_EXERCISE_TYPES` et `VALID_AGE_GROUPS` dÃ©rivent de `lib/constants/exercises.ts` via `Object.values()`                                                                                                                                                                                                                      | `lib/validation/exercise.ts`                                               | ~15min |
| âœ… P2.4 | `AcademyStatsWidgetLazy` â†’ skeleton dimensionnÃ© (5 stats en grid), `ChatbotFloatingLazy` â†’ cercle `bg-muted animate-pulse` en position fixe                                                                                                                                                                                  | `app/page.tsx`                                                             | ~30min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Streaming SSE et ReadableStream prÃ©servÃ©s Ã  l'identique.

---

### Phase 3 â€” Premium upgrade (~4h) ðŸŸ¡ EN COURS

| #        | Action                                                                                                                                                                                             | Fichiers                                   | Effort |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------ |
| âœ… P3.1 | Animations d'entrÃ©e charts â€” `isAnimationActive={!shouldReduceMotion}` + `animationDuration/Easing` sur `Line` et `Bar`. Respecte `prefers-reduced-motion` via `useAccessibleAnimation`         | ProgressChart.tsx, DailyExercisesChart.tsx | ~30min |
| â¬œ P3.2 | Tokens d'Ã©lÃ©vation â€” `shadow-card`, `shadow-elevated`, `shadow-float`                                                                                                                          | globals.css + composants                   | ~1h    |
| âœ… P3.3 | DefaultRenderer â€” CardHeader avec icÃ´ne `FileJson`/`Type` + Badge type, vue structurÃ©e avec coloration syntaxique lÃ©gÃ¨re par type de valeur (number/string/boolean/null)                     | DefaultRenderer.tsx                        | ~30min |
| âœ… P3.4 | Feature cards Home â€” classe `card-spatial-depth` ajoutÃ©e â†’ sweep au hover + translateY(-4px) + shadow primary. Reduced-motion dÃ©jÃ  gÃ©rÃ© par globals.css                                   | `app/page.tsx`                             | ~30min |
| âœ… P3.5 | ThÃ©matiser charts â€” `var(--color-chart-1/2)` pour Line/Bar, `var(--color-border/muted-foreground/popover)` pour grilles, axes, tooltip. Couleurs backend ignorÃ©es au profit des tokens thÃ¨me. | ProgressChart.tsx, DailyExercisesChart.tsx | ~1h    |
| âœ… P3.6 | i18n labels "Vue grille"/"Vue liste" â€” clÃ©s `viewGrid`/`viewList` ajoutÃ©es dans namespaces `exercises` et `challenges` (fr.json + en.json), cÃ¢blÃ©es via `t()` dans les deux pages            | exercises/challenges pages + messages      | ~15min |
| âœ… P3.7 | VisualRenderer flip â€” `<span>â†”</span>` remplacÃ© par `<FlipHorizontal className="h-4 w-4" />`                                                                                                  | VisualRenderer.tsx                         | ~5min  |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). 59/59 tests unitaires verts.

---

### Phase 4 â€” Polish accessibilitÃ© (~2h) âœ… TERMINÃ‰E

| #        | Action                                                                                                                                                                                                  | Fichiers                                 | Effort |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| âœ… P4.1 | Badge `alt` descriptif â€” nom du badge dans BadgeCard et badges/page.tsx                                                                                                                               | BadgeCard.tsx, badges/page.tsx           | ~15min |
| âœ… P4.2 | `useAccessibleAnimation` sur DeductionRenderer + GraphRenderer â€” `shouldReduceMotion` contrÃ´le transition-colors hover et animations Framer Motion                                                   | DeductionRenderer.tsx, GraphRenderer.tsx | ~30min |
| âœ… P4.3 | High-contrast unifiÃ© â€” `.high-contrast` supprimÃ© d'`accessibility.css`, `@media (prefers-contrast: high)` alignÃ© sur tokens shadcn/ui (`--foreground`, `--card`)                                   | accessibility.css                        | ~1h    |
| âœ… P4.4 | GraphRenderer tokens + animations SVG â€” couleurs â†’ `var(--color-chart-2/popover-foreground/primary-foreground)`, `motion.g` entrÃ©e opacity+scale avec stagger, dÃ©sactivÃ© si `shouldReduceMotion` | GraphRenderer.tsx                        | ~30min |

**Tests :** Build TypeScript sans erreur. 59/59 tests unitaires verts.

---

## 8. Matrice rÃ©capitulative

### Par effort et impact

| Phase                             | Effort | Impact                        | Risque | PrioritÃ©             |
| --------------------------------- | ------ | ----------------------------- | ------ | --------------------- |
| **Phase 0** â€” Quick wins        | ~3h    | Ã‰levÃ© (bugs, divergence)    | ZÃ©ro  | ðŸ”´ Faire maintenant |
| **Phase 1** â€” Design System     | ~4h    | Ã‰levÃ© (cohÃ©rence visuelle) | Faible | ðŸŸ  Faire ensuite    |
| **Phase 2** â€” DRY & Refactoring | ~4h    | Moyen (maintenabilitÃ©)       | Moyen  | ðŸŸ¡ Planifier        |
| **Phase 3** â€” Premium           | ~4h    | Moyen (perception qualitÃ©)   | Faible | ðŸŸ¡ Planifier        |
| **Phase 4** â€” Polish a11y       | ~2h    | Faible-Moyen (conformitÃ©)    | ZÃ©ro  | ðŸŸ¢ Quand possible   |

### Scores par zone

| Zone                    | Score actuel | Score cible |
| ----------------------- | ------------ | ----------- |
| Architecture & DRY      | 6/10         | 9/10        |
| Design System / ThÃ¨mes | 6/10         | 9/10        |
| UI/UX EdTech            | 7/10         | 9/10        |
| QualitÃ© visuelle       | 6/10         | 9/10        |
| AccessibilitÃ©          | 8/10         | 9/10        |
| **Moyenne**             | **6.6/10**   | **9/10**    |

### Estimation totale

|           | Heures   |
| --------- | -------- |
| Phase 0   | ~3h      |
| Phase 1   | ~4h      |
| Phase 2   | ~4h      |
| Phase 3   | ~4h      |
| Phase 4   | ~2h      |
| **Total** | **~17h** |

---

## Navigation

- [â† Audit Backend (terminÃ©)](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md)
- [â† Index projet](./README.md)
- [â† Index documentation](../INDEX.md)
