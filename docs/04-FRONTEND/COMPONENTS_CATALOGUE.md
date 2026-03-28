# Catalogue des composants React — Mathakine

> Scope : `frontend/components/`
> Updated : 2026-03-27
> Source : audit répertoire + ARCHITECTURE.md

---

## Vue d'ensemble

**125 composants TSX** répartis en 21 catégories.
Tous les composants sont `"use client"` sauf indication contraire.

---

## Catégories

| Catégorie | Dossier | Composants | Rôle |
|-----------|---------|-----------|------|
| UI de base | `ui/` | 21 | Primitives shadcn/ui (Radix) |
| Dashboard | `dashboard/` | 26 | Widgets stats et visualisations |
| Défis | `challenges/` | 16 | Interface défis logiques |
| Layout | `layout/` | 12 | Structure de page |
| Admin | `admin/` | 7 | Modales CRUD backoffice |
| Spatial | `spatial/` | 5 | Animations thème spatial |
| Exercices | `exercises/` | 5 | Interface exercices |
| Shared | `shared/` | 6 | Composants cross-domaine |
| Providers | `providers/` | 4 | Contextes React globaux |
| Home | `home/` | 4 | Page d'accueil |
| Badges | `badges/` | 3 | Affichage badges |
| Chat | `chat/` | 3 | Chatbot assistant |
| Locale | `locale/` | 2 | Sélecteur langue + init |
| Theme | `theme/` | 2 | Sélecteur thème |
| Accessibility | `accessibility/` | 2 | Toolbar + audit WCAG |
| Auth | `auth/` | 1 | ProtectedRoute |
| Diagnostic | `diagnostic/` | 1 | Composant diagnostic |
| Feedback | `feedback/` | 1 | FAB retour utilisateur |
| Settings | `settings/` | 1 | Formulaire paramètres |
| PWA | `pwa/` | 1 | Prompt installation |
| Racine | `components/` | 2 | LogoMathakine, LogoBadge |

---

## `ui/` — Primitives shadcn/ui

Composants Radix UI wrappés avec Tailwind. Ne pas modifier directement — régénérer via `npx shadcn-ui`.

| Composant | Usage |
|-----------|-------|
| `Button` | Bouton (variants : default, outline, ghost, destructive) |
| `Card`, `CardHeader`, `CardContent`, `CardFooter` | Conteneur carte |
| `Dialog` | Modale/dialog accessible |
| `Input` | Champ de saisie |
| `Select` | Sélecteur dropdown |
| `Textarea` | Zone de texte |
| `Tabs` | Navigation par onglets |
| `Badge` | Étiquette/pastille |
| `Progress` | Barre de progression |
| `Skeleton` | Placeholder chargement |
| `Tooltip` | Info-bulle |
| `Separator` | Ligne de séparation |
| `Switch` | Toggle on/off |
| `Label` | Label formulaire |
| `Pagination` | Contrôles pagination |
| `Sonner` | Toasts (via sonner) |
| `Dropdown-menu` | Menu contextuel |
| `Feedback` | Composant feedback interne |
| `GrowthMindsetHint` | Encart pedagogique |
| `MathText` | Rendu LaTeX/mathématiques |
| `UserAvatar` | Avatar utilisateur avec initiales |

---

## `dashboard/` — Widgets (26)

| Composant | Rôle |
|-----------|------|
| `StatsCard` | Carte stat générique (valeur + libellé + icône) |
| `ProgressChart` / `ProgressChartLazy` | Courbe progression dans le temps |
| `DailyExercisesChart` / `DailyExercisesChartLazy` | Histogramme exercices quotidiens |
| `DashboardCategoryRadarChart` | Radar par type d'exercice |
| `VolumeByTypeChart` / `VolumeByTypeChartLazy` | Volume par catégorie |
| `CategoryAccuracyChart` | Précision par catégorie |
| `PerformanceByType` | Performance détaillée par type |
| `AverageTimeWidget` | Temps moyen de résolution |
| `StreakWidget` | Série de jours consécutifs |
| `ChallengesProgressWidget` | Progression défis |
| `DailyChallengesWidget` | Défis du jour |
| `LeaderboardWidget` | Mini-classement dashboard |
| `LevelIndicator` | Indicateur niveau et XP |
| `LevelEstablishedWidget` | Confirmation passage de niveau |
| `ProgressTimelineWidget` | Chronologie des événements |
| `PracticeConsistencyWidget` | Régularité de pratique |
| `Recommendations` | Recommandations exercices et défis |
| `QuickStartActions` | Actions rapides (page accueil) |
| `RecentActivity` | Flux d'activité récente |
| `ExportButton` | Export PDF / Excel |
| `TimeRangeSelector` | Filtre temporel (7j / 30j / 90j) |
| `DashboardDataScopeBadge` | Badge scope des données affichées |
| `DashboardSkeletons` | Skeletons chargement dashboard |

---

## `challenges/` — Défis logiques (16)

| Composant | Rôle |
|-----------|------|
| `ChallengeCard` | Carte défi (liste) |
| `ChallengeSolver` | Interface de résolution d'un défi |
| `ChallengeModal` | Modale d'affichage défi |
| `AIGenerator` | Génération IA de défis via SSE |
| `visualizations/VisualRenderer` | Dispatcher vers les renderers spécialisés |
| `visualizations/PatternRenderer` | Rendu patterns (formes, motifs) |
| `visualizations/SequenceRenderer` | Rendu suites logiques |
| `visualizations/DeductionRenderer` | Grilles de déduction |
| `visualizations/PuzzleRenderer` | Puzzles interactifs |
| `visualizations/RiddleRenderer` | Énigmes textuelles |
| `visualizations/ProbabilityRenderer` | Probabilités visuelles |
| `visualizations/GraphRenderer` | Graphes |
| `visualizations/CodingRenderer` | Codage/décryptage |
| `visualizations/ChessRenderer` | Problèmes d'échecs |
| `visualizations/CustomRenderer` | Rendu personnalisé |
| `visualizations/SymmetryRenderer` | Symétries géométriques |

---

## `layout/` — Structure de page (12)

| Composant | Rôle |
|-----------|------|
| `PageLayout` | Conteneur racine de page |
| `PageHeader` | En-tête de page (titre + actions) |
| `PageSection` | Section de page avec séparateur |
| `PageGrid` | Grille responsive pour les cartes |
| `Header` | Navigation principale (desktop + mobile) |
| `Footer` | Pied de page |
| `EmptyState` | État vide générique (illustration + CTA) |
| `LoadingState` | État de chargement générique |
| `PageTransition` | Animation de transition entre pages |
| `AlphaBanner` | Bannière version alpha |
| `UnverifiedBanner` | Bandeau email non vérifié |
| `MaintenanceOverlay` | Overlay maintenance |

---

## `shared/` — Cross-domaine (6)

| Composant | Rôle |
|-----------|------|
| `AIGeneratorBase` | Base UI partagée exercices + défis AIGenerator |
| `ContentCardBase` | Base commune pour ExerciseCard et ChallengeCard |
| `CompactListItem` | Ligne de liste compacte (résultats, activité) |
| `ContentListProgressiveFilterToolbar` | Toolbar filtres progressive (type, difficulté, âge) |
| `ContentListSkeleton` | Skeleton pour listes de contenu |
| `ListLoadingShells` | Shells de chargement pour liste paginée |

---

## `exercises/` — Exercices (5)

| Composant | Rôle |
|-----------|------|
| `ExerciseCard` | Carte exercice (liste) |
| `ExerciseSolver` | Interface de résolution d'un exercice |
| `ExerciseModal` | Modale d'affichage exercice |
| `AIGenerator` | Génération IA d'exercices via SSE |
| `UnifiedExerciseGenerator` | Génération unifiée exercices (wrapper) |

---

## `providers/` — Contextes globaux (4)

| Composant | Rôle |
|-----------|------|
| `QueryProvider` | TanStack Query (cache API global) |
| `ThemeProvider` | Thème actif (lit `themeStore`) |
| `IntlProvider` | Internationalisation next-intl |
| *(4e)* | Provider Sentry ou autre |

---

## `spatial/` — Animations thème (5)

| Composant | Rôle |
|-----------|------|
| `SpatialBackground` | Fond étoilé animé (canvas) |
| `Starfield` | Champ d'étoiles paramétrable |
| `Planet` | Planète 3D décorative |
| `Particles` | Système de particules |
| `DinoFloating` | Mascotte flottante (accessibilité : `prefers-reduced-motion`) |

---

## `admin/` — Backoffice (7)

| Composant | Rôle |
|-----------|------|
| `ExerciseModal` (admin) | CRUD exercice |
| `ChallengeModal` (admin) | CRUD défi |
| `BadgeModal` (admin) | CRUD badge |
| *(+4)* | Modales utilisateurs, sessions, config, modération |

---

## Conventions

### Importer `cn`

```tsx
// ✅ toujours depuis @/lib/utils
import { cn } from "@/lib/utils";

// ❌ pas depuis @/lib/utils/cn directement
```

### Props obligatoires et patterns

- Les cartes (`ExerciseCard`, `ChallengeCard`) utilisent `ContentCardBase` comme base commune.
- Les listes paginées utilisent `ContentListSkeleton` + `ListLoadingShells` pour les états de chargement.
- Les composants AIGenerator (exercices et défis) partagent `AIGeneratorBase` pour l'interface, mais appellent des hooks séparés.

### Accessibilité

- Tous les composants d'animation respectent `prefers-reduced-motion`.
- `AccessibilityToolbar` expose 5 modes (contraste, taille, espacement, animations, focus visible).
- `WCAGAudit` est un composant dev-only, non rendu en production.
