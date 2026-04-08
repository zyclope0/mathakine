# Catalogue des composants React â€” Mathakine

> Scope : `frontend/components/`
> Updated : 2026-04-08 (FFI-L20C auth/providers)
> Source : audit rÃ©pertoire + ARCHITECTURE.md

---

## Vue d'ensemble

**199 composants TSX** repartis en 23 categories.
Tous les composants sont `"use client"` sauf indication contraire.

---

## CatÃ©gories

| CatÃ©gorie    | Dossier          | Composants | RÃ´le                                                             |
| ------------- | ---------------- | ---------- | ----------------------------------------------------------------- |
| UI de base    | `ui/`            | 21         | Primitives shadcn/ui (Radix)                                      |
| Dashboard     | `dashboard/`     | 34         | Widgets stats, visualisations et tabs sections                    |
| DÃ©fis        | `challenges/`    | 30         | Interface dÃ©fis logiques + sous-blocs command bar (FFI-L18B)     |
| Layout        | `layout/`        | 15         | Structure de page                                                 |
| Admin         | `admin/`         | 12         | Modales CRUD + sections page contenu admin                        |
| Spatial       | `spatial/`       | 6          | Animations et decor theme-aware                                   |
| Exercices     | `exercises/`     | 9          | Interface exercices                                               |
| Shared        | `shared/`        | 15         | Composants cross-domaine                                          |
| Providers     | `providers/`     | 7          | Composition racine (FFI-L20C) : `Providers`, `ThemeBootstrap`, `AccessibilityDomSync`, `AccessibilityHotkeys`, `AuthSyncProvider`, `AccessScopeSync`, `NextIntlProvider` |
| Home          | `home/`          | 2          | Page d'accueil (Chatbot embarquÃ©, widgets)                       |
| Badges        | `badges/`        | 11         | Domaine badges et sections de page                                |
| Profile       | `profile/`       | 12         | Sections profil + sous-blocs préférences apprentissage (FFI-L18A) |
| Chat          | `chat/`          | 5          | Shell drawer global + UI messages / composer                      |
| Locale        | `locale/`        | 2          | SÃ©lecteur langue + init                                          |
| Theme         | `theme/`         | 2          | ThemeSelectorCompact + DarkModeToggle                             |
| Accessibility | `accessibility/` | 2          | Toolbar + audit WCAG                                              |
| Auth          | `auth/`          | 1          | ProtectedRoute                                                    |
| Diagnostic    | `diagnostic/`    | 1          | Composant diagnostic                                              |
| Feedback      | `feedback/`      | 1          | FAB retour utilisateur                                            |
| Settings      | `settings/`      | 6          | Page paramÃ¨tres (sections + SaveButton)                          |
| PWA           | `pwa/`           | 1          | Prompt installation                                               |
| Learner       | `learner/`       | 2          | LearnerCard + LearnerLayout                                       |
| Racine        | `components/`    | 2          | LogoMathakine, LogoBadge                                          |

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

## `dashboard/` â€” Widgets (34)

| Composant                                         | RÃ´le                                                    |
| ------------------------------------------------- | -------------------------------------------------------- |
| `StatsCard`                                       | Carte stat gÃ©nÃ©rique (valeur + libellÃ© + icÃ´ne)      |
| `ProgressChart` / `ProgressChartLazy`             | Courbe progression dans le temps                         |
| `DailyExercisesChart` / `DailyExercisesChartLazy` | Histogramme exercices quotidiens                         |
| `DashboardCategoryRadarChart`                     | Radar par type d'exercice                                |
| `VolumeByTypeChart` / `VolumeByTypeChartLazy`     | Volume par catÃ©gorie                                    |
| `CategoryAccuracyChart`                           | PrÃ©cision par catÃ©gorie                                |
| `PerformanceByType`                               | Performance dÃ©taillÃ©e par type                         |
| `AverageTimeWidget`                               | Temps moyen de rÃ©solution                               |
| `StreakWidget`                                    | SÃ©rie de jours consÃ©cutifs                             |
| `ChallengesProgressWidget`                        | Progression dÃ©fis                                       |
| `DailyChallengesWidget`                           | DÃ©fis du jour                                           |
| `LeaderboardWidget`                               | Mini-classement dashboard                                |
| `LevelIndicator`                                  | Indicateur niveau et XP                                  |
| `LevelEstablishedWidget`                          | Confirmation passage de niveau                           |
| `ProgressTimelineWidget`                          | Chronologie des Ã©vÃ©nements                             |
| `PracticeConsistencyWidget`                       | RÃ©gularitÃ© de pratique                                 |
| `Recommendations`                                 | Recommandations exercices et dÃ©fis                      |
| `QuickStartActions`                               | Actions rapides (page accueil)                           |
| `RecentActivity`                                  | Flux d'activitÃ© rÃ©cente                                |
| `SpacedRepetitionSummaryWidget`                   | Resume F04 + CTA `Reviser maintenant`                    |
| `ExportButton`                                    | Export PDF / Excel                                       |
| `TimeRangeSelector`                               | Filtre temporel (7j / 30j / 90j)                         |
| `DashboardDataScopeBadge`                         | Badge scope des donnÃ©es affichÃ©es                      |
| `DashboardSkeletons`                              | Skeletons chargement dashboard                           |
| `DashboardLastUpdate`                             | Date relative de derniÃ¨re activitÃ©                     |
| `DashboardTabsNav`                                | Navigation par onglets du dashboard                      |
| `DashboardOverviewSection`                        | Section vue d'ensemble (actions + rÃ©pÃ©tition + sÃ©rie) |
| `DashboardRecommendationsSection`                 | Section recommandations                                  |
| `DashboardProgressSection`                        | Section progression (timeline + charts)                  |
| `DashboardProfileSection`                         | Section profil (niveau, stats, activitÃ©)                |

---

## `challenges/` â€” DÃ©fis logiques (30)

| Composant                            | RÃ´le                                         |
| ------------------------------------ | --------------------------------------------- |
| `ChallengeCard`                      | Carte dÃ©fi (liste)                           |
| `ChallengeSolver`                    | Orchestrateur mince du solver de dÃ©fi        |
| `ChallengeSolverStatus`              | Etats loading / error / not-found             |
| `ChallengeSolverHeader`              | Retour, titre, badges                         |
| `ChallengeSolverContent`             | Enonce, image, renderer visuel                |
| `ChallengeSolverHintsPanel`          | Liste des indices reveles                     |
| `ChallengeSolverFeedback`            | Feedback post-submit + actions                |
| `ChallengeSolverCommandBar`          | FaÃ§ade zone de reponse multi-mode (FFI-L18B) |
| `ChallengeSolverCommandBarTypes`     | Types partagÃ©s traduction command bar        |
| `ChallengeSolverMcqGrid`             | Grille QCM / radiogroup                       |
| `ChallengeSolverVisualButtons`       | Choix visuels simple / multi-position         |
| `ChallengeSolverOrderPuzzleBlock`    | Bloc ordre puzzle + champ figÃ©               |
| `ChallengeSolverGridAutoAnswerBlock` | RÃ©ponse auto sÃ©quence / pattern (grille)    |
| `ChallengeSolverGridDeductionBlock`  | RÃ©sumÃ© associations dÃ©duction              |
| `ChallengeSolverFreeTextAnswerBlock` | Saisie texte libre + raccourci EntrÃ©e        |
| `ChallengeSolverValidateActions`     | Valider + indice + hint texte                 |
| `ChallengeSolverHint`                | Hint premiere visite non bloquant             |
| `ChallengeModal`                     | Modale d'affichage dÃ©fi                      |
| `AIGenerator`                        | GÃ©nÃ©ration IA de dÃ©fis via SSE             |
| `visualizations/VisualRenderer`      | Dispatcher vers les renderers spÃ©cialisÃ©s   |
| `visualizations/PatternRenderer`     | Rendu patterns (formes, motifs)               |
| `visualizations/SequenceRenderer`    | Rendu suites logiques                         |
| `visualizations/DeductionRenderer`   | Grilles de dÃ©duction                         |
| `visualizations/PuzzleRenderer`      | Puzzles interactifs                           |
| `visualizations/RiddleRenderer`      | Ã‰nigmes textuelles                           |
| `visualizations/ProbabilityRenderer` | ProbabilitÃ©s visuelles                       |
| `visualizations/GraphRenderer`       | Graphes                                       |
| `visualizations/CodingRenderer`      | Codage/dÃ©cryptage                            |
| `visualizations/ChessRenderer`       | ProblÃ¨mes d'Ã©checs                          |
| `visualizations/CustomRenderer`      | Rendu personnalisÃ©                           |
| `visualizations/SymmetryRenderer`    | SymÃ©tries gÃ©omÃ©triques                     |

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

## `profile/` â€” Domaine profil (12)

| Composant                                     | RÃ´le                                                          |
| --------------------------------------------- | -------------------------------------------------------------- |
| `ProfileSidebarNav`                           | Navigation desktop/mobile entre profil, accessibilite et stats |
| `ProfilePersonalInfoSection`                  | Edition/lecture des informations personnelles                  |
| `ProfileLearningPreferencesSection`           | FaÃ§ade section prÃ©fÃ©rences (orchestre sous-blocs FFI-L18A)  |
| `ProfileLearningPreferencesHeader`            | En-tÃªte carte + bouton Modifier                               |
| `ProfileLearningPreferencesEditGradeBlock`    | Ã‰dition systÃ¨me / niveau / tranche d'Ã¢ge (unifiÃ©)          |
| `ProfileLearningPreferencesEditPedagogyBlock` | Ã‰dition style + difficultÃ© prÃ©fÃ©rÃ©e                       |
| `ProfileLearningPreferencesEditGoalsBlock`    | Ã‰dition objectif + rythme                                     |
| `ProfileLearningPreferencesEditActions`       | Annuler / Enregistrer + Ã©tat chargement                       |
| `ProfileLearningPreferencesReadSummary`       | Vue lecture des prÃ©fÃ©rences                                  |
| `ProfileSecuritySection`                      | Changement de mot de passe et visibilite des champs            |
| `ProfileAccessibilitySection`                 | Theme et toggles accessibilite                                 |
| `ProfileStatisticsSection`                    | Stats, activite recente et badges recents                      |

---

## `layout/` â€” Structure de page (15)

| Composant            | RÃ´le                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------- |
| `PageLayout`         | Conteneur racine de page                                                              |
| `PageHeader`         | En-tÃªte de page (titre + actions)                                                    |
| `PageSection`        | Section de page avec sÃ©parateur                                                      |
| `PageGrid`           | Grille responsive pour les cartes                                                     |
| `Header`             | FaÃ§ade navigation shell (orchestre sous-blocs)                                       |
| `HeaderDesktopNav`   | Nav primaire/secondaire desktop + CTA Assistant **si authentifie** (pas pour invites) |
| `HeaderUserMenu`     | Menu dÃ©roulant utilisateur (profil, admin, logout)                                   |
| `HeaderMobileMenu`   | Menu mobile animÃ© (nav + Assistant **si authentifie** + thÃ¨me)                      |
| `Footer`             | Pied de page                                                                          |
| `EmptyState`         | Ã‰tat vide gÃ©nÃ©rique (illustration + CTA)                                           |
| `LoadingState`       | Ã‰tat de chargement gÃ©nÃ©rique                                                       |
| `PageTransition`     | Animation de transition entre pages                                                   |
| `AlphaBanner`        | BanniÃ¨re version alpha                                                               |
| `UnverifiedBanner`   | Bandeau email non vÃ©rifiÃ©                                                           |
| `MaintenanceOverlay` | Overlay maintenance                                                                   |

**FFI-L16 (shell)** : invites publics — pas de CTA Assistant dans le header ; acces assistant via **FAB global** (`components/chat/ChatbotFloatingGlobal.tsx`). Authentifies : CTA header inchange.

---

## `chat/` â€” Assistant global & messages (5)

Ownership **FFI-L16** : UI drawer / FAB global sous `components/chat/` (distinct de la carte embarquee `home/Chatbot.tsx` sur la home marketing).

| Composant               | RÃ´le                                                   |
| ----------------------- | ------------------------------------------------------- |
| `ChatbotFloating`       | Shell drawer assistant (compose messages + composer)    |
| `ChatbotFloatingGlobal` | FAB + montage global du drawer (parcours public + auth) |
| `ChatMessagesView`      | Liste des messages                                      |
| `ChatComposer`          | Saisie utilisateur                                      |
| `ChatSuggestionsBar`    | Suggestions rapides                                     |

Quota **invite** : **5 messages** / session navigateur (`useGuestChatAccess`, sessionStorage), en complement du rate-limit **serveur** sur `/api/chat` (autorite backend inchangee).

---

## `shared/` â€” Cross-domaine (15)

| Composant                             | RÃ´le                                                                        |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| `AIGeneratorBase`                     | Base UI partagÃ©e exercices + dÃ©fis AIGenerator                             |
| `aiGeneratorSharedUi`                 | Helpers UI partagÃ©s des generateurs                                         |
| `ContentCardBase`                     | Base commune pour ExerciseCard et ChallengeCard                              |
| `CompactListItem`                     | Ligne de liste compacte (rÃ©sultats, activitÃ©)                              |
| `ContentListProgressiveFilterToolbar` | FaÃ§ade toolbar filtres progressive (orchestre sous-blocs)                   |
| `ContentListToolbarSearchRow`         | Ligne recherche + bouton panneau avancÃ©                                     |
| `ContentListToolbarTypeChips`         | Chips type inline (`showTypeChipsInline`)                                    |
| `ContentListToolbarSummary`           | RÃ©sumÃ© Ã©tat + chips critÃ¨res actifs                                      |
| `ContentListToolbarAdvancedPanel`     | Panneau Ã¢ge / tri / masquer rÃ©ussis / reset                                |
| `ContentListSkeleton`                 | Skeleton pour listes de contenu                                              |
| `ContentListViewModeToggle`           | Bascule grille / liste                                                       |
| `ContentListResultsHeader`            | Titre / compteur liste + toggle grille-liste                                 |
| `ContentListResultsSection`           | Coquille rÃ©sultats (erreur / chargement / vide / grille-liste / pagination) |
| `ListLoadingShells`                   | Shells de chargement pour liste paginÃ©e                                     |
| `SolverFocusBoard`                    | Conteneur calme pour surfaces solver apprenant                               |

---

## `exercises/` â€” Exercices (9)

| Composant                  | RÃ´le                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------- |
| `ExerciseCard`             | Carte exercice (liste)                                                             |
| `ExerciseSolver`           | Facade resolution exercice (`interleaved`, `spaced-review`) ; runtime `useExerciseSolverController` |
| `ExerciseSolverHeader`     | En-tete solver exercice                                                            |
| `ExerciseSolverChoices`    | Bloc de reponse exercice                                                           |
| `ExerciseSolverFeedback`   | Feedback post-reponse exercice                                                     |
| `ExerciseSolverHint`       | Hint premiere visite du solver                                                     |
| `ExerciseModal`            | Modale d'affichage exercice                                                        |
| `AIGenerator`              | GÃ©nÃ©ration IA d'exercices via SSE                                                |
| `UnifiedExerciseGenerator` | GÃ©nÃ©ration unifiÃ©e exercices (wrapper)                                          |

---

## `providers/` â€” Contextes globaux (7)

| Composant               | RÃ´le                                                     |
| ----------------------- | --------------------------------------------------------- |
| `Providers`             | Composition racine des providers frontend (FFI-L20C)      |
| `NextIntlProvider`      | Internationalisation next-intl                            |
| `AuthSyncProvider`      | Sync auth frontend / backend                              |
| `AccessScopeSync`       | Sync local des scopes d'acces                             |
| `ThemeBootstrap`        | Bootstrap thÃ¨me + application DOM                         |
| `AccessibilityDomSync`  | Sync classes a11y sur `documentElement`                   |
| `AccessibilityHotkeys`  | Raccourcis globaux accessibilitÃ© (Alt+*)                 |

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

## `admin/` â€” Backoffice

Modales CRUD : `ExerciseCreateModal`, `ExerciseEditModal`, `ChallengeCreateModal`, `ChallengeEditModal`, `BadgeCreateModal`, `BadgeEditModal`, `AdminAcademyStatsSection`.

### `admin/content/` â€” Page contenu (FFI-L14)

Shell `/admin/content` : onglets + domaines exercices / dÃ©fis / badges. Reliquat contrat/produit : difficulte liste exercices transitoire tant que la liste admin API ne garantit pas `difficulty_tier` ; modales exercices en valeurs legacy API.

| Composant                | RÃ´le                                   |
| ------------------------ | --------------------------------------- |
| `AdminContentTabsNav`    | Tabs shell uniquement (pas de fetch)    |
| `AdminExercisesSection`  | Liste + filtres + modales exercices     |
| `AdminChallengesSection` | Liste + filtres + modales dÃ©fis        |
| `AdminBadgesSection`     | Liste + filtres + modales badges        |
| `AdminContentSortIcon`   | IcÃ´ne tri colonnes (partagÃ© sections) |

---

## `settings/` â€” Page paramÃ¨tres (6)

Pattern FFI-L13 : `app/settings/page.tsx` (container) + `useSettingsPageController` + `lib/settings/settingsPage.ts`.

| Composant                      | RÃ´le                                             |
| ------------------------------ | ------------------------------------------------- |
| `SaveButton`                   | Bouton enregistrer (Ã©tats chargement)            |
| `SettingsSidebarNav`           | Select mobile + sidebar desktop (sections)        |
| `SettingsGeneralSection`       | Langue, fuseau, sauvegarde gÃ©nÃ©ral              |
| `SettingsNotificationsSection` | Interrupteurs notifications + sauvegarde          |
| `SettingsSecuritySection`      | ConfidentialitÃ© + sessions actives (rÃ©vocation) |
| `SettingsDataSection`          | Diagnostic, export donnÃ©es, suppression compte   |

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
