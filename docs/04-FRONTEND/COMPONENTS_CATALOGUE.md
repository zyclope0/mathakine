# Catalogue des composants React - Mathakine

> Scope : `frontend/components/`
> Updated : 2026-04-16
> Source : audit repertoire + `ARCHITECTURE.md`
> Methode : comptage terrain des `.tsx` source (tests exclus)

---

## Vue d'ensemble

Le repertoire `frontend/components/` contient **229 composants source** repartis en **26 buckets top-level**.

Le but de ce document n'est pas de dupliquer chaque implementation ligne par ligne, mais de donner :

- la cartographie reelle du repertoire
- les familles de composants vivantes
- les buckets a lire en priorite selon le domaine touche

---

## Buckets top-level

| Bucket | Composants | Role |
| ------ | ---------- | ---- |
| `ui/` | 21 | primitives shadcn/ui |
| `dashboard/` | 34 | widgets stats, charts, tabs sections |
| `challenges/` | 30 | UI defis logiques + renderers visuels |
| `layout/` | 15 | structure de page |
| `admin/` | 14 | shell admin read-heavy + contenu admin |
| `spatial/` | 6 | decor theme-aware |
| `exercises/` | 11 | UI exercices |
| `shared/` | 15 | composants transverses |
| `providers/` | 7 | composition racine |
| `home/` | 2 | home marketing |
| `badges/` | 15 | badges + sous-blocs `badgeCard/` |
| `profile/` | 12 | sections profil |
| `chat/` | 5 | assistant global |
| `locale/` | 2 | locale init / selecteur |
| `theme/` | 2 | theme selector / dark mode |
| `accessibility/` | 2 | toolbar + audit |
| `auth/` | 1 | `ProtectedRoute` |
| `diagnostic/` | 7 | solver et primitives diagnostic |
| `feedback/` | 1 | feedback trigger |
| `settings/` | 8 | page parametres |
| `pwa/` | 1 | prompt installation |
| `learner/` | 7 | surfaces `home-learner` |
| `leaderboard/` | 8 | classement et podium |
| `progression/` | 1 | arc de progression |
| racine `components/` | 2 | `LogoMathakine`, `LogoBadge` |

---

## Familles structurantes

### `layout/`

Famille shell/navigation.

Composants pivots :

- `Header`
- `HeaderDesktopNav`
- `HeaderMobileMenu`
- `HeaderUserMenu`
- `PageLayout`
- `PageHeader`
- `PageSection`

### `providers/`

Famille bootstrap/runtime client.

Composants pivots :

- `Providers`
- `NextIntlProvider`
- `AuthSyncProvider`
- `AccessScopeSync`
- `ThemeBootstrap`
- `AccessibilityDomSync`
- `AccessibilityHotkeys`

### `dashboard/`

Famille widgets analytiques et progression.

Sous-familles notables :

- charts : `CategoryAccuracyChart`, `DashboardCategoryRadarChart`, `ProgressChart`, `DailyExercisesChart`, `VolumeByTypeChart`
- widgets : `LevelIndicator`, `LeaderboardWidget`, `SpacedRepetitionSummaryWidget`, `ChallengesProgressWidget`
- sections : `DashboardOverviewSection`, `DashboardProgressSection`, `DashboardRecommendationsSection`, `DashboardProfileSection`

### `challenges/`

Famille solver defi et renderers visuels.

Sous-familles notables :

- shell solver : `ChallengeSolver`, `ChallengeSolverHeader`, `ChallengeSolverContent`, `ChallengeSolverFeedback`
- command bar : `ChallengeSolverCommandBar` + blocs specialises
- renderers visuels : `visualizations/VisualRenderer`, `PatternRenderer`, `SequenceRenderer`, `PuzzleRenderer`, `ProbabilityRenderer`, `GraphRenderer`, `ChessRenderer`, `SymmetryRenderer`

### `exercises/`

Famille solver exercice et cartes catalogue.

Composants pivots :

- `ExerciseCard`
- `ExerciseSolver`
- `ExerciseSolverHeader`
- `ExerciseSolverChoices`
- `ExerciseSolverFeedback`
- `ExerciseModal`
- `AIGenerator`
- `UnifiedExerciseGenerator`

### `badges/`

Famille badges et progression meta.

Sous-familles notables :

- presentation de badge : `BadgeCard`, `BadgeIcon`, `BadgeGrid`
- sections page : `BadgesCollectionSection`, `BadgesProgressTabsSection`, `BadgesClosestSection`, `BadgesLastExploitsSection`

### `admin/`

Famille backoffice.

Points structurants :

- `AdminReadHeavyPageShell`
- `AdminStatePanel`
- `admin/content/` pour les sections contenu admin

### `shared/`

Famille cross-domaine.

Composants pivots :

- `ContentCardBase`
- `ContentListProgressiveFilterToolbar`
- `ContentListResultsSection`
- `ContentListSkeleton`
- `ContentListViewModeToggle`
- `SolverFocusBoard`

---

## Composants publics a connaitre en premier

Si on touche les surfaces majeures du produit, lire d'abord :

- `frontend/components/layout/Header.tsx`
- `frontend/components/providers/Providers.tsx`
- `frontend/components/chat/ChatbotFloatingGlobal.tsx`
- `frontend/components/dashboard/SpacedRepetitionSummaryWidget.tsx`
- `frontend/components/challenges/ChallengeSolver.tsx`
- `frontend/components/challenges/visualizations/VisualRenderer.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `frontend/components/badges/BadgeCard.tsx`
- `frontend/components/profile/ProfileLearningPreferencesSection.tsx`
- `frontend/components/settings/SettingsSecuritySection.tsx`
- `frontend/components/admin/AdminReadHeavyPageShell.tsx`

---

## Regles d'entretien

1. Toute nouvelle famille de composants doit vivre dans le bucket metier le plus proche, pas en racine par defaut.
2. Les coques runtime doivent rester minces ; la logique doit vivre dans les hooks/controllers et helpers `lib/`.
3. Les tests Vitest doivent etre co-localises a cote des composants sources.
4. Les anciens redirects `docs/06-WIDGETS/` ne sont plus actifs ; la doc widgets canonique est `docs/04-FRONTEND/DASHBOARD_WIDGETS/`.
