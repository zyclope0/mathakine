# Catalogue des composants React â€” Mathakine

> Scope : `frontend/components/`
> Updated : 2026-04-06
> Source : audit rÃ©pertoire + ARCHITECTURE.md

---

## Vue d'ensemble

**158 composants TSX** repartis en 23 categories.
Tous les composants sont `"use client"` sauf indication contraire.

---

## CatÃ©gories

| CatÃ©gorie    | Dossier          | Composants | RÃ´le                                    |
| ------------- | ---------------- | ---------- | ---------------------------------------- |
| UI de base    | `ui/`            | 21         | Primitives shadcn/ui (Radix)             |
| Dashboard     | `dashboard/`     | 28         | Widgets stats et visualisations          |
| DÃ©fis        | `challenges/`    | 23         | Interface dÃ©fis logiques                |
| Layout        | `layout/`        | 12         | Structure de page                        |
| Admin         | `admin/`         | 7          | Modales CRUD backoffice                  |
| Spatial       | `spatial/`       | 6          | Animations et decor theme-aware          |
| Exercices     | `exercises/`     | 9          | Interface exercices                      |
| Shared        | `shared/`        | 9          | Composants cross-domaine                 |
| Providers     | `providers/`     | 4          | Contextes React globaux                  |
| Home          | `home/`          | 4          | Page d'accueil                           |
| Badges        | `badges/`        | 11         | Domaine badges et sections de page       |
| Profile       | `profile/`       | 6          | Sections et navigation de la page profil |
| Chat          | `chat/`          | 3          | Chatbot assistant                        |
| Locale        | `locale/`        | 2          | SÃ©lecteur langue + init                 |
| Theme         | `theme/`         | 2          | ThemeSelectorCompact + DarkModeToggle    |
| Accessibility | `accessibility/` | 2          | Toolbar + audit WCAG                     |
| Auth          | `auth/`          | 1          | ProtectedRoute                           |
| Diagnostic    | `diagnostic/`    | 1          | Composant diagnostic                     |
| Feedback      | `feedback/`      | 1          | FAB retour utilisateur                   |
| Settings      | `settings/`      | 1          | Formulaire paramÃ¨tres                   |
| PWA           | `pwa/`           | 1          | Prompt installation                      |
| Learner       | `learner/`       | 2          | LearnerCard + LearnerLayout              |
| Racine        | `components/`    | 2          | LogoMathakine, LogoBadge                 |

---

## `ui/` â€” Primitives shadcn/ui

Composants Radix UI wrappÃ©s avec Tailwind. Ne pas modifier directement â€” rÃ©gÃ©nÃ©rer via `npx shadcn-ui`.

| Composant                                         | Usage                                                    |
| ------------------------------------------------- | -------------------------------------------------------- |
| `Button`                                          | Bouton (variants : default, outline, ghost, destructive) |
| `Card`, `CardHeader`, `CardContent`, `CardFooter` | Conteneur carte                                          |
| `Dialog`                                          | Modale/dialog accessible                                 |
| `Input`                                           | Champ de saisie                                          |
| `Select`                                          | SÃ©lecteur dropdown                                      |
| `Textarea`                                        | Zone de texte                                            |
| `Tabs`                                            | Navigation par onglets                                   |
| `Badge`                                           | Ã‰tiquette/pastille                                      |
| `Progress`                                        | Barre de progression                                     |
| `Skeleton`                                        | Placeholder chargement                                   |
| `Tooltip`                                         | Info-bulle                                               |
| `Separator`                                       | Ligne de sÃ©paration                                     |
| `Switch`                                          | Toggle on/off                                            |
| `Label`                                           | Label formulaire                                         |
| `Pagination`                                      | ContrÃ´les pagination                                    |
| `Sonner`                                          | Toasts (via sonner)                                      |
| `Dropdown-menu`                                   | Menu contextuel                                          |
| `Feedback`                                        | Composant feedback interne                               |
| `GrowthMindsetHint`                               | Encart pedagogique                                       |
| `MathText`                                        | Rendu LaTeX/mathÃ©matiques                               |
| `UserAvatar`                                      | Avatar utilisateur avec initiales                        |

---

## `dashboard/` â€” Widgets (28)

| Composant                                         | RÃ´le                                               |
| ------------------------------------------------- | --------------------------------------------------- |
| `StatsCard`                                       | Carte stat gÃ©nÃ©rique (valeur + libellÃ© + icÃ´ne) |
| `ProgressChart` / `ProgressChartLazy`             | Courbe progression dans le temps                    |
| `DailyExercisesChart` / `DailyExercisesChartLazy` | Histogramme exercices quotidiens                    |
| `DashboardCategoryRadarChart`                     | Radar par type d'exercice                           |
| `VolumeByTypeChart` / `VolumeByTypeChartLazy`     | Volume par catÃ©gorie                               |
| `CategoryAccuracyChart`                           | PrÃ©cision par catÃ©gorie                           |
| `PerformanceByType`                               | Performance dÃ©taillÃ©e par type                    |
| `AverageTimeWidget`                               | Temps moyen de rÃ©solution                          |
| `StreakWidget`                                    | SÃ©rie de jours consÃ©cutifs                        |
| `ChallengesProgressWidget`                        | Progression dÃ©fis                                  |
| `DailyChallengesWidget`                           | DÃ©fis du jour                                      |
| `LeaderboardWidget`                               | Mini-classement dashboard                           |
| `LevelIndicator`                                  | Indicateur niveau et XP                             |
| `LevelEstablishedWidget`                          | Confirmation passage de niveau                      |
| `ProgressTimelineWidget`                          | Chronologie des Ã©vÃ©nements                        |
| `PracticeConsistencyWidget`                       | RÃ©gularitÃ© de pratique                            |
| `Recommendations`                                 | Recommandations exercices et dÃ©fis                 |
| `QuickStartActions`                               | Actions rapides (page accueil)                      |
| `RecentActivity`                                  | Flux d'activitÃ© rÃ©cente                           |
| `SpacedRepetitionSummaryWidget`                   | Resume F04 + CTA `Reviser maintenant`               |
| `ExportButton`                                    | Export PDF / Excel                                  |
| `TimeRangeSelector`                               | Filtre temporel (7j / 30j / 90j)                    |
| `DashboardDataScopeBadge`                         | Badge scope des donnÃ©es affichÃ©es                 |
| `DashboardSkeletons`                              | Skeletons chargement dashboard                      |

---

## `challenges/` â€” DÃ©fis logiques (23)

| Composant                            | RÃ´le                                       |
| ------------------------------------ | ------------------------------------------- |
| `ChallengeCard`                      | Carte dÃ©fi (liste)                         |
| `ChallengeSolver`                    | Orchestrateur mince du solver de dÃ©fi      |
| `ChallengeSolverStatus`              | Etats loading / error / not-found           |
| `ChallengeSolverHeader`              | Retour, titre, badges                       |
| `ChallengeSolverContent`             | Enonce, image, renderer visuel              |
| `ChallengeSolverHintsPanel`          | Liste des indices reveles                   |
| `ChallengeSolverFeedback`            | Feedback post-submit + actions              |
| `ChallengeSolverCommandBar`          | Zone de reponse multi-mode                  |
| `ChallengeSolverHint`                | Hint premiere visite non bloquant           |
| `ChallengeModal`                     | Modale d'affichage dÃ©fi                    |
| `AIGenerator`                        | GÃ©nÃ©ration IA de dÃ©fis via SSE           |
| `visualizations/VisualRenderer`      | Dispatcher vers les renderers spÃ©cialisÃ©s |
| `visualizations/PatternRenderer`     | Rendu patterns (formes, motifs)             |
| `visualizations/SequenceRenderer`    | Rendu suites logiques                       |
| `visualizations/DeductionRenderer`   | Grilles de dÃ©duction                       |
| `visualizations/PuzzleRenderer`      | Puzzles interactifs                         |
| `visualizations/RiddleRenderer`      | Ã‰nigmes textuelles                         |
| `visualizations/ProbabilityRenderer` | ProbabilitÃ©s visuelles                     |
| `visualizations/GraphRenderer`       | Graphes                                     |
| `visualizations/CodingRenderer`      | Codage/dÃ©cryptage                          |
| `visualizations/ChessRenderer`       | ProblÃ¨mes d'Ã©checs                        |
| `visualizations/CustomRenderer`      | Rendu personnalisÃ©                         |
| `visualizations/SymmetryRenderer`    | SymÃ©tries gÃ©omÃ©triques                   |

---

## `badges/` â€” Domaine badges (11)

| Composant                    | RÃ´le                                                |
| ---------------------------- | ---------------------------------------------------- |
| `BadgeCard`                  | Carte badge unitaire (earned, locked, progress, pin) |
| `BadgeGrid`                  | Grille de badges                                     |
| `BadgeIcon`                  | IcÃ´ne / visuel de badge                             |
| `BadgesHeaderStats`          | Barre stats condensÃ©e sous le PageHeader            |
| `BadgesMotivationBanner`     | Bandeau motivationnel badges                         |
| `BadgesLastExploitsSection`  | Vitrine des derniers badges obtenus                  |
| `BadgesClosestSection`       | Badges les plus proches du dÃ©blocage                |
| `BadgesFiltersBar`           | Barre filtres + tri + reset                          |
| `BadgesCollectionSection`    | Collection obtenue + collapse + pin                  |
| `BadgesProgressTabsSection`  | Onglets badges en cours / a dÃ©bloquer               |
| `BadgesDetailedStatsSection` | Stats detaillÃ©es repliables                         |

---

## `profile/` â€” Domaine profil (6)

| Composant                           | RÃ´le                                                          |
| ----------------------------------- | -------------------------------------------------------------- |
| `ProfileSidebarNav`                 | Navigation desktop/mobile entre profil, accessibilite et stats |
| `ProfilePersonalInfoSection`        | Edition/lecture des informations personnelles                  |
| `ProfileLearningPreferencesSection` | Edition/lecture des preferences d'apprentissage                |
| `ProfileSecuritySection`            | Changement de mot de passe et visibilite des champs            |
| `ProfileAccessibilitySection`       | Theme et toggles accessibilite                                 |
| `ProfileStatisticsSection`          | Stats, activite recente et badges recents                      |

---

## `layout/` â€” Structure de page (12)

| Composant            | RÃ´le                                       |
| -------------------- | ------------------------------------------- |
| `PageLayout`         | Conteneur racine de page                    |
| `PageHeader`         | En-tÃªte de page (titre + actions)          |
| `PageSection`        | Section de page avec sÃ©parateur            |
| `PageGrid`           | Grille responsive pour les cartes           |
| `Header`             | Navigation principale (desktop + mobile)    |
| `Footer`             | Pied de page                                |
| `EmptyState`         | Ã‰tat vide gÃ©nÃ©rique (illustration + CTA) |
| `LoadingState`       | Ã‰tat de chargement gÃ©nÃ©rique             |
| `PageTransition`     | Animation de transition entre pages         |
| `AlphaBanner`        | BanniÃ¨re version alpha                     |
| `UnverifiedBanner`   | Bandeau email non vÃ©rifiÃ©                 |
| `MaintenanceOverlay` | Overlay maintenance                         |

---

## `shared/` â€” Cross-domaine (9)

| Composant                             | RÃ´le                                            |
| ------------------------------------- | ------------------------------------------------ |
| `AIGeneratorBase`                     | Base UI partagÃ©e exercices + dÃ©fis AIGenerator |
| `aiGeneratorSharedUi`                 | Helpers UI partagÃ©s des generateurs             |
| `ContentCardBase`                     | Base commune pour ExerciseCard et ChallengeCard  |
| `CompactListItem`                     | Ligne de liste compacte (rÃ©sultats, activitÃ©)  |
| `ContentListProgressiveFilterToolbar` | Toolbar filtres progressive                      |
| `ContentListSkeleton`                 | Skeleton pour listes de contenu                  |
| `ContentListViewModeToggle`           | Bascule grille / liste                           |
| `ListLoadingShells`                   | Shells de chargement pour liste paginÃ©e         |
| `SolverFocusBoard`                    | Conteneur calme pour surfaces solver apprenant   |

---

## `exercises/` â€” Exercices (9)

| Composant                  | RÃ´le                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------- |
| `ExerciseCard`             | Carte exercice (liste)                                                             |
| `ExerciseSolver`           | Interface de rÃ©solution d'un exercice, y compris `interleaved` et `spaced-review` |
| `ExerciseSolverHeader`     | En-tete solver exercice                                                            |
| `ExerciseSolverChoices`    | Bloc de reponse exercice                                                           |
| `ExerciseSolverFeedback`   | Feedback post-reponse exercice                                                     |
| `ExerciseSolverHint`       | Hint premiere visite du solver                                                     |
| `ExerciseModal`            | Modale d'affichage exercice                                                        |
| `AIGenerator`              | GÃ©nÃ©ration IA d'exercices via SSE                                                |
| `UnifiedExerciseGenerator` | GÃ©nÃ©ration unifiÃ©e exercices (wrapper)                                          |

---

## `providers/` â€” Contextes globaux (4)

| Composant          | RÃ´le                             |
| ------------------ | --------------------------------- |
| `QueryProvider`    | TanStack Query (cache API global) |
| `ThemeProvider`    | ThÃ¨me actif (lit `themeStore`)   |
| `NextIntlProvider` | Internationalisation next-intl    |
| `AccessScopeSync`  | Sync local des scopes d'acces     |

---

## `spatial/` â€” Animations thÃ¨me (6)

| Composant           | RÃ´le                                                          |
| ------------------- | -------------------------------------------------------------- |
| `SpatialBackground` | Fond Ã©toilÃ© animÃ© (canvas)                                  |
| `Starfield`         | Champ d'Ã©toiles paramÃ©trable                                 |
| `Planet`            | PlanÃ¨te 3D dÃ©corative                                        |
| `Particles`         | SystÃ¨me de particules                                         |
| `DinoFloating`      | Mascotte flottante (accessibilitÃ© : `prefers-reduced-motion`) |
| `UnicornFloating`   | Mascotte thÃ©matique additionnelle                             |

---

## `admin/` â€” Backoffice (7)

| Composant                | RÃ´le                                               |
| ------------------------ | --------------------------------------------------- |
| `ExerciseModal` (admin)  | CRUD exercice                                       |
| `ChallengeModal` (admin) | CRUD dÃ©fi                                          |
| `BadgeModal` (admin)     | CRUD badge                                          |
| _(+4)_                   | Modales utilisateurs, sessions, config, modÃ©ration |

---

## Conventions

### Importer `cn`

```tsx
// âœ… toujours depuis @/lib/utils
import { cn } from "@/lib/utils";

// âŒ pas depuis @/lib/utils/cn directement
```

### Props obligatoires et patterns

- Les cartes (`ExerciseCard`, `ChallengeCard`) utilisent `ContentCardBase` comme base commune.
- Les listes paginÃ©es utilisent `ContentListSkeleton` + `ListLoadingShells` pour les Ã©tats de chargement.
- Les composants AIGenerator (exercices et dÃ©fis) partagent `AIGeneratorBase` pour l'interface, mais appellent des hooks sÃ©parÃ©s.
- Les solveurs complexes sont maintenant traites comme des shells composes :
  - container
  - blocs visuels purs
  - hook runtime dedie

### AccessibilitÃ©

- Tous les composants d'animation respectent `prefers-reduced-motion`.
- `AccessibilityToolbar` expose 5 modes (contraste, taille, espacement, animations, focus visible).
- `WCAGAudit` est un composant dev-only, non rendu en production.
