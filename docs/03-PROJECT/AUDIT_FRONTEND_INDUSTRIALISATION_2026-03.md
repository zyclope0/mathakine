# Audit Frontend — Industrialisation, Design System & UX Premium

**Date :** 03/03/2026
**Type :** Audit exhaustif (Architecture, DRY, Design System, UX EdTech, Qualité visuelle, Accessibilité)
**Périmètre :** `frontend/` — 101 composants, 32 hooks, 7 thèmes, ~15 000 lignes TSX
**Méthode :** Inspection systématique composant par composant, analyse cross-cutting des patterns
**Statut :** ✅ AUDIT HISTORIQUE TERMINÉ (03/03/2026) — ne plus utiliser ce fichier comme plan d'exécution actif

**Complémentaire à :** [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md) (backend — terminé)

> **Mise à jour 2026-04-03**
> Ce document reste utile comme photographie de la dette initiale, mais la source de vérité
> opérationnelle frontend est désormais [AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md](./AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md)
> et sa feuille de route `FFI-L1` à `FFI-L13`.
>
> Depuis cet audit historique, les lots suivants ont déjà été livrés et poussés :
> `FFI-L1` à `FFI-L9` (tokens critiques multi-thème, auth/bootstrap, storage, DRY pages contenu,
> loading/skeletons, cleanup legacy safe, recouvrement générateurs IA, préparation solver,
> split `ExerciseSolver`).
>
> Les principaux chantiers encore ouverts ne sont donc plus ceux de cet audit pris ligne à ligne,
> mais surtout :
> `FFI-L10` split `ChallengeSolver`, `FFI-L11` sweep large des couleurs sémantiques hardcodées,
> `FFI-L12` split `Header.tsx`, `FFI-L13` documentation design system + clarification chatbot.

---

## Sommaire

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Axe 1 — Architecture, Code Qualité & DRY](#2-axe-1--architecture-code-qualité--dry)
3. [Axe 2 — Thèmes & Design System](#3-axe-2--thèmes--design-system)
4. [Axe 3 — UI/UX & Best Practices EdTech](#4-axe-3--uiux--best-practices-edtech)
5. [Axe 4 — Qualité Graphique & Rendu Premium](#5-axe-4--qualité-graphique--rendu-premium)
6. [Axe 5 — Accessibilité & Performances](#6-axe-5--accessibilité--performances)
7. [Plan d'implémentation priorisé](#7-plan-dimplémentation-priorisé)
8. [Matrice récapitulative](#8-matrice-récapitulative)

---

## 1. Résumé exécutif

| Axe                    | 🔴 Critical | 🟡 Améliorations | 🟢 Acquis | Total  |
| ---------------------- | ----------- | ---------------- | --------- | ------ |
| Architecture & DRY     | 5           | 5                | 8         | **18** |
| Thèmes & Design System | 3           | 3                | 3         | **9**  |
| UI/UX EdTech           | 2           | 4                | 5         | **11** |
| Qualité visuelle       | 4           | 4                | 4         | **12** |
| Accessibilité          | 0           | 3                | 5         | **8**  |
| **Total**              | **14**      | **19**           | **25**    | **58** |

**Verdict global :** Le frontend a une base solide (shadcn/ui, Zustand, React Query, 7 thèmes, AccessibilityToolbar AAA). Mais il reste un palier d'industrialisation à franchir pour passer de "bon projet" à "premium" : duplications de constantes, couleurs hardcodées ignorant les thèmes, charts non thématisés, raw inputs hors design system.

---

## 2. Axe 1 — Architecture, Code Qualité & DRY

### 🔴 Constats critiques

#### A1 — Constantes admin dupliquées ✅

**Sévérité :** Critical — risque de divergence entre les sources

| Fichier                                             | Constantes dupliquées                             |
| --------------------------------------------------- | ------------------------------------------------- |
| `components/admin/ExerciseCreateModal.tsx` (L25–44) | EXERCISE_TYPES, DIFFICULTIES, AGE_GROUPS          |
| `components/admin/ExerciseEditModal.tsx` (L41–53)   | EXERCISE_TYPES, DIFFICULTIES                      |
| `components/admin/ChallengeCreateModal.tsx` (L39)   | AGE_GROUPS                                        |
| `components/admin/ChallengeEditModal.tsx` (L59)     | AGE_GROUPS                                        |
| `components/admin/BadgeCreateModal.tsx` (L27)       | DIFFICULTIES (bronze/silver/gold/legendary)       |
| `components/admin/BadgeEditModal.tsx` (L28)         | DIFFICULTIES                                      |
| `app/admin/content/page.tsx` (L42–74)               | EXERCISE_TYPES, CHALLENGE_TYPES, BADGE_CATEGORIES |

**Source centrale existante mais ignorée :** `lib/constants/exercises.ts`, `lib/constants/challenges.ts`

**Action :** Importer depuis `lib/constants/` et supprimer les définitions locales.

---

#### A2 — AIGenerator dupliqué (~800 lignes × 2) ✅

| Fichier                                 | Lignes | Méthode streaming      |
| --------------------------------------- | ------ | ---------------------- |
| `components/exercises/AIGenerator.tsx`  | ~372   | EventSource (SSE)      |
| `components/challenges/AIGenerator.tsx` | ~416   | fetch + ReadableStream |

**Duplication ~60% :** Même layout (Card, Selects type/âge, textarea prompt, streaming UI, cancel).
**Différences :** Endpoint, validation (exercices valident, challenges non), affichage succès.

**Action :** Extraire `AIGeneratorBase` avec endpoint/options/streaming configurables. Garder les variantes domaine-spécifiques légères.

---

#### A3 — Logique `hasAiTag` dupliquée ✅

**Fichier :** `components/challenges/ChallengeCard.tsx` (L48–55 et L84–95)

Même bloc complexe apparaît 2 fois :

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

#### A4 — Validation duplique les constantes ✅

> Note : P1.4 a unifié `lib/validations/` → `lib/validation/` (A5 partiellement traité aussi).

**Fichiers :** `lib/validation/exercise.ts` (L11–24) vs `lib/constants/exercises.ts`

`VALID_EXERCISE_TYPES` et `VALID_AGE_GROUPS` sont des copies de ce qui existe dans `lib/constants/`.

**Action :** Dériver les tableaux de validation depuis les constantes centrales.

---

#### A5 — Dossier naming incohérent ✅

- `lib/validation/` (singulier) — `exercise.ts`
- `lib/validations/` (pluriel) — `dashboard.ts`

**Action :** Standardiser sur `lib/validation/` et déplacer `dashboard.ts`.

---

### 🟡 Points d'amélioration

| #   | Constat                                      | Détail                                                                                                                                                                                   |
| --- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A6  | **LoadingState sous-utilisé**                | ~10 composants utilisent `Loader2` + `animate-spin` inline au lieu du `LoadingState` partagé (ExerciseModal, ExerciseSolver, ChallengeModal, ChallengeSolver, ProtectedRoute, BadgeGrid) |
| A7  | **BadgeCard n'utilise pas ContentCardBase**  | ExerciseCard et ChallengeCard l'utilisent ; BadgeCard implémente sa propre Card + motion                                                                                                 |
| A8  | **Import `cn` incohérent**                   | Certains composants importent depuis `@/lib/utils`, d'autres depuis `@/lib/utils/cn`                                                                                                     |
| A9  | **ExerciseGenerator vs AIGenerator overlap** | ExerciseGenerator (non-streaming) et AIGenerator (SSE) ont une UI similaire sans distinction claire                                                                                      |
| A10 | **Skeletons dashboard ad-hoc**               | StreakWidget, LeaderboardWidget, ChallengesProgressWidget, CategoryAccuracyChart, AverageTimeWidget utilisent chacun un pattern `animate-pulse` différent                                |

---

### 🟢 Bonnes pratiques en place

| #   | Acquis                                                                                           |
| --- | ------------------------------------------------------------------------------------------------ |
| ✅  | **ContentCardBase** — DRY cartes exercices/défis (motion + badge "Résolu")                       |
| ✅  | **usePaginatedContent** — pagination centralisée, utilisée par useExercises et useChallenges     |
| ✅  | **API client unique** (`lib/api/client.ts`) — CSRF, refresh 401, méthodes typées                 |
| ✅  | **Zustand stores ciblés** — themeStore, localeStore, accessibilityStore (separation of concerns) |
| ✅  | **Zéro `any` dans les props** — interfaces bien définies partout (ExerciseCardProps, etc.)       |
| ✅  | **useChallenge/useExercise symétriques** — même pattern (query, invalidation, return shape)      |
| ✅  | **shadcn/ui + Radix + cva** — composants UI abstraits, pas de styles inline                      |
| ✅  | **32 hooks custom** — couverture complète (auth, badges, challenges, admin, stats)               |

---

## 3. Axe 2 — Thèmes & Design System

### 🔴 Constats critiques

#### T1 — Couleurs hardcodées ignorant le thème (~25+ occurrences) ⬜

| Fichier                            | Valeurs hardcodées                                       | Contexte                    |
| ---------------------------------- | -------------------------------------------------------- | --------------------------- |
| `ProgressChart.tsx` (L68–86)       | `#7c3aed`, `rgba(124,58,237,0.2)`, `rgba(18,18,26,0.95)` | Courbe, tooltip             |
| `DailyExercisesChart.tsx` (L42–98) | `rgba(255,206,86,...)`, `#a0a0a0`, `rgba(18,18,26,0.95)` | Barres, axes, tooltip       |
| `ChatbotFloating.tsx` (L214–215)   | `rgba(59,130,246,0.5)`                                   | Glow bleu (pas theme-aware) |
| `ChessRenderer.tsx` (L289–398)     | `#1e3a5f`, `#e8e8e8`, multiples `rgba`                   | Pièces, cases               |
| `GraphRenderer.tsx` (L217–238)     | `#fbbf24`, `#f59e0b`, `#1e293b`                          | Nœuds SVG                   |
| `Planet.tsx` (L54–183)             | Multiples `rgba`                                         | Gradients planète           |
| `Starfield.tsx` (L41–47)           | Multiples `rgba`                                         | Couleurs étoiles            |
| `Particles.tsx` (L40–49)           | `rgba(139,92,246,0.3)` etc.                              | Couleurs particules         |
| `AccessibilityToolbar.tsx` (L195)  | `text-violet-600 ring-violet-600`                        | Badge theme-specific        |

---

#### T2 — Variables CSS référencées mais non définies ✅

| Variable                  | Référencée dans               | Définie | Impact                        |
| ------------------------- | ----------------------------- | ------- | ----------------------------- |
| `--sidebar-*` (6 vars)    | `@theme inline` (globals.css) | ❌      | Sidebar potentiellement cassé |
| `--chart-1` à `--chart-5` | `@theme inline` (globals.css) | ❌      | Charts sans tokens            |

**Action :** Définir ces 11 variables dans chaque bloc thème de `globals.css`.

---

#### T3 — Usages `dark:` avec couleurs fixes (~30+ occurrences) ⬜

Nombreux composants utilisent le pattern `text-yellow-600 dark:text-yellow-400` ou `border-slate-400 dark:border-slate-600` au lieu de tokens sémantiques. Ces couleurs ignorent le `data-theme` actif.

**Exemples :** pages auth (verify-email, login, forgot-password), PerformanceByType, banners, exercises/challenges.

**Action :** Créer des tokens sémantiques (`--warning`, `--success`, `--info`) et les utiliser.

---

### 🟡 Points d'amélioration

| #   | Constat                                   | Détail                                                                                                                                                                 |
| --- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T4  | **Spacing arbitraire** (~40+ occurrences) | `min-h-[60px]`, `w-[400px]`, `min-h-[200px]` etc. au lieu de la scale Tailwind                                                                                         |
| T5  | **Accessibility vs theme conflit**        | `accessibility.css` définit `--surface`, `--text-primary` ; `globals.css` utilise `--background`, `--foreground` — noms différents, risque de conflit en high-contrast |
| T6  | **WCAG hardcoded**                        | `globals.css` L641–648 : `#6d28d9`, `#525252` pour minimalist, bypass le système de variables                                                                          |

### 🟢 Bonnes pratiques en place

| #   | Acquis                                                                                          |
| --- | ----------------------------------------------------------------------------------------------- |
| ✅  | **7 thèmes complets** (spatial, minimalist, ocean, dune, forest, peach, dino) avec light + dark |
| ✅  | **`@theme inline` natif Tailwind v4** — tokens sémantiques via CSS variables                    |
| ✅  | **themeStore Zustand** — persistence, migration (`neutral` → `dune`)                            |

---

## 4. Axe 3 — UI/UX & Best Practices EdTech

### 🔴 Constats critiques

#### U1 — Page Badges : pas de gestion d'erreur ✅

**Fichier :** `app/badges/page.tsx` (L63–74)

`useBadges()` retourne `error` mais il n'est jamais affiché. Pas de `EmptyState` ni de retry.

**Action :** Ajouter un `EmptyState` avec retry comme sur les autres pages.

---

#### U2 — Home : lazy components avec placeholder vide ✅

**Fichier :** `app/page.tsx`

`AcademyStatsWidget` et `ChatbotFloating` utilisent `dynamic()` avec `loading: () => null`. L'utilisateur voit un espace vide pendant le chargement.

**Action :** Remplacer `null` par un skeleton ou un placeholder dimensionné.

---

### 🟡 Points d'amélioration

| #   | Constat                             | Détail                                                                                                                              |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| U3  | **Skeletons dashboard hétérogènes** | `StatsCard` a un skeleton dédié (`StatsCardSkeleton`), mais StreakWidget/LeaderboardWidget/etc. utilisent du `animate-pulse` ad-hoc |
| U4  | **Labels i18n manquants**           | "Vue grille", "Vue liste" hardcodés en français dans exercises/challenges au lieu de `t()`                                          |
| U5  | **Leaderboard error non standard**  | Custom error card au lieu du `EmptyState` partagé ; pas de retry                                                                    |
| U6  | **Badge icons `alt=""`**            | `BadgeCard.tsx` (L165–167) et `badges/page.tsx` (L492–494) — `alt=""` au lieu du nom du badge                                       |

### 🟢 Bonnes pratiques en place

| #   | Acquis                                                                                     |
| --- | ------------------------------------------------------------------------------------------ |
| ✅  | **Layout cohérent** : `PageLayout` → `PageHeader` → `PageSection` → `PageGrid`             |
| ✅  | **EmptyState partagé** avec icône, description, action                                     |
| ✅  | **Suspense + LoadingState** sur exercices/challenges                                       |
| ✅  | **Dashboard 4 onglets** — hiérarchie claire (Overview, Recommendations, Progress, Details) |
| ✅  | **QuickStartActions** — CTAs clairs en haut du dashboard                                   |

---

## 5. Axe 4 — Qualité Graphique & Rendu Premium

### 🔴 Constats critiques

#### V1 — DefaultRenderer : rendu JSON brut ⬜

**Fichier :** `components/challenges/visualizations/DefaultRenderer.tsx`

JSON affiché dans un `<pre>` sans Card, sans coloration syntaxique. C'est le composant le plus "cheap" du projet.

**Action :** Wrapper dans une Card, ajouter un minimum de formatage typographique.

---

#### V2 — Raw `<input>` × 4 hors design system ✅

| Fichier                       | Élément                      |
| ----------------------------- | ---------------------------- |
| `PatternRenderer.tsx` (L172)  | `<input type="text">` custom |
| `SequenceRenderer.tsx` (L130) | `<input type="text">` custom |
| `Chatbot.tsx` (L160)          | `<input type="text">` custom |
| `ChatbotFloating.tsx` (L179)  | `<input type="text">` custom |

Le composant `Input` (`components/ui/input.tsx`) existe mais n'est pas utilisé.

---

#### V3 — ChatbotFloating button hors thème ✅

**Fichier :** `ChatbotFloating.tsx` (L218–224)

`bg-blue-600`, `border-4 border-white/50`, `shadow-[0_0_20px_rgba(59,130,246,0.5)]` — couleur bleue fixe au lieu de `bg-primary` + `shadow-primary/30`.

---

#### V4 — GraphRenderer couleurs hardcodées ⬜

**Fichier :** `GraphRenderer.tsx` (L217–238)

SVG avec `#fbbf24`, `#f59e0b`, `#1e293b` au lieu de tokens. Pas d'animation.

---

### 🟡 Points d'amélioration

| #   | Constat                            | Détail                                                                                      |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------- |
| V5  | **Ombres non systématisées**       | `shadow-sm`, `shadow-lg`, `shadow-2xl`, `shadow-[custom]` utilisés sans échelle d'élévation |
| V6  | **Charts sans animation d'entrée** | Recharts supporte `isAnimationActive` mais non exploité                                     |
| V7  | **Feature cards Home**             | Pas de hover ni de `card-spatial-depth` (utilisé ailleurs)                                  |
| V8  | **VisualRenderer flip**            | `<span>↔</span>` au lieu de l'icône Lucide `FlipHorizontal`                                 |

### 🟢 Bonnes pratiques en place

| #   | Acquis                                                                                        |
| --- | --------------------------------------------------------------------------------------------- |
| ✅  | **Gradients hero/footer cohérents** — `from-primary via-accent to-primary`                    |
| ✅  | **Visualisations challenges** — framer-motion, drag-and-drop (Puzzle), chess, coding          |
| ✅  | **Spatial background performant** — Canvas, `requestAnimationFrame`, cleanup, z-index correct |
| ✅  | **`card-spatial-depth`** — défini dans globals.css, utilisé sur StatsCard et badges           |

---

## 6. Axe 5 — Accessibilité & Performances

### 🔴 Constats critiques

Aucun constat critique — l'accessibilité est sérieusement traitée dans ce projet.

### 🟡 Points d'amélioration

| #   | Constat                                          | Détail                                                                                                                                             |
| --- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC1 | **`alt=""` sur badges**                          | Devrait être le nom du badge quand il est informatif (pas décoratif)                                                                               |
| AC2 | **Visualisations sans `useAccessibleAnimation`** | DeductionRenderer, GraphRenderer n'utilisent pas le hook (pas de respect reduced-motion)                                                           |
| AC3 | **High-contrast conflit**                        | `globals.css` et `accessibility.css` définissent des overrides high-contrast avec des noms de variables différents (`--background` vs `--surface`) |

### 🟢 Bonnes pratiques en place

| #   | Acquis                                                                                                                       |
| --- | ---------------------------------------------------------------------------------------------------------------------------- |
| ✅  | **AccessibilityToolbar AAA** — 5 modes (contraste, texte agrandi, animations, dyslexie, focus), bouton 44×44px, ARIA complet |
| ✅  | **`prefers-reduced-motion`** — CSS + JS + composants spatiaux                                                                |
| ✅  | **`useAccessibleAnimation` centralisé** — motion + reducedMotion + focusMode                                                 |
| ✅  | **Skip link** dans le Header                                                                                                 |
| ✅  | **`sr-only`** sur les loaders                                                                                                |

---

## 7. Plan d'implémentation priorisé

### Phase 0 — Quick wins (risque zéro, ~3h) ✅ TERMINÉE (03/03/2026)

| #       | Action                                                                                                                                                                                                                 | Fichiers                                                                   | Effort |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------ |
| ✅ P0.1 | Centraliser constantes admin — `ADMIN_EXERCISE_TYPES`, `ADMIN_DIFFICULTIES`, `ADMIN_CHALLENGE_TYPE_OPTIONS`, `ADMIN_CHALLENGE_AGE_GROUP_OPTIONS`, `BADGE_CATEGORIES`, `BADGE_DIFFICULTIES` créés dans `lib/constants/` | 6 modales admin + `content/page.tsx` + `lib/constants/badges.ts` (nouveau) | ~1h    |
| ✅ P0.2 | Définir `--chart-1`→`--chart-5` + `--sidebar-*` dans chaque thème                                                                                                                                                      | `globals.css` — blocs per-thème + catch-all sidebar                        | ~1h    |
| ✅ P0.3 | Remplacer raw `<input>` par `Input` du design system                                                                                                                                                                   | PatternRenderer, SequenceRenderer, Chatbot, ChatbotFloating                | ~30min |
| ✅ P0.4 | Ajouter gestion erreur page Badges avec `EmptyState` + retry                                                                                                                                                           | `app/badges/page.tsx` + clés i18n fr/en                                    | ~15min |
| ✅ P0.5 | Extraire `hasAiTag()` dans `lib/utils/format.ts`                                                                                                                                                                       | ChallengeCard.tsx                                                          | ~15min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Comportement identique, pas de nouveau test requis.

---

### Phase 1 — Industrialisation Design System (~4h) ✅ TERMINÉE (03/03/2026)

| #       | Action                                                                                                                                                                                                                                    | Fichiers                   | Effort |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------ |
| ✅ P1.1 | `DashboardWidgetSkeleton` ajouté dans `DashboardSkeletons.tsx` — 5 widgets migrés (StreakWidget, LeaderboardWidget, AverageTimeWidget, ChallengesProgressWidget, CategoryAccuracyChart)                                                   | 6 fichiers dashboard       | ~1h    |
| ✅ P1.2 | ChatbotFloating thématisé — `bg-primary` + shadow via `color-mix(in srgb, var(--color-primary) 40%)`                                                                                                                                      | ChatbotFloating.tsx        | ~30min |
| ✅ P1.3 | Tokens `--warning`, `--success`, `--info` + foreground dans `globals.css` — `@theme inline` + catch-all light/dark. Remplacé dans `feedback.tsx`, `login/page.tsx`, `verify-email/page.tsx` (catégories/types laissés intentionnellement) | globals.css + 3 composants | ~2h    |
| ✅ P1.4 | `lib/validations/dashboard.ts` déplacé → `lib/validation/dashboard.ts`, dossier `validations/` supprimé, 3 imports + 1 test mis à jour                                                                                                    | 5 fichiers                 | ~30min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Comportement identique.

---

### Phase 2 — DRY & Refactoring (~4h) ✅ TERMINÉE (03/03/2026)

| #       | Action                                                                                                                                                                                                                                                                                                                        | Fichiers                                                                 | Effort |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------ |
| ✅ P2.1 | `AIGeneratorBase` extrait dans `components/shared/` — UI partagée (Card, Selects, Textarea, streaming indicator, résultat, bandeau auth). Chaque variante reste thin wrapper (~130 lignes vs ~400) avec sa logique de streaming intacte (EventSource / fetch+ReadableStream). `Textarea` shadcn remplace le `<textarea>` raw. | `components/shared/AIGeneratorBase.tsx` (nouveau) + 2 variantes réécrits | ~3h    |
| ✅ P2.2 | Import `cn` unifié sur `@/lib/utils` — batch replace sur tous les `.ts/.tsx`, `lib/utils.ts` commentaire mis à jour                                                                                                                                                                                                           | ~37 fichiers                                                             | ~15min |
| ✅ P2.3 | `VALID_EXERCISE_TYPES` et `VALID_AGE_GROUPS` dérivent de `lib/constants/exercises.ts` via `Object.values()`                                                                                                                                                                                                                   | `lib/validation/exercise.ts`                                             | ~15min |
| ✅ P2.4 | `AcademyStatsWidgetLazy` → skeleton dimensionné (5 stats en grid), `ChatbotFloatingLazy` → cercle `bg-muted animate-pulse` en position fixe                                                                                                                                                                                   | `app/page.tsx`                                                           | ~30min |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). Streaming SSE et ReadableStream préservés à l'identique.

---

### Phase 3 — Premium upgrade (~4h) 🟡 EN COURS

| #       | Action                                                                                                                                                                                        | Fichiers                                   | Effort |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------ |
| ✅ P3.1 | Animations d'entrée charts — `isAnimationActive={!shouldReduceMotion}` + `animationDuration/Easing` sur `Line` et `Bar`. Respecte `prefers-reduced-motion` via `useAccessibleAnimation`       | ProgressChart.tsx, DailyExercisesChart.tsx | ~30min |
| ⬜ P3.2 | Tokens d'élévation — `shadow-card`, `shadow-elevated`, `shadow-float`                                                                                                                         | globals.css + composants                   | ~1h    |
| ✅ P3.3 | DefaultRenderer — CardHeader avec icône `FileJson`/`Type` + Badge type, vue structurée avec coloration syntaxique légère par type de valeur (number/string/boolean/null)                      | DefaultRenderer.tsx                        | ~30min |
| ✅ P3.4 | Feature cards Home — classe `card-spatial-depth` ajoutée → sweep au hover + translateY(-4px) + shadow primary. Reduced-motion déjà géré par globals.css                                       | `app/page.tsx`                             | ~30min |
| ✅ P3.5 | Thématiser charts — `var(--color-chart-1/2)` pour Line/Bar, `var(--color-border/muted-foreground/popover)` pour grilles, axes, tooltip. Couleurs backend ignorées au profit des tokens thème. | ProgressChart.tsx, DailyExercisesChart.tsx | ~1h    |
| ✅ P3.6 | i18n labels "Vue grille"/"Vue liste" — clés `viewGrid`/`viewList` ajoutées dans namespaces `exercises` et `challenges` (fr.json + en.json), câblées via `t()` dans les deux pages             | exercises/challenges pages + messages      | ~15min |
| ✅ P3.7 | VisualRenderer flip — `<span>↔</span>` remplacé par `<FlipHorizontal className="h-4 w-4" />`                                                                                                  | VisualRenderer.tsx                         | ~5min  |

**Tests :** Build TypeScript sans erreur (`tsc --noEmit`). 59/59 tests unitaires verts.

---

### Phase 4 — Polish accessibilité (~2h) ✅ TERMINÉE

| #       | Action                                                                                                                                                                                           | Fichiers                                 | Effort |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------- | ------ |
| ✅ P4.1 | Badge `alt` descriptif — nom du badge dans BadgeCard et badges/page.tsx                                                                                                                          | BadgeCard.tsx, badges/page.tsx           | ~15min |
| ✅ P4.2 | `useAccessibleAnimation` sur DeductionRenderer + GraphRenderer — `shouldReduceMotion` contrôle transition-colors hover et animations Framer Motion                                               | DeductionRenderer.tsx, GraphRenderer.tsx | ~30min |
| ✅ P4.3 | High-contrast unifié — `.high-contrast` supprimé d'`accessibility.css`, `@media (prefers-contrast: high)` aligné sur tokens shadcn/ui (`--foreground`, `--card`)                                 | accessibility.css                        | ~1h    |
| ✅ P4.4 | GraphRenderer tokens + animations SVG — couleurs → `var(--color-chart-2/popover-foreground/primary-foreground)`, `motion.g` entrée opacity+scale avec stagger, désactivé si `shouldReduceMotion` | GraphRenderer.tsx                        | ~30min |

**Tests :** Build TypeScript sans erreur. 59/59 tests unitaires verts.

---

## 8. Matrice récapitulative

### Par effort et impact

| Phase                           | Effort | Impact                     | Risque | Priorité            |
| ------------------------------- | ------ | -------------------------- | ------ | ------------------- |
| **Phase 0** — Quick wins        | ~3h    | Élevé (bugs, divergence)   | Zéro   | 🔴 Faire maintenant |
| **Phase 1** — Design System     | ~4h    | Élevé (cohérence visuelle) | Faible | 🟠 Faire ensuite    |
| **Phase 2** — DRY & Refactoring | ~4h    | Moyen (maintenabilité)     | Moyen  | 🟡 Planifier        |
| **Phase 3** — Premium           | ~4h    | Moyen (perception qualité) | Faible | 🟡 Planifier        |
| **Phase 4** — Polish a11y       | ~2h    | Faible-Moyen (conformité)  | Zéro   | 🟢 Quand possible   |

### Scores par zone

| Zone                   | Score actuel | Score cible |
| ---------------------- | ------------ | ----------- |
| Architecture & DRY     | 6/10         | 9/10        |
| Design System / Thèmes | 6/10         | 9/10        |
| UI/UX EdTech           | 7/10         | 9/10        |
| Qualité visuelle       | 6/10         | 9/10        |
| Accessibilité          | 8/10         | 9/10        |
| **Moyenne**            | **6.6/10**   | **9/10**    |

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

- [← Audit Backend (terminé)](./AUDIT_ARCHITECTURE_BACKEND_2026-03.md)
- [← Index projet](./README.md)
- [← Index documentation](../INDEX.md)
