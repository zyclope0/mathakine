# Audit Frontend — Standardisation & Design System

> Généré le 2026-03-29 via `/octo:extract` (deep mode)
> Stack : Next.js 15 + TypeScript + Tailwind v4 + Radix UI
> Version frontend : 3.6.0-alpha.1

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Design Tokens](#2-design-tokens)
3. [Inventaire Composants](#3-inventaire-composants)
4. [Patterns de Layout](#4-patterns-de-layout)
5. [État du Thème Hybride](#5-état-du-thème-hybride)
6. [Inconsistances Prioritaires](#6-inconsistances-prioritaires)
7. [Chantiers de Standardisation](#7-chantiers-de-standardisation)

---

## 1. Vue d'ensemble

### Métriques globales

| Métrique               | Valeur                         |
| ---------------------- | ------------------------------ |
| Composants TSX         | 144                            |
| Fichiers de tests      | 76                             |
| Hooks custom           | 47                             |
| Routes Next.js         | 20+                            |
| Thèmes couleur         | 8                              |
| Animations keyframes   | 12                             |
| Variables CSS (tokens) | 80+                            |
| Couverture tokens      | ~82% (18% hardcodé edge cases) |
| Clés i18n fr+en        | ~2 000+                        |

### Points forts

- **Système de tokens CSS complet** : 80+ variables CSS dans `globals.css` (48 KB), couvrant 8 thèmes avec dark mode
- **Composants atomiques propres** : 24 composants UI headless (Radix UI) avec CVA variants
- **Accessibilité avancée** : 5 modes implémentés (large text, dyslexia, high contrast, reduced motion, TSA/TDAH)
- **TypeScript strict** : 0 `any` explicite dans les composants UI
- **i18n opérationnel** : fr/en complet avec next-intl

### Points faibles

- **Monolithes runtime/pages encore lourds** : plus de mega-page sur `app/admin/content/page.tsx` depuis FFI-L14 (container fin + sections) ; les surfaces les plus lourdes restantes sont surtout des composants (solver, toolbar, Header)
- **Plateforme content-list encore trop implicite** : toolbar, generators, cards, pagination et état liste restent dispersés entre `Exercises` et `Challenges`
- **Dette shell globale** : `Header.tsx` reste massif et le recouvrement `ChatbotFloating` / `ChatbotFloatingGlobal` n'est pas clarifié
- **Balayage visuel volontairement secondaire** : tokens/couleurs hardcodées existent encore, mais ne sont plus la priorité d'exécution tant que les seams d'architecture restent ouverts

---

### 1.1 État d'avancement réel — 2026-04-06

La photographie initiale reste utile, mais le plan actif a ete requalifie autour des seams d'architecture les plus rentables depuis
l'extraction du 2026-03-29 ; `FFI-L14` (admin content) est desormais livre cote architecture frontend et le prochain jalon prioritaire est `FFI-L15`.

**Livré, commité et poussé**

- `FFI-L1` : tokens critiques multi-thème (podium leaderboard + `primary-on-dark`)
- `FFI-L2` : consolidation auth / bootstrap API
- `FFI-L3` : couche storage typée et centralisée
- `FFI-L4` : DRY pages contenu exercices / défis
- `FFI-L5` : normalisation loading / skeletons
- `FFI-L6` : nettoyage legacy Star Wars safe
- `FFI-L7` : réduction du vrai recouvrement générateurs IA
- `FFI-L8` : préparation du split solver
- `FFI-L9` : split `ExerciseSolver`
- `FFI-L10` : split `ChallengeSolver`
- `FFI-L11` : modulariser `Profile` (container + `useProfilePageController` + sections)
- `FFI-L12` : modulariser `Badges` (container + `useBadgesPageController` + sections)
- `FFI-L13` : modulariser `Settings` (container ~`133` LOC + `useSettingsPageController` + `components/settings/*`)
- `FFI-L14` : decouper `Admin Content` (container ~`50` LOC + `components/admin/content/*` + shell controller)

**Encore ouverts (ordre actif révisé)**

- `FFI-L15` : standardiser la plateforme `content-list`
- `FFI-L16` : split `Header.tsx` + ownership chatbot flottant
- `FFI-L17` : garde-fous architecture / tests / doc runtime

**Conséquences visibles**

- `app/profile/page.tsx` n'est plus une mega-page : la surface est passee a un container fin (~`191` LOC) avec `useProfilePageController.ts`, `lib/profile/profilePage.ts` et `components/profile/*`.
- `app/settings/page.tsx` n'est plus une mega-page : container ~`133` LOC avec `useSettingsPageController.ts`, `lib/settings/settingsPage.ts` et `components/settings/*` (reliquat : `SettingsSecuritySection` encore dense).
- `app/admin/content/page.tsx` n'est plus une mega-page : container ~`50` LOC avec `useAdminContentPageController`, `lib/admin/content/adminContentPage.ts`, `lib/admin/exercises/adminExerciseCoherence.ts` et `components/admin/content/*` (reliquat contrat/produit : difficulte liste exercices transitoire tant que `difficulty_tier` n'est pas garanti sur la liste admin API ; modales exercices encore en valeurs legacy pour l'edition).
- `ExerciseSolver.tsx` n'est plus le seam principal ; le split `ChallengeSolver` est lui aussi livré.
- Le risque runtime frontal se concentre désormais surtout dans les mega-pages et dans quelques sous-composants encore denses (`ChallengeSolverCommandBar`, `ContentListProgressiveFilterToolbar`, `Header`).
- La duplication AIGenerator n'est plus le sujet principal ; le vrai enjeu devient la discipline de découpage des surfaces et la standardisation des patterns shared.

### 1.2 Addendum roles canoniques et NI-13 — 2026-04-04

Depuis le lot de realignement des roles utilisateur :

- le contrat frontend n'utilise plus `padawan / maitre / gardien / archiviste` comme verite metier
- les roles canoniques actifs sont :
  - `apprenant`
  - `enseignant`
  - `moderateur`
  - `admin`
- les anciens noms restent limites aux couches de compatibilite backend/DB ou a des domaines hors scope (difficultes, badges, rangs, archives)

Impact frontend structurel :

- `User.role` est maintenant type sur l'union canonique
- les helpers de role sont centralises dans `frontend/lib/auth/userRoles.ts`
- `NI-13` n'est plus un guard local de page ; le boundary apprenant/adulte est maintenant porte par `frontend/proxy.ts`, avec `ProtectedRoute` comme defense en profondeur cote client
- `/home-learner` devient la home principale des apprenants
- `/dashboard` reste accessible a l'apprenant comme entree secondaire discrete, sans redevenir la destination par defaut

### 1.3 Sidecar produit a surveiller — coherence interaction defis

Ce sujet ne fait **pas** partie de la sequence FFI active, mais il doit rester visible
dans les documents de pilotage :

- la verite runtime des defis se base sur `response_mode`, pas seulement sur `challenge_type`
- un meme type visible peut encore produire QCM / interaction / texte libre selon la policy backend
- c'est un **sujet produit / UX / contrat**, pas un simple refactor frontend

Reference backlog a suivre :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` - **F44**

Decision d'execution :

- ne pas diluer ce sujet dans `FFI-L11` a `FFI-L17`
- reprendre d'abord les lots d'industrialisation frontend
- ouvrir ensuite un lot dedie si la matrice produit cible est validee

---

## 2. Design Tokens

### 2.1 Source de vérité

- **Fichier principal** : `frontend/app/globals.css` (48.2 KB)
- **Architecture** : CSS variables + `@theme inline` Tailwind v4
- **Config Tailwind** : `tailwind.config.js` minimal — tout est dans globals.css

### 2.2 Palette — Thèmes disponibles

#### Thème Spatial (défaut)

```css
--background: #0a0a0f --foreground: #ffffff --card: #12121a --primary: #7c3aed
  /* violet-600 */ --primary-light: #a78bfa --secondary: #6366f1
  --muted: #1a1a24 --muted-foreground: #c0c0c0 --accent: #ec4899
  --destructive: #ef4444 --border: rgba(124, 58, 237, 0.2) --ring: #7c3aed
  --radius: 1rem --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.07);
```

Dark override : `--background: #000000`, `--card: #0a0a0f`, borders plus opaques (0.4 / 0.2)

#### 6 thèmes additionnels

| Thème       | Bg light | Primary light  | Accent  |
| ----------- | -------- | -------------- | ------- |
| Minimaliste | #ffffff  | #000000        | —       |
| Océan       | #0c1220  | #0369a1        | #0d9488 |
| Dune        | #fef7ed  | #b45309        | #d97706 |
| Forêt       | #f0fdf4  | #047857        | #059669 |
| Pêche       | #fff7ed  | #ea580c        | #f97316 |
| Dino        | #fef9c3  | #65a30d (lime) | #84cc16 |

### 2.3 Tokens sémantiques

```css
--warning: #d97706 (light) / #fbbf24 (dark) --success: #059669 (light) / #34d399
  (dark) --info: #0284c7 (light) / #38bdf8 (dark);
```

### 2.4 Tokens spéciaux

**Canvas spatial** (format RGB pour canvas API) :

```css
--spatial-particle-rgb
--spatial-star-rgb
--spatial-planet-glow-rgb
--spatial-planet-color-{1,2,3}-rgb
--spatial-dino-symbol-rgb
```

**Sidebar** : miroir des tokens principaux (`--sidebar`, `--sidebar-foreground`, etc.)

**Charts** : 5 couleurs par thème (`--chart-1` à `--chart-5`)

**Border radius** :

```css
--radius-sm: calc(var(--radius) - 4px) --radius-md: calc(var(--radius) - 2px)
  --radius-lg: var(--radius) --radius-xl: calc(var(--radius) + 4px);
```

### 2.5 Typographie

| Rôle            | Valeur                                         |
| --------------- | ---------------------------------------------- |
| Font principale | Exo 2 (Google Fonts, chargé dans `layout.tsx`) |
| Font sans       | `--font-geist-sans` (variable Tailwind v4)     |
| Font mono       | `--font-geist-mono` (variable Tailwind v4)     |

### 2.6 Animations

| Nom             | Usage                                       |
| --------------- | ------------------------------------------- |
| `shimmer`       | Badges, skeletons                           |
| `pulse-subtle`  | Feedback discret                            |
| `scale-in`      | Apparitions modales                         |
| `slide-up`      | Transitions de page                         |
| `success-pulse` | Feedback réussite                           |
| `error-shake`   | Feedback erreur                             |
| `pulse-ring`    | Planète (thème spatial)                     |
| `dino-bob`      | Dino flottant (thème Dino)                  |
| `orbit-{0..5}`  | Symboles mathématiques en orbite (6 phases) |

### 2.7 Micro-interactions (globals.css)

- **Boutons** : shine au hover + `translateY(-2px)` + box-shadow étendue
- **Cards** : shine + `translateY(-4px) scale(1.01)` + border colorisée
- **Inputs** : focus ring 3px + border-color primary
- **Liens** : opacity transitions

---

## 3. Inventaire Composants

### 3.1 Composants UI Atomiques (24 fichiers — `components/ui/`)

| Composant           | Variants CVA                                                                  | Base     |
| ------------------- | ----------------------------------------------------------------------------- | -------- |
| `badge.tsx`         | default, secondary, destructive, outline                                      | custom   |
| `button.tsx`        | default, destructive, outline, secondary, ghost, link                         | custom   |
| `card.tsx`          | 7 sous-composants (Card, Header, Title, Description, Content, Footer, Action) | custom   |
| `dialog.tsx`        | 6 sous-composants                                                             | Radix UI |
| `dropdown-menu.tsx` | 5 sous-composants                                                             | Radix UI |
| `input.tsx`         | —                                                                             | HTML     |
| `label.tsx`         | —                                                                             | Radix UI |
| `progress.tsx`      | —                                                                             | Radix UI |
| `select.tsx`        | 4 sous-composants                                                             | Radix UI |
| `separator.tsx`     | horizontal / vertical                                                         | Radix UI |
| `skeleton.tsx`      | shimmer animé                                                                 | custom   |
| `switch.tsx`        | —                                                                             | Radix UI |
| `tabs.tsx`          | 3 sous-composants                                                             | Radix UI |
| `textarea.tsx`      | —                                                                             | HTML     |
| `tooltip.tsx`       | 3 sous-composants                                                             | Radix UI |
| `feedback.tsx`      | type toast                                                                    | custom   |
| `pagination.tsx`    | nav complexe                                                                  | custom   |
| `sonner.tsx`        | Toaster wrapper                                                               | Sonner   |

### 3.2 Surfaces complexes (Top 10 par LOC, pages incluses)

| Surface                                                      | LOC | Responsabilité dominante                        |
| ------------------------------------------------------------ | --- | ----------------------------------------------- |
| `components/exercises/ExerciseSolver.tsx`                    | 632 | Solveur exercices déjà réduit mais encore dense |
| `components/challenges/visualizations/VisualRenderer.tsx`    | 625 | Visualisation générique défis                   |
| `app/admin/ai-monitoring/page.tsx`                           | 587 | Monitoring IA admin                             |
| `components/challenges/visualizations/CodingRenderer.tsx`    | 586 | Renderer code                                   |
| `components/badges/BadgeCard.tsx`                            | 534 | Carte badge riche / compacte / expand           |
| `components/challenges/visualizations/DeductionRenderer.tsx` | 482 | Renderer déduction                              |
| `app/leaderboard/page.tsx`                                   | 452 | Podium + classements + états communautaires     |

_Mise à jour 2026-04-06 : `app/settings/page.tsx` (~`133` LOC, FFI-L13 livré) ne figure plus dans ce top 10._

_Mise à jour 2026-04-06 : `app/admin/content/page.tsx` (~`50` LOC container, FFI-L14 livré) ne figure plus dans ce top 10 ; le domaine vit dans `components/admin/content/*`._

### 3.3 Composants Layout (12 fichiers — `components/layout/`)

| Composant                | Rôle                                        |
| ------------------------ | ------------------------------------------- |
| `Header.tsx` (394 LOC)   | Navigation fixe, dropdown user, menu mobile |
| `Footer.tsx`             | Liens + info légale                         |
| `PageLayout.tsx`         | Wrapper max-width + spacing                 |
| `PageSection.tsx`        | Section avec padding vertical               |
| `PageGrid.tsx`           | Grid helper                                 |
| `PageHeader.tsx`         | Titre + description                         |
| `PageTransition.tsx`     | Fade in/out avec framer-motion              |
| `EmptyState.tsx`         | Message quand aucun contenu                 |
| `LoadingState.tsx`       | Loading UI                                  |
| `AlphaBanner.tsx`        | Banner version alpha                        |
| `UnverifiedBanner.tsx`   | Rappel vérification email                   |
| `MaintenanceOverlay.tsx` | Overlay maintenance                         |

### 3.4 Composants Dashboard (26 widgets)

Tous dans `components/dashboard/` — architecture widget indépendant.
Lazy loading pour les charts lourds : `DailyExercisesChartLazy`, `ProgressChartLazy`, `VolumeByTypeChartLazy`.

### 3.5 Composants Spatiaux (5 fichiers — `components/spatial/`)

| Composant               | Rôle                                            |
| ----------------------- | ----------------------------------------------- |
| `SpatialBackground.tsx` | Conteneur orchestrant les 4 animations          |
| `Starfield.tsx`         | Champ d'étoiles canvas animé                    |
| `Planet.tsx`            | Planète SVG avec rotation + glow (thème-aware)  |
| `Particles.tsx`         | Particules flottantes canvas                    |
| `DinoFloating.tsx`      | Dinosaure flottant (actif seulement thème Dino) |

### 3.6 Doublons et recouvrements identifiés

| Recouvrement          | Fichiers / zone                                                                 | Problème réel actuel                                                       |
| --------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Chatbot flottant      | `ChatbotFloating.tsx` + `ChatbotFloatingGlobal.tsx`                             | Ownership et responsabilité produit encore non documentées                 |
| Content-list platform | `Exercises`, `Challenges`, toolbar, cards, compact list, generators, pagination | Pattern partagé puissant mais encore trop diffus et peu gouverné           |
| Shell navigation      | `Header.tsx`                                                                    | Desktop/mobile/menu utilisateur cohabitent encore dans un composant massif |

---

## 4. Patterns de Layout

### 4.1 Root Layout

```tsx
<html>
  <body className="flex min-h-screen flex-col">
    <Header /> // fixed top-0 z-40 h-16
    <div className="h-16" /> // spacer fixed header
    <AlphaBanner />
    <UnverifiedBanner />
    <main className="flex-1">
      <PageTransition>{children}</PageTransition>
    </main>
    <Footer />
  </body>
</html>
```

### 4.2 PageLayout (standardisé)

```tsx
<PageLayout maxWidth="xl" compact={false}>
  <div className="space-y-6 md:space-y-8">{children}</div>
</PageLayout>
```

Options `maxWidth` : `sm (42rem)` | `md (56rem)` | `lg (72rem)` | `xl (80rem)` | `2xl (1536px)` | `full`

Padding responsive : `1rem` (mobile) → `1.5rem` (640px+) → `2rem` (1024px+)

### 4.3 Pattern Exercice / Défi Solver

1. Loading state (skeleton)
2. Error state (message + retry)
3. Question display (MathText pour LaTeX)
4. Multiple choice / open answer
5. Submit button
6. Feedback (success-pulse / error-shake)
7. Explication (expandable)
8. Hint (optionnel)
9. Next / Session complete CTA

### 4.4 Pattern Dashboard

- `TimeRangeSelector` en haut
- Grid : sidebar (Level + Streak + Stats) + main (Timeline + Charts + Recommendations)
- Lazy loading charts
- Export button

### 4.5 Pattern Liste

1. Filtres (type, difficulty, age group, search)
2. Sort controls
3. View toggle (grid / list)
4. Cards + Pagination

### 4.6 Header Navigation

```
fixed top-0 left-0 right-0 z-index:40
Desktop nav: hidden md:flex
Mobile nav:  md:hidden + AnimatePresence
Skip link:   sr-only → focus:not-sr-only
```

---

## 5. État du Thème Hybride

### 5.1 Références Star Wars / Jedi encore actives (21 occurrences)

| Fichier                                    | Contenu                                                  | Nb  |
| ------------------------------------------ | -------------------------------------------------------- | --- |
| `messages/fr.json`                         | `"padawan": "Apprenti"` (rank gamification)              | 3   |
| `messages/en.json`                         | `"padawan": "Learner"`                                   | 3   |
| `lib/gamification/badgeThematicTitle.ts`   | `star_wars_title` @deprecated                            | 1   |
| `lib/gamification/progressionRankLabel.ts` | `jedi_rank` @deprecated                                  | 1   |
| `types/api.ts`                             | `User.jedi_rank`, `Badge.star_wars_title`                | 7   |
| `hooks/useLeaderboard.ts`                  | `jedi_rank: string` dans l'interface                     | 1   |
| `lib/constants/badge-icons.ts`             | `maitre_jedi`, `voie_du_padawan`, `epreuve_du_chevalier` | 3   |
| `__tests__/`                               | Tests vérifiant le fallback `jedi_rank`                  | 2   |

Toutes en couche données/types — aucune référence visible dans l'UI (sauf la clé `padawan` dans les messages de rang).

### 5.2 Mapping legacy → canonique (déjà en place)

```typescript
// lib/gamification/progressionRankLabel.ts
youngling    → cadet
padawan      → explorer
knight       → navigator
master       → commander
grand_master → cosmic_legend
```

### 5.3 Nouveaux patterns spatiaux (actifs)

| Zone                | Valeurs                                                                                      |
| ------------------- | -------------------------------------------------------------------------------------------- |
| Ranks canoniques    | cadet, scout, explorer, navigator, cartographer, commander, stellar_archivist, cosmic_legend |
| Emojis ranks        | 🌟 🔭 🧭 🛰️ 🗺️ ⭐ 📚 ✨                                                                      |
| Composants spatiaux | Starfield, Planet, Particles — thème-aware via tokens RGB                                    |
| Thème Dino          | DinoFloating conditionnel, lime/fossil colors                                                |

---

## 6. Inconsistances Prioritaires

### 6.1 Couleurs hardcodées (18% — 64 occurrences)

```
lib/constants/leaderboard.ts — podium ranks 1-3 :
  bg-amber-500/10  (or)
  bg-slate-500/10  (argent)
  bg-amber-700/10  (bronze)

Composants — états sémantiques :
  text-blue-500, text-red-500, text-green-500 (35 occ.)
```

**Bug** : Les couleurs podium ne s'adaptent pas au thème sélectionné.

### 6.2 Surfaces runtime/pages encore critiques

| Surface                                                    | LOC | Problème actuel                                      |
| ---------------------------------------------------------- | --- | ---------------------------------------------------- |
| `components/profile/ProfileLearningPreferencesSection.tsx` | 449 | Sous-section profil encore dense, mais page fermee   |
| `ChallengeSolverCommandBar.tsx`                            | 446 | Bloc réponse défi encore dense après split du solver |
| `Header.tsx`                                               | 394 | Desktop + mobile + menu utilisateur encore couples   |

_Note : le container `app/settings/page.tsx` (~`133` LOC) est sorti de cette liste depuis FFI-L13 ; le reliquat dense côté paramètres est surtout `SettingsSecuritySection` (confidentialité + sessions)._

_Note : le shell `app/admin/content/page.tsx` est sorti de cette liste depuis FFI-L14 ; un reliquat **contrat/produit** subsiste sur la difficulté exercices admin (voir `session-plan` FFI-L14 et `DIFFICULTY_AND_RANKS_MANIFEST.md`)._

### 6.3 AIGenerator requalifié

`shared/AIGeneratorBase.tsx` est deja en place et les wrappers domaine sont minces.
Le recouvrement restant le plus rentable concerne surtout `UnifiedExerciseGenerator.tsx`
et, plus largement, la plateforme `content-list` (`toolbar`, `generator`, cartes,
pagination, state liste).

### 6.4 Chatbot floating ambigu

`ChatbotFloating.tsx` vs `ChatbotFloatingGlobal.tsx` — responsabilités non documentées.

### 6.5 Résidus Star Wars dans types TypeScript

`User.jedi_rank` et `Badge.star_wars_title` dans `types/api.ts` propagent le legacy partout dans le frontend.

### 6.6 Token `primary-on-dark` - risque initial levé

Le risque initial a ete corrige : `--primary-text-on-dark` est maintenant defini dans
tous les themes actifs de `globals.css`.

Le sujet n'est donc plus un bug critique de standardisation. La dette residuelle
concerne surtout :

- la surveillance des nouveaux usages pour eviter de reintroduire un contraste hardcode
- le remplacement progressif des couleurs semantiques encore fixes quand elles bloquent
  un vrai comportement multi-theme

---

## 7. Chantiers de Standardisation

> Addendum 2026-03-29 : les chantiers ci-dessous sont conserves comme photographie initiale.
> Une requalification quality-first, basee sur la relecture architecte du code reel, est ajoutee
> des le debut de cette section pour mettre a jour l'ordre d'execution sans faire disparaitre les constats initiaux.

### Requalification architecte 2026-03-29

Cette relecture conserve tous les points de l'audit initial, mais requalifie leur **ordre reel**
et leur **vrai scope technique** a partir du code actuellement en place.

| Point initial                 | Statut 2026-03-29         | Requalification                                                                                                                                                                             |
| ----------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tokens podium theme-aware     | **Maintenu**              | Devient un lot "tokens critiques multi-theme". Le sous-risque `primary-on-dark` a ete corrige ; la dette restante est surtout podium/symbolique et couleurs semantiques encore hardcodees.  |
| 21 residus Star Wars          | **Maintenu, scope borne** | A traiter, mais sans grand sweep destructif. Nettoyer d'abord les couches frontend internes, tout en gardant les alias/types deprecated tant que le contrat backend public les sert encore. |
| AIGenerator / AIGeneratorBase | **Requalifie**            | Les wrappers `exercises/AIGenerator.tsx` et `challenges/AIGenerator.tsx` sont deja minces. Le vrai recouvrement restant concerne surtout `exercises/UnifiedExerciseGenerator.tsx`.          |
| Solver x2 trop lourds         | **Traite**                | `ExerciseSolver` puis `ChallengeSolver` ont ete decoupes. La dette residuelle porte surtout sur quelques sous-composants denses et non plus sur un monolithe runtime unique.                |
| Header.tsx trop lourd         | **Confirme, depriorise**  | Bon chantier de lisibilite, mais moins urgent que auth/bootstrap, storage, pages contenu et solvers.                                                                                        |
| 64 couleurs hardcodees        | **Confirme, depriorise**  | Toujours vrai, mais a lancer apres les tokens critiques et les chantiers infra plus rentables.                                                                                              |
| Chatbot floating ambigu       | **Confirme**              | Ne bloque pas le runtime. A documenter et clarifier dans le lot Design System plutot qu'en hotfix.                                                                                          |

### Chantiers supplementaires identifies

La relecture architecte fait ressortir 4 sujets a meilleur ROI que certains chantiers initiaux :

| Nouveau chantier                    | Pourquoi il passe devant                                                                                                                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consolidation auth / bootstrap API  | La logique est dupliquee entre `components/providers/AuthSyncProvider.tsx`, `hooks/useAuth.ts` et `lib/api/client.ts`. C'est un vrai sujet d'industrialisation, securite et robustesse runtime. |
| Couche storage typee et centralisee | `localStorage` / `sessionStorage` sont disperses entre pages, analytics, providers et sessions F04. Une couche unique reduit parsing fragile, duplication et dette future.                      |
| DRY pages contenu exercices / defis | `app/exercises/page.tsx` et `app/challenges/page.tsx` partagent une grosse partie de l'etat filtre / ordre / pagination / persistence.                                                          |
| Normalisation loading / skeletons   | L'ancien audit frontend reste partiellement vrai : `LoadingState` et `DashboardWidgetSkeleton` existent, mais tous les loaders de surface ne sont pas encore alignes.                           |

### Feuille de route quality-first

#### FFI-L1 - Tokens critiques multi-theme

**Priorite** : P0 | **Effort** : S (2-4h) | **Impact** : bug fix immediat + fiabilite multi-theme

Objectif :

- ajouter `--rank-gold`, `--rank-silver`, `--rank-bronze` dans chaque theme de `globals.css`
- remplacer les classes hardcodees du podium dans `lib/constants/leaderboard.ts`
- maintenir les tokens critiques multi-theme sans reintroduire de contraste fixe

Perimetre :

- `frontend/app/globals.css`
- `frontend/lib/constants/leaderboard.ts`
- usages tokens podium / contrastes semantiques critiques

#### FFI-L2 - Consolidation auth / bootstrap API

**Priorite** : P1 | **Effort** : M | **Impact** : maintenabilite, securite, robustesse runtime

Objectif :

- etablir une seule source de verite pour refresh/sync access token/cookie frontend
- reduire le recouvrement entre `AuthSyncProvider`, `useAuth` et `lib/api/client`
- clarifier les flows cross-domain prod vs dev

Perimetre :

- `frontend/components/providers/AuthSyncProvider.tsx`
- `frontend/hooks/useAuth.ts`
- `frontend/lib/api/client.ts`

#### FFI-L3 - Couche storage typee et centralisee

**Priorite** : P1 | **Effort** : M | **Impact** : DRY, fiabilite, defense parsing/storage

Objectif :

- extraire une couche utilitaire unique pour `localStorage` / `sessionStorage`
- centraliser cles, parsing defensif, fallbacks et noms de stockage
- migrer les usages de preferences ordre, sessions F04, analytics session et bootstrap frontend

Perimetre type :

- `frontend/app/exercises/page.tsx`
- `frontend/app/challenges/page.tsx`
- `frontend/lib/spacedReviewSession.ts`
- `frontend/lib/analytics/edtech.ts`
- `frontend/components/providers/Providers.tsx`

#### FFI-L4 - DRY pages contenu exercices / defis

**Priorite** : P1 | **Effort** : M | **Impact** : reduction de duplication structurelle

Objectif :

- extraire le pattern commun ordre persistant / filtres / pagination / reset / vue grid-list
- garder les differences domaine-specifiques (types, labels, hooks) en configuration

Perimetre :

- `frontend/app/exercises/page.tsx`
- `frontend/app/challenges/page.tsx`
- hooks / helpers strictement necessaires

#### FFI-L5 - Normalisation loading / skeletons

**Priorite** : P1 | **Effort** : S-M | **Impact** : cohesion runtime, reduction duplication

Objectif :

- terminer l'alignement des loaders de surface sur `LoadingState`
- terminer l'alignement des widgets dashboard sur `DashboardWidgetSkeleton`
- laisser les spinners de bouton localises quand ils restent le bon niveau de feedback

Points concernes :

- `components/auth/ProtectedRoute.tsx`
- `components/badges/BadgeGrid.tsx`
- `components/dashboard/Recommendations.tsx`
- `components/dashboard/DailyChallengesWidget.tsx`
- surfaces analogues encore inline

#### FFI-L6 - Nettoyage legacy Star Wars borne et sur

**Priorite** : P1 | **Effort** : M | **Impact** : coherence thematique, dette reduite

Objectif :

- nettoyer les residus encore utiles a l'interieur du frontend
- conserver les champs/types deprecated exposes par le backend tant qu'ils restent necessaires
- documenter clairement les alias legacy au lieu de casser le contrat de maniere implicite

Ordre recommande :

1. messages / constantes / labels internes
2. helpers frontend et interfaces derivees
3. types API deprecated gardes mais isoles / annotees

#### FFI-L7 - Requalification du chantier AIGenerator

**Priorite** : P1 | **Effort** : S-M | **Impact** : DRY cible sur le vrai recouvrement

Objectif :

- conserver les wrappers `AIGenerator.tsx` s'ils restent minces
- auditer le chevauchement entre `shared/AIGeneratorBase.tsx` et `exercises/UnifiedExerciseGenerator.tsx`
- extraire uniquement ce qui duplique vraiment la logique ou la structure

Important :

- ce lot remplace le vieux constat "supprimer les deux AIGenerator"
- le but n'est plus la suppression cosmetique, mais la reduction du vrai recouvrement restant

#### FFI-L8 - Preparation du decoupage solver

**Priorite** : P1 | **Effort** : M | **Impact** : baisse du risque avant refactor lourd

Objectif :

- extraire types, selecteurs, composants purs et logique commune sans changer le comportement
- preparer une seam commune pour `ExerciseSolver` et `ChallengeSolver`

Pieces candidates :

- affichage question
- affichage feedback
- bloc explanation / hint
- resume fin de session
- logique de submit / timing / transitions convertie en helpers purs quand possible

#### FFI-L9 - Split `ExerciseSolver`

**Priorite** : P1 | **Effort** : L | **Impact** : maintenabilite + testabilite

Objectif :

- decouper d'abord `ExerciseSolver.tsx`
- profiter du fait qu'il a deja ete stabilise et teste recemment avec F04

Decoupage cible :

```
ExerciseSolverContainer.tsx
ExerciseQuestionBlock.tsx
ExerciseAnswerBlock.tsx
ExerciseFeedbackBlock.tsx
ExerciseExplanationBlock.tsx
ExerciseSessionSummary.tsx
```

#### FFI-L10 - Split `ChallengeSolver` ✅ Livré

**Priorite** : P1 | **Effort** : L | **Impact** : maintenabilite + testabilite

Résultat :

- lot livre apres stabilisation de `FFI-L8` et `FFI-L9`
- helpers purs extraits + tests de caracterisation
- split `status / header / content / hints / feedback`
- extraction `ChallengeSolverCommandBar` et `useChallengeSolverController`
- `ChallengeSolver.tsx` ramene a un container ~`188` LOC
- retry multi-position revalide apres reset `visualSelections`

Seam residuel :

```text
ChallengeSolver.tsx
ChallengeSolverStatus.tsx
ChallengeSolverHeader.tsx
ChallengeSolverContent.tsx
ChallengeSolverHintsPanel.tsx
ChallengeSolverFeedback.tsx
ChallengeSolverCommandBar.tsx
useChallengeSolverController.ts
challengeSolver.ts
```

Le lot est considere ferme. La dette residuelle la plus visible n'est plus le monolithe
runtime, mais `ChallengeSolverCommandBar.tsx` (~`446` LOC), qui reste un composant dense
sans remettre en cause la fermeture de `FFI-L10`.

#### FFI-L11 - Modulariser `app/profile/page.tsx`

**Priorite** : P1 | **Effort** : L | **Impact** : lisibilite + ownership domaine profil

Statut :

- **livre**
- `app/profile/page.tsx` ramene a un container fin (~`191` LOC)
- extraction `useProfilePageController.ts`
- extraction `lib/profile/profilePage.ts`
- extraction des sections `components/profile/*`
- couverture reelle : page profil + hook controller + helpers purs

Resultat :

- la mega-page critique est fermee
- la validation mot de passe `min 8` a ete re-verrouillee apres refactor
- la couverture `useProfilePageController` est maintenant un vrai test hook (`renderHook`), plus un faux positif fonde sur des helpers purs

Reliquat connu :

- `components/profile/ProfileLearningPreferencesSection.tsx` reste un sous-seam dense (~`449` LOC), mais il n'empeche pas la fermeture de `FFI-L11`

#### FFI-L12 - Modulariser `app/badges/page.tsx`

**Priorite** : P1 | **Effort** : L | **Impact** : lisibilite + testabilite

Statut :

- **livre**
- `app/badges/page.tsx` ramene a un container ~`252` LOC
- extraction `useBadgesPageController.ts`
- extraction `lib/badges/badgesPage.ts`
- extraction des sections `components/badges/*`
- couverture reelle : page badges + hook controller + helpers purs

Resultat :

- la mega-page badges critique est fermee
- filtres, stats, progression, collection et vitrines sont maintenant separables et testables
- les tests de caracterisation page badges ont ete stabilises (plus d'import dynamique repete dans la suite)

Reliquat connu :

- `BadgesProgressTabsSection.tsx` reste une vue dense (~`250` LOC)
- `BadgeCard.tsx` reste hors lot et demeure un candidat naturel pour une phase ulterieure

#### FFI-L13 - Modulariser `app/settings/page.tsx`

**Priorite** : P1 | **Effort** : L | **Impact** : robustesse des parcours compte | **Statut** : **livre** (2026-04-06)

Resultat :

- `app/settings/page.tsx` est ramene a un container fin (~`133` LOC)
- logique runtime dans `useSettingsPageController.ts`, derivations pures dans `lib/settings/settingsPage.ts`
- sections dans `components/settings/*` (general, notifications, securite, donnees + nav)
- tests de caracterisation page + hook + helpers en place

Reliquat connu :

- `SettingsSecuritySection.tsx` reste une vue dense (confidentialite + sessions actives sur la meme section)

#### FFI-L14 - Decouper `app/admin/content/page.tsx`

**Priorite** : P1 | **Effort** : L | **Impact** : frontiere admin plus nette | **Statut** : **livre** cote architecture frontend (2026-04-06)

Resultat :

- `app/admin/content/page.tsx` ramene a un container fin (~`50` LOC)
- `useAdminContentPageController.ts`, `lib/admin/content/adminContentPage.ts`, sections `components/admin/content/*`
- coherence exercices : liste sans vocabulaire Star Wars visible ; `getAdminExerciseDifficultyDisplay` transitoire (`Niveau 1..5` / `Palier n` si `difficulty_tier`)

Reliquat connu (contrat / produit, pas echec du split) :

- alignement **final** difficulte exercices admin sur `difficulty_tier` F42 : depend d'une liste admin API qui expose ce champ de facon garantie
- modales exercices : valeurs legacy `ADMIN_DIFFICULTIES` pour l'edition / persistance

#### FFI-L15 - Standardiser la plateforme content-list

**Priorite** : P1 | **Effort** : M-L | **Impact** : DRY structurel

Objectif :

- industrialiser le pattern commun `Exercises` / `Challenges`
- expliciter les conventions shared pour toolbar, generator, cards, pagination et state de liste
- reduire la logique page-specifique encore dupliquee ou implicite

#### FFI-L16 - Split shell/navigation + ownership chatbot

**Priorite** : P2 | **Effort** : M | **Impact** : lisibilite du shell global

Objectif :

- decouper `Header.tsx`
- clarifier `ChatbotFloating.tsx` vs `ChatbotFloatingGlobal.tsx`
- documenter ce qui appartient au shell, a la home ou au domaine chatbot

#### FFI-L17 - Garde-fous architecture, tests et doc runtime

**Priorite** : P2 | **Effort** : M | **Impact** : non-regression

Objectif :

- verrouiller les conventions apres les gros decoupages
- documenter les patterns actifs
- ajouter les tests de structure les plus utiles avant de re-ouvrir des sweeps visuels

### Gate qualite commune

Chaque lot frontend de cette feuille de route doit passer a minima :

1. `cd frontend && npx tsc --noEmit`
2. `cd frontend && npm run lint`
3. `cd frontend && npx vitest run <tests touches>`
4. `cd frontend && npx prettier --check <fichiers touches>`

Ajouter des tests cibles de non-regression avant tout refactor structurel (`FFI-L4`, `FFI-L7`, `FFI-L8`, `FFI-L9`, `FFI-L10`, `FFI-L12`, `FFI-L13`, `FFI-L14`).

### Recapitulatif mis a jour

| Ordre | Lot                                                           | Priorite | Effort | Impact principal          | Statut au 2026-04-06 |
| ----- | ------------------------------------------------------------- | -------- | ------ | ------------------------- | -------------------- |
| 1     | FFI-L1 Tokens critiques multi-theme                           | P0       | S      | Bug fix + multi-theme     | ✅ Livré             |
| 2     | FFI-L2 Consolidation auth / bootstrap API                     | P1       | M      | Maintenabilite + securite | ✅ Livré             |
| 3     | FFI-L3 Couche storage typee                                   | P1       | M      | DRY + robustesse          | ✅ Livré             |
| 4     | FFI-L4 DRY pages contenu exercices / defis                    | P1       | M      | Reduction duplication     | ✅ Livré             |
| 5     | FFI-L5 Normalisation loading / skeletons                      | P1       | S-M    | Cohesion runtime          | ✅ Livré             |
| 6     | FFI-L6 Nettoyage legacy Star Wars borne                       | P1       | M      | Dette thematique          | ✅ Livré             |
| 7     | FFI-L7 Requalification AIGenerator / UnifiedExerciseGenerator | P1       | S-M    | DRY cible                 | ✅ Livré             |
| 8     | FFI-L8 Preparation split solver                               | P1       | M      | Baisse du risque          | ✅ Livré             |
| 9     | FFI-L9 Split ExerciseSolver                                   | P1       | L      | Maintenabilite            | ✅ Livré             |
| 10    | FFI-L10 Split ChallengeSolver                                 | P1       | L      | Maintenabilite runtime    | ✅ Livré             |
| 11    | FFI-L11 Modulariser Profile                                   | P1       | L      | Ownership domaine         | ✅ Livré             |
| 12    | FFI-L12 Modulariser Badges                                    | P1       | L      | Lisibilite page           | ✅ Livré             |
| 13    | FFI-L13 Modulariser Settings                                  | P1       | L      | Robustesse parcours       | ✅ Livré             |
| 14    | FFI-L14 Decouper Admin Content                                | P1       | L      | Frontiere admin           | ✅ Livré             |
| 15    | FFI-L15 Standardiser plateforme content-list                  | P1       | M-L    | DRY structurel            | À faire              |
| 16    | FFI-L16 Split shell/navigation + chatbot                      | P2       | M      | Lisibilite shell          | À faire              |
| 17    | FFI-L17 Garde-fous architecture / tests / doc runtime         | P2       | M      | Gouvernance               | À faire              |

**Recommandation solo founder mise a jour** :

- `FFI-L1` a `FFI-L14` sont deja livres : la dette la plus rentable restante est desormais `FFI-L15`
- la priorite n'est plus le polish visuel mais les mega-pages et seams runtime
- traiter `FFI-L15` a `FFI-L17` avant de rouvrir de gros sweeps cosmetiques
- garder `D:\\Mathakine\\.claude\\session-plan.md` comme source de verite d'execution active ; cet audit reste la reference projet detaillee

### Plan initial (historique)

> Ce bloc conserve le **plan initial** issu de l'extraction `/octo:extract`.
> Il reste utile comme trace d'origine et comme justification des constats.
> **La source de verite d'execution active est `D:\\Mathakine\\.claude\\session-plan.md`.**
> En cas de divergence, suivre d'abord le `session-plan`, puis la feuille de route `FFI-L1` a `FFI-L17` ci-dessus.

### Chantier 1 — Tokens podium thème-aware

**Priorité** : P0 | **Effort** : S (2–4h) | **Impact** : Bug fix visuel + cohérence multi-thèmes

Ajouter dans chaque thème (globals.css) :

```css
--rank-gold:   /* couleur or adaptée */ --rank-silver: /* couleur argent */
  --rank-bronze: /* couleur bronze */;
```

Remplacer les classes hardcodées dans `lib/constants/leaderboard.ts`.

---

### Chantier 2 — Éliminer les 21 résidus Star Wars

**Priorité** : P1 | **Effort** : M (1 jour) | **Impact** : Cohérence thématique, dette réduite

1. `types/api.ts` : déprécier `jedi_rank` → `progression_rank`, `star_wars_title` → `thematic_title`
2. `hooks/useLeaderboard.ts` : utiliser `progression_rank`
3. `messages/*.json` : clé `padawan` → `explorer`
4. `lib/constants/badge-icons.ts` : renommer les 3 icônes Jedi

---

### Chantier 3 — Compléter la migration AIGeneratorBase

**Priorité** : P1 | **Effort** : S (3–5h) | **Impact** : DRY, un seul composant à maintenir

1. Auditer les différences entre les deux `AIGenerator.tsx`
2. Extraire les différences en props de `AIGeneratorBase`
3. Supprimer les deux doublons

---

### Chantier 4 — Découper ChallengeSolver + ExerciseSolver

**Priorité** : P1 | **Effort** : L (2–3 jours) | **Impact** : Maintenabilité, testabilité

Découpage suggéré (identique pour les deux) :

```
SolverContainer.tsx      — orchestration des états
SolverQuestion.tsx       — affichage question + MathText
SolverChoices.tsx        — choix multiples / input libre
SolverFeedback.tsx       — animations + message
SolverExplanation.tsx    — explication expandable
SolverSessionSummary.tsx — résumé fin de session
```

---

### Chantier 5 — Documenter le Design System

**Priorité** : P2 | **Effort** : M (1 jour) | **Impact** : Onboarding, cohérence future

Créer `frontend/docs/design-system.md` :

- Tableau tokens CSS par catégorie
- Galerie CVA variants (button, badge, card)
- Règles d'usage tokens
- Convention nommage composants
- Clarification `ChatbotFloating` vs `ChatbotFloatingGlobal`

---

### Chantier 6 — Remplacer les couleurs sémantiques hardcodées

**Priorité** : P2 | **Effort** : M (4–6h) | **Impact** : Cohérence multi-thèmes

```
text-blue-500  → text-[--info]
text-red-500   → text-destructive
text-green-500 → text-[--success]
```

---

### Chantier 7 — Découper Header.tsx

**Priorité** : P2 | **Effort** : M (4–6h) | **Impact** : Lisibilité, tests

```
HeaderDesktop.tsx  — navigation desktop
HeaderMobile.tsx   — menu mobile + hamburger
HeaderUserMenu.tsx — dropdown user
HeaderActions.tsx  — Theme + Locale selectors
```

---

### Récapitulatif du plan initial

| #   | Chantier                        | Priorité | Effort | Impact         |
| --- | ------------------------------- | -------- | ------ | -------------- |
| 1   | Tokens podium thème-aware       | P0       | S      | Bug fix        |
| 2   | Éliminer résidus Star Wars (21) | P1       | M      | Cohérence      |
| 3   | Migrer AIGeneratorBase          | P1       | S      | DRY            |
| 4   | Découper Solver ×2              | P1       | L      | Maintenabilité |
| 5   | Documenter Design System        | P2       | M      | Onboarding     |
| 6   | Remplacer couleurs hardcodées   | P2       | M      | Cohérence      |
| 7   | Découper Header.tsx             | P2       | M      | Lisibilité     |

**Recommandation solo founder** : Chantiers 1 + 2 + 3 en premier (P0+P1 courts, gains immédiats).
Chantier 4 (Solver) = sprint dédié à planifier séparément.
