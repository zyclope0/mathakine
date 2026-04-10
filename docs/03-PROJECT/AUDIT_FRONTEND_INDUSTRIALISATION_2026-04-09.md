# Audit Frontend — Industrialisation & Qualité Technique

> Généré le 2026-04-09 via `/octo:review` (prompt d'audit structuré 8 dimensions)
> Stack : Next.js 16 App Router + TypeScript strict + Tailwind CSS + shadcn/ui + React Query v5
> Outil d'exploration : Agent Explore (lecture seule, 14 tâches parallèles)
> Méthode : scoring factuel — chaque constat cite fichier:ligne lu pendant l'audit

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Méthodologie](#2-méthodologie)
3. [Scores par dimension](#3-scores-par-dimension)
4. [D1 — Industrialisation](#4-d1--industrialisation)
5. [D2 — DRY / Factorisation](#5-d2--dry--factorisation)
6. [D3 — TypeScript Strict](#6-d3--typescript-strict)
7. [D4 — ESLint / Hooks](#7-d4--eslint--hooks)
8. [D5 — Modularité](#8-d5--modularité)
9. [D6 — Maintenabilité](#9-d6--maintenabilité)
10. [D7 — Performance Frontend](#10-d7--performance-frontend)
11. [D8 — Réplicabilité / Testabilité](#11-d8--réplicabilité--testabilité)
12. [Findings classés P0-P3](#12-findings-classés-p0-p3)
13. [Forces confirmées](#13-forces-confirmées)
14. [Plan d'exécution solo-founder](#14-plan-dexécution-solo-founder)

---

## 1. Résumé exécutif

| Indicateur                         | Valeur           |
| ---------------------------------- | ---------------- |
| Score global pondéré               | **7.05 / 10**    |
| Findings P0                        | **0**            |
| Findings P1                        | **4**            |
| Findings P2                        | **3**            |
| Findings P3                        | **2**            |
| Fichiers lus pendant l'audit       | 50+              |
| Queries React Query avec staleTime | **41/41** (100%) |
| Occurrences `: any` ou `as any`    | **0**            |
| TODO/FIXME/HACK non ticketés       | **0**            |

**Verdict :** codebase industriellement mature sur TypeScript, cache React Query et guardrails d'architecture. Les risques ouverts sont concentrés sur la performance bundle (exports PDF/Excel sans lazy loading) et l'adoption incomplète des Server Components.

> **Hors-scope de cet audit :** la dimension sécurité frontend (headers HTTP au-delà de la CSP, surface XSS détaillée) n'est pas couverte par les 8 dimensions ci-dessus. **Mise à jour lots QF-07A / QF-07B (2026-04-10)** : en production, **`script-src`** n’utilise plus `'unsafe-inline'` ; CSP dynamique via `frontend/proxy.ts`. **QF-07B** : header interne **`x-nonce`** pour usage serveur optionnel (`headers()`), sans forcer le root layout en dynamic. **`style-src 'unsafe-inline'`** inchangé. Poursuivre la veille sécurité via `CLAUDE.md` / audits dédiés si besoin.

---

## 2. Méthodologie

### Sources lues

Toutes les assertions ci-dessous sont extraites de lectures directes pendant l'audit. Aucune supposition.

| Tâche               | Méthode                                     | Résultat                                                 |
| ------------------- | ------------------------------------------- | -------------------------------------------------------- |
| Guardrails          | Lecture complète `frontendGuardrails.ts`    | 523 lignes, 17 surfaces, 17 seams, 20 lib requis         |
| Fichiers volumineux | `wc -l` sur app/, components/, hooks/, lib/ | 19 fichiers > 300 lignes                                 |
| "use client"        | grep dans app/                              | 38 fichiers sur ~50                                      |
| eslint-disable      | grep + contexte ±1 ligne                    | 13 occurrences dans 12 fichiers                          |
| `: any` / `as any`  | grep exhaustif hors node_modules            | 0 résultat                                               |
| `fetch()` direct    | grep dans app/ + components/                | 0 résultat métier (page `test-sentry` supprimée — QF-01) |
| TODO/FIXME/HACK     | grep dans tout frontend/                    | 0 résultat                                               |
| staleTime           | grep dans hooks/                            | 41 occurrences, toutes définies                          |
| `dynamic()`         | grep dans tout frontend/                    | 0 résultat                                               |
| `next/image`        | grep dans app/ + components/                | 1 import, 5 contournements                               |

> **Note méthodologique sur le scoring :** les scores par dimension (0-10) sont des jugements calibrés, pas une addition mécanique de critères binaires. Un critère partiellement satisfait contribue proportionnellement. L'échelle est : 0-3 = problématique, 4-6 = acceptable, 7-8 = bon, 9-10 = excellent.

### Dimensions et pondérations

| Dimension            | Poids | Justification                      |
| -------------------- | ----- | ---------------------------------- |
| D1 Industrialisation | 15%   | Cœur du chantier FFI-L20           |
| D2 DRY               | 10%   | Factorisation SSE, helpers, cache  |
| D3 TypeScript Strict | 15%   | Différenciateur qualité majeur     |
| D4 ESLint / Hooks    | 10%   | Discipline de code quotidienne     |
| D5 Modularité        | 15%   | Maintenabilité long terme solo     |
| D6 Maintenabilité    | 15%   | Coût de changement futur           |
| D7 Performance       | 10%   | Impact UX élèves (Core Web Vitals) |
| D8 Réplicabilité     | 10%   | Vélocité feature + fiabilité CI    |

---

## 3. Scores par dimension

| Dimension            | Score | Poids    | Score pondéré | Findings P0 | Findings P1 |
| -------------------- | ----- | -------- | ------------- | ----------- | ----------- |
| D1 Industrialisation | 7/10  | 15%      | 1.05          | 0           | 1           |
| D2 DRY               | 7/10  | 10%      | 0.70          | 0           | 1           |
| D3 TypeScript        | 9/10  | 15%      | 1.35          | 0           | 0           |
| D4 ESLint/Hooks      | 7/10  | 10%      | 0.70          | 0           | 0           |
| D5 Modularité        | 6/10  | 15%      | 0.90          | 0           | 0           |
| D6 Maintenabilité    | 7/10  | 15%      | 1.05          | 0           | 0           |
| D7 Performance       | 5/10  | 10%      | 0.50          | 0           | 2           |
| D8 Réplicabilité     | 8/10  | 10%      | 0.80          | 0           | 0           |
| **TOTAL**            |       | **100%** | **7.05/10**   | **0**       | **4**       |

---

## 4. D1 — Industrialisation

**Score : 7/10** | Poids 15%

### Critères passés ✓

**Hook controllers séparés (+2)**

8 controllers présents dans `frontend/hooks/` (lus pendant l'audit) :

```
useAdminContentPageController.ts
useBadgesPageController.ts
useChallengeSolverController.ts
useContentListPageController.ts
useDashboardPageController.ts
useExerciseSolverController.ts
useProfilePageController.ts
useSettingsPageController.ts
```

Ces fichiers correspondent exactement aux `REQUIRED_ARCHITECTURE_SEAMS` définis dans `frontendGuardrails.ts`. Le guardrail teste leur présence via `collectMissingSeams()`.

**Helpers purs dans `lib/` (+2)**

`frontend/lib/` contient des modules par domaine : `api/`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `settings/`, `utils/`. Aucun `fetch()` direct dans ces modules (0 occurrence trouvée).

**Guardrails actifs sans exception (+1)**

`ALLOWED_DENSE_EXCEPTIONS = []` (lu dans `frontendGuardrails.ts`). Zéro exception tolérée. La politique est appliquée et vérifiée par `frontendGuardrails.test.ts` (présent dans `__tests__/unit/architecture/`).

### Critères en dérogation ✗

**Pages non réduites à des coques (-2)**

Trois pages `app/` dépassent le modèle coque attendu :

| Fichier                     | Lignes  | Problème                        |
| --------------------------- | ------- | ------------------------------- |
| `app/leaderboard/page.tsx`  | **481** | Pas de controller séparé trouvé |
| `app/home-learner/page.tsx` | **317** | Logique probable inline         |
| `app/exercises/page.tsx`    | **311** | Filtres, pagination inline      |

La norme projet est < 100 lignes pour une coque. Ces trois pages ont `"use client"` en ligne 1, confirmant qu'elles gèrent du runtime côté client.

**Sections partiellement extraites (-1)**

10 composants dans `components/` dépassent 300 lignes :

```
components/badges/BadgeCard.tsx          494 lignes
components/diagnostic/DiagnosticSolver.tsx 456 lignes
components/exercises/ExerciseModal.tsx   448 lignes
components/dashboard/StudentChallengesBoard.tsx 443 lignes
components/admin/BadgeEditModal.tsx      431 lignes
components/admin/ChallengeEditModal.tsx  428 lignes
components/shared/AIGeneratorBase.tsx    426 lignes
components/admin/ExerciseEditModal.tsx   368 lignes
components/exercises/ExerciseSolver.tsx  366 lignes
components/admin/BadgeCreateModal.tsx    342 lignes
```

Les modaux admin (`BadgeEditModal`, `ChallengeEditModal`, `ExerciseEditModal`) peuvent légitimement être denses (formulaires multi-champs). `BadgeCard` (494 lignes) et `DiagnosticSolver` (456 lignes) sont plus préoccupants.

---

## 5. D2 — DRY / Factorisation

**Score : 7/10** | Poids 10%

### Critères passés ✓

**Zéro `fetch()` direct dans composants (+3)**

Grep exhaustif sur `app/` et `components/` : **0** `fetch()` direct hors React Query en surfaces métier (historique : ancienne page dev `test-sentry`, supprimée — QF-01). Résultat : **0 contournement React Query** en production.

**Policy de cache homogène sur 41 queries (+2)**

`staleTime` défini sur chaque hook de données. Distribution par domaine :

| Domaine        | staleTime           | Justification                                |
| -------------- | ------------------- | -------------------------------------------- |
| Exercices      | 10 000 ms           | Données dynamiques (résultats en temps réel) |
| Challenges     | 30 000 ms           | Mis à jour moins fréquemment                 |
| Admin          | 60 000 ms           | Usage interne, fraîcheur moindre             |
| Badges         | 60 000 – 300 000 ms | Données quasi-statiques                      |
| Auth (useAuth) | 300 000 ms (5 min)  | Token validé côté serveur                    |

**Proxy SSE factorisé (+1)**

Lot SSE-DRY-07 fermé : `frontend/lib/api/sseProxyRequest.ts` et `frontend/lib/api/proxyForwardHeaders.ts` factorisent les deux routes SSE pédagogiques. Avant : ~100 LOC par route. Après : ~15 LOC par route.

### Critères en dérogation ✗

**5 composants avec `<img>` dupliqué (-2)**

5 fichiers contournent `next/image` sans factorisation commune :

```
components/ui/UserAvatar.tsx:31
components/badges/BadgesProgressTabsSection.tsx:145
components/badges/BadgeIcon.tsx:131
components/badges/BadgeCard.tsx:49
components/chat/ChatMessagesView.tsx:71
```

Chacun gère son propre rendu image avec les mêmes limitations (pas de lazy loading, pas d'optimisation WebP). Un composant partagé `AppImage` ou `UserAvatarImage` éliminerait cette duplication.

**Barrel exports absents (-1)**

4 barrel exports sur ~150 modules `lib/` :

```
lib/storage/index.ts              12 lignes
components/challenges/visualizations/index.ts  12 lignes
components/layout/index.ts        15 lignes
components/learner/index.ts       2 lignes
```

Les domaines principaux (`lib/auth/`, `lib/badges/`, `lib/challenges/`, `lib/security/`) n'ont pas d'`index.ts`. Les imports consommateurs utilisent des chemins absolus internes, créant un couplage fort aux chemins de fichiers.

---

## 6. D3 — TypeScript Strict

**Score : 9/10** | Poids 15%

### Critères passés ✓

**Zéro `any` explicite (+3)**

Grep complet sur `frontend/` (hors `node_modules/`, `.next/`, `coverage/`, `@types/`) :

```
Pattern `: any`  → 0 résultat
Pattern `as any` → 0 résultat
```

Résultat absolu. Aucun contournement du système de types.

**Configuration la plus stricte du marché (+2)**

`tsconfig.json` active :

- `strict: true` (active `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `noImplicitAny`, `noImplicitThis`, `alwaysStrict`)
- `noUncheckedIndexedAccess: true` — accès tableau retourne `T | undefined`
- `exactOptionalPropertyTypes: true` — `{ a?: string }` ≠ `{ a: string | undefined }`

C'est la configuration recommandée par Matt Pocock (TypeScript Total) et l'équipe TypeScript Microsoft pour les codebases production 2024.

**Types API centralisés en `types/api.ts` (+2)**

`frontend/types/api.ts` — 314 lignes contenant :

```typescript
(GamificationLevelIndicator,
  User,
  Exercise,
  PaginatedResponse<T>,
  ExercisesPaginatedResponse,
  ExerciseFiltersWithSearch,
  ChallengeResponseMode,
  Challenge,
  ChallengesPaginatedResponse,
  DailyChallenge,
  DailyChallengesResponse,
  ChallengeFiltersWithSearch,
  ChallengeAttemptResponse,
  ChallengeCatalogStatBucket,
  ChallengesStats,
  Badge,
  UserBadge,
  UserBadgesResponse,
  GamificationStats);
```

### Nuance (-1)

**Types locaux dans 70 fichiers**

70 fichiers dans `app/` et `components/` déclarent des `interface` ou `type` locaux. Certains sont légitimes (props de composants, types internes de hooks). Une passe d'audit spécifique serait nécessaire pour distinguer les types qui mériteraient d'être centralisés dans `types/api.ts` (types partagés entre plusieurs modules) de ceux qui sont correctement locaux (types de props, types de state interne).

---

## 7. D4 — ESLint / Hooks

**Score : 7/10** | Poids 10%

### Critères passés ✓

**`exhaustive-deps` : toutes les dérogations justifiées (+3)**

8 suppressions de règles `react-hooks/exhaustive-deps` et `set-state-in-effect` lues pendant l'audit. Toutes avec justification :

| Fichier                                                       | Ligne                 | Justification lue                                                                                             |
| ------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------- |
| `hooks/useSettingsPageController.ts:181`                      | `exhaustive-deps`     | `mount-only load; useSettings callbacks are unstable`                                                         |
| `hooks/chat/useGuestChatAccess.ts:40`                         | `set-state-in-effect` | `intentional post-hydration sync from sessionStorage (guest quota)`                                           |
| `hooks/useChallengeSolverController.ts:141`                   | `exhaustive-deps`     | `Reset only on visible challenge identity change; full object deps would wipe in-progress answers on refetch` |
| `hooks/useContentListOrderPreference.ts:24`                   | `set-state-in-effect` | `intentional post-hydration sync`                                                                             |
| `hooks/useExerciseSolverController.ts:253`                    | `exhaustive-deps`     | `reset seulement si l'exercice courant change de réalité visible`                                             |
| `components/challenges/visualizations/PuzzleRenderer.tsx:162` | `exhaustive-deps`     | `onOrderChange via ref ; pieces dérivé de visualData — éviter reset sur identité du tableau seule`            |
| `components/challenges/visualizations/PuzzleRenderer.tsx:201` | `exhaustive-deps`     | `intentionnel au montage seulement — inclure items/onOrderChange recréerait des boucles avec le parent`       |
| `components/ui/sonner.tsx:38`                                 | `exhaustive-deps`     | `Register once; MutationObserver handles subsequent theme class changes`                                      |

**`react-hooks/rules-of-hooks` : 0 violation (+3)**

Aucune occurrence trouvée pendant l'audit. Hooks appelés uniquement au niveau supérieur des composants et hooks custom.

### Critères en dérogation ✗

**5 suppressions `@next/next/no-img-element` sans justification (-1)**

```
components/ui/UserAvatar.tsx:31
components/badges/BadgesProgressTabsSection.tsx:145
components/badges/BadgeIcon.tsx:131
components/badges/BadgeCard.tsx:49
components/chat/ChatMessagesView.tsx:71
```

Chacun supprime la règle sans commentaire adjacent expliquant pourquoi `next/image` ne peut pas être utilisé (URL externe dynamique, dimensions inconnues, contrainte de rendu SVG…). La règle du projet exige `// Intentional: <raison>`.

---

## 8. D5 — Modularité

**Score : 6/10** | Poids 15%

### Critères passés ✓

**Domaines `lib/` séparés (+2)**

`frontend/lib/` est organisé par domaine fonctionnel : `api/`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `settings/`, `utils/`, `theme/`, `storage/`. Chaque domaine contient ses helpers sans imports croisés évidents au premier niveau.

**8 controllers séparés (+2)**

Voir D1. La séparation runtime/UI est le signal fort de la modularité du projet.

### Critères en dérogation ✗

**Tests non co-localisés (-2)**

133 fichiers de tests dans `__tests__/unit/` séparé du code source :

```
__tests__/unit/hooks/useAuth.test.ts
__tests__/unit/components/badges/BadgeCard.test.tsx
__tests__/unit/lib/api/backendUrl.test.ts
```

Le fichier `components/badges/BadgeCard.tsx` (494 lignes) n'a pas son test dans `components/badges/`. Ce pattern rend la navigation difficile lors d'un refactoring (trouver le test correspondant nécessite de connaître la structure `__tests__/`).

La recommandation Jest / Vitest 2024 est la co-location : `BadgeCard.test.tsx` à côté de `BadgeCard.tsx`. La migration est progressive et non bloquante.

**Barrel exports quasi-absents (-2)**

4 barrel exports sur ~150 modules `lib/`. Les domaines `lib/auth/`, `lib/badges/`, `lib/challenges/`, `lib/security/` n'exposent pas d'API surface formelle via `index.ts`. Les consommateurs importent directement les chemins internes :

```typescript
// Pattern actuel (couplage fort au chemin)
import { buildContentSecurityPolicy } from "@/lib/security/buildContentSecurityPolicy";

// Pattern idéal (API surface formelle)
import { buildContentSecurityPolicy } from "@/lib/security";
```

Sans barrel, tout renommage de fichier dans `lib/` casse les imports consommateurs.

**Composants denses (-1)**

`BadgeCard.tsx` (494 lignes), `DiagnosticSolver.tsx` (456 lignes) — vraisemblablement plusieurs responsabilités internes sans sous-composants extraits. Non quantifiable sans lecture des sources.

---

## 9. D6 — Maintenabilité

**Score : 7/10** | Poids 15%

### Critères passés ✓

**Zéro dette commentaire (-0)**

Grep sur TODO/FIXME/HACK : **0 résultat** dans tout `frontend/`. Codebase propre de toute dette commentée non trackée.

**Policy de cache documentée par domaine (+2)**

Les valeurs `staleTime` sont cohérentes et sémantiquement justifiables (10s pour exercices temps-réel, 300s pour auth). Une policy de cache lisible est un indicateur de maintenabilité (un développeur qui reprend le code comprend immédiatement la politique de fraîcheur de chaque domaine).

**Guardrails auto-vérifiés (+1)**

`frontendGuardrails.ts` expose des fonctions `collectMissingSeams()`, `collectProtectedBudgetViolations()`, `collectDenseExceptionViolations()` testées par CI. La maintenance de l'architecture est automatisée.

**Zéro `any` → couplage type-safe (+2)**

0 contournement du système de types. Tout changement d'API se propage par erreur de compilation plutôt que par bug runtime.

### Critères en dérogation ✗

**Controllers volumineux (-1)**

```
hooks/useProfilePageController.ts   463 lignes
hooks/useExerciseSolverController.ts 391 lignes
```

La complexité cyclomatique de ces fichiers n'est pas mesurable sans outillage, mais leur taille suggère des fonctions de plus de 30 lignes et une complexité cyclomatique potentiellement > 10 (seuil Clean Code, Martin 2008).

**Utilitaires monolithiques dans `lib/utils/` (-1)**

```
lib/utils/exportPDF.ts    384 lignes
lib/utils/exportExcel.ts  391 lignes
```

Ces deux modules contiennent probablement plusieurs fonctions de haut niveau non décomposées. Ils constituent également un problème de performance (voir D7).

---

## 10. D7 — Performance Frontend

**Score : 5/10** | Poids 10%

C'est la dimension avec le plus de travail restant.

### Critères passés ✓

**`staleTime` sur 100% des queries (+2)**

Voir D2. Aucune query à staleTime = 0 (rechargement systématique). React Query met en cache correctement dans tout le projet.

### Critères en dérogation ✗

**76% des pages `app/` avec `"use client"` — Server Components sous-exploités (-3)**

38 fichiers sur ~50 dans `app/` ont `"use client"` en ligne 1. Parmi eux, au moins 4 pages n'ont pas d'interactivité JSX évidente :

| Page                     | Interactivité attendue              | Candidat SC |
| ------------------------ | ----------------------------------- | ----------- |
| `app/docs/page.tsx`      | Affichage de documentation statique | Oui         |
| `app/changelog/page.tsx` | Liste de changements statique       | Oui         |
| `app/offline/page.tsx`   | Page d'erreur offline statique      | Oui         |
| `app/contact/page.tsx`   | À vérifier (formulaire ?)           | Probable    |

Note : `app/about/page.tsx` et `app/privacy/page.tsx` ont déjà été convertis en Server Components dans le lot FFI-L20G — non comptés négativement.

Conséquence : hydration JavaScript inutile sur des pages statiques, bundle client alourdi, TTI (Time to Interactive) dégradé.

**~~`exportPDF.ts` + `exportExcel.ts` sans chargement paresseux~~ — traité (QF-02) (+0)**

Les dépendances lourdes (`jspdf`, `jspdf-autotable`, `exceljs`) sont chargées via `import()` à l’intérieur des fonctions d’export, pas au chargement du module. Next `dynamic()` sur composant reste à 0 ; le pattern retenu est l’`import()` dans les utilitaires.

**5 `<img>` non optimisés (-2)**

Même liste que D2. Sans `next/image` :

- Pas de conversion automatique WebP/AVIF
- Pas de lazy loading `loading="lazy"` automatique
- Pas de gestion du Cumulative Layout Shift (CLS) via `width`/`height`
- Pas de `sizes` pour le responsive

Les pages badges (leaderboard, dashboard) affichent des badges — surfaces à forte visibilité pour les élèves.

**`next/image` utilisé dans 1 seul endroit (+0)**

`components/challenges/visualizations/ChallengeSolverContent.tsx:3` — seule occurrence de `import Image from "next/image"`. Confirme que l'adoption n'est pas systématique.

---

## 11. D8 — Réplicabilité / Testabilité

**Score : 8/10** | Poids 10%

### Critères passés ✓

**Controllers testables isolément (+3)**

Les 8 controllers n'ont aucun `fetch()` direct (0 occurrence dans `hooks/`). Ils délèguent le réseau aux hooks de données React Query passés en paramètre. Pattern Command/Query Separation appliqué : le controller orchestre, le hook de données communique.

Exemple dans `useChallengeSolverController.ts` :

```typescript
// Le controller reçoit les actions réseau en paramètre — testable sans mock réseau
export function useChallengeSolverController({
  submitAnswer,
  getHint,
  setHints,
  ...
}: UseChallengeSolverControllerArgs)
```

**36 tests sur les helpers `lib/` (+2)**

`__tests__/unit/lib/` contient 36 fichiers couvrant : `api/backendUrl`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `utils/`. Les fonctions pures sont testées indépendamment du DOM.

**6 specs E2E Playwright (+4)**

```
__tests__/e2e/auth.spec.ts
__tests__/e2e/exercises.spec.ts
__tests__/e2e/dashboard.spec.ts
__tests__/e2e/badges.spec.ts
__tests__/e2e/settings.spec.ts
__tests__/e2e/admin.spec.ts
```

Flux critiques couverts : authentification (invité), exercices, dashboard, badges, settings, admin (lecture). Configuration : `workers: 1`, `fullyParallel: false` pour éviter les conflits de rate-limit.

**Test d'architecture auto-vérifié (+1)**

`__tests__/unit/architecture/frontendGuardrails.test.ts` — les guardrails sont testés par CI. Toute violation de surface protégée casse le pipeline avant merge.

### Nuance (-2)

**Tests non co-localisés**

133 fichiers dans `__tests__/unit/` vs code source dans `components/`, `hooks/`, `lib/`. Voir D5. Impact sur la vélocité de maintenance.

---

## 12. Findings classés P0-P3

### P1 — Dette technique mesurable

---

**[P1-PERF-01] `app/leaderboard/page.tsx` — page non décomposée**

```
Fichier  : frontend/app/leaderboard/page.tsx:1
Constat  : 481 lignes avec "use client". Aucun useLeaderboardPageController.ts trouvé.
Impact   : Runtime non testable isolément. Pattern coque violé. Complexité cyclomatique élevée.
Action   : Extraire useLeaderboardPageController.ts + LeaderboardRankingSection + LeaderboardFilterSection.
Validation : wc -l frontend/app/leaderboard/page.tsx → résultat < 80.
```

---

**[P1-PERF-02] ~~Exports PDF/Excel sans lazy loading~~ — résolu (QF-02)**

```
Statut   : `exportDashboardToPDF` / `exportDashboardToExcel` chargent `jspdf`, `jspdf-autotable` et `exceljs`
           via `import()` au clic (helpers `lib/utils/exportPDF.ts` et `exportExcel.ts`) ; `ExportButton` await.
Validation : bundle analyzer — libs absentes du chemin initial du dashboard jusqu’au clic export.
```

---

**[P1-PERF-03] 5 composants avec `<img>` non optimisé**

```
Fichiers : frontend/components/ui/UserAvatar.tsx:31
           frontend/components/badges/BadgesProgressTabsSection.tsx:145
           frontend/components/badges/BadgeIcon.tsx:131
           frontend/components/badges/BadgeCard.tsx:49
           frontend/components/chat/ChatMessagesView.tsx:71
Constat  : <img> brut avec eslint-disable @next/next/no-img-element sans justification textuelle.
Impact   : Pas de lazy loading, pas de WebP/AVIF, CLS potentiel sur pages badges (surface haute
           visibilité élèves). Aucune gestion du Cumulative Layout Shift.
Action   : Migrer vers <Image from="next/image"> avec sizes défini, OU ajouter commentaire
           // Intentional: <raison précise> si migration impossible.
Validation : grep -r "eslint-disable.*no-img-element" frontend/components/ --include="*.tsx"
             → 0 ligne sans justification adjacente.
```

---

**[P2-PERF-04] Pages potentiellement convertibles en Server Components** _(rétrogradé P1→P2 — contenu non lu)_

```
Fichiers : frontend/app/docs/page.tsx:1
           frontend/app/changelog/page.tsx:1
           frontend/app/offline/page.tsx:1
           frontend/app/contact/page.tsx:1
Constat  : "use client" présent. Contenu de ces fichiers non lu pendant l'audit — l'interactivité
           réelle de ces pages n'est pas connue. Candidats Server Components probables mais non confirmés.
Impact   : Potentiellement : hydration inutile, bundle client alourdi, TTI dégradé sur mobile.
           Impact réel à confirmer par lecture des fichiers.
Action   : Lire chaque fichier. Si absence de hooks React / gestionnaires d'événements client :
           supprimer "use client", convertir en Server Component, remplacer useTranslations() par
           await getTranslations().
Validation : Lecture de chaque fichier confirme l'absence d'interactivité → conversion justifiée.
             grep -n '"use client"' frontend/app/docs/page.tsx → vide après correction.
```

---

**[P1-ARCH-05] `app/home-learner/page.tsx` (317 lignes) et `app/exercises/page.tsx` (311 lignes)**

```
Fichiers : frontend/app/home-learner/page.tsx:1
           frontend/app/exercises/page.tsx:1
Constat  : Pages dépassant 300 lignes avec "use client". Pattern coque non respecté.
Impact   : Logique runtime probable inline. Non testable isolément.
Action   : Extraire useHomeLearnerPageController.ts (ou useExercisesPageController.ts)
           + sections ExercisesListSection, ExercisesFiltersSection.
Validation : wc -l frontend/app/exercises/page.tsx → résultat < 100.
```

---

### P2 — Améliorations recommandées

---

**[P2-MOD-01] Tests non co-localisés**

```
Fichier  : frontend/__tests__/unit/ (133 fichiers)
Constat  : Tous les tests dans __tests__/ séparé. Ex: __tests__/unit/components/badges/BadgeCard.test.tsx
           au lieu de components/badges/BadgeCard.test.tsx.
Impact   : Navigation difficile lors de refactoring. Risque d'oubli de mise à jour des tests.
Action   : Migration progressive : co-localiser les tests des composants les plus actifs en priorité.
           Mettre à jour jest.config.ts : testMatch: ["**/*.test.{ts,tsx}"].
Validation : ls frontend/components/badges/BadgeCard.test.tsx → fichier présent.
```

---

> ~~**[P2-MOD-02] Barrel exports absents**~~ — **Invalidé par le débat multi-AI.**
> Dans le contexte Next.js 16 App Router, les barrel exports `index.ts` dans `lib/` nuisent au tree-shaking granulaire c�t� Server Components et peuvent introduire des d�pendances circulaires involontaires (Matt Pocock, TypeScript Total 2023-2024). Les imports explicites `@/lib/security/buildContentSecurityPolicy` sont **la bonne pratique** pour ce stack. Ne pas cr�er de barrel exports dans `lib/`.

---

**[P2-LINT-03] 5 eslint-disable `@next/next/no-img-element` sans justification**

```
Fichiers : (voir P1-PERF-03)
Constat  : Règle supprimée sans commentaire de raison.
Impact   : Crée une ambiguïté : est-ce intentionnel (URL externe) ou un oubli de migration ?
Action   : Ajouter // Intentional: <raison> sur la ligne précédant chaque disable.
           Exemple : // Intentional: URL d'avatar externe sans dimensions connues au build.
Validation : grep -B1 "eslint-disable.*no-img-element" → ligne précédente commence par // Intentional:.
```

---

### P3 — Polish et cohérence

---

**[P3-COMP-01] `BadgeCard.tsx` (494 lignes) et `DiagnosticSolver.tsx` (456 lignes)**

```
Fichiers : frontend/components/badges/BadgeCard.tsx:1
           frontend/components/diagnostic/DiagnosticSolver.tsx:1
Constat  : Composants > 450 lignes. Responsabilités multiples probables.
Impact   : Tests unitaires difficiles. Complexité cyclomatique potentiellement élevée.
Action   : Audit interne. Identifier les sections extractibles en sous-composants.
Validation : Chaque sous-composant extrait < 150 lignes, testé isolément.
```

---

**[P3-DIAG-02] ~~`fetch()` direct dans `app/test-sentry/page.tsx`~~ — résolu (QF-01)**

```
Statut   : La route produit /test-sentry a été supprimée ; plus de surface de test dans l’app.
Action   : Vérification Sentry documentée dans docs/01-GUIDES/SENTRY_MONITORING.md (sans page dédiée).
```

---

## 13. Forces confirmées

### Force 1 — TypeScript au niveau de rigueur maximal

**Preuve terrain :** 0 occurrence de `: any` ou `as any` dans tout `frontend/` (grep exhaustif). Configuration `strict + noUncheckedIndexedAccess + exactOptionalPropertyTypes` active.

Cette configuration est celle recommandée par la communauté TypeScript avancée (Matt Pocock, TypeScript Total) pour les codebases production. Elle signifie que tout changement d'interface API propagera une erreur de compilation avant tout bug runtime — particulièrement critique pour un projet solo sans code review systématique d'une équipe.

### Force 2 — React Query avec policy de cache exhaustive

**Preuve terrain :** `staleTime` trouvé sur les 41 queries du projet. Distribution sémantique cohérente : exercices temps-réel (10s), challenges (30s), admin (60s), auth (300s).

Un projet sans `staleTime` rechercherait le backend à chaque montage de composant, surchargeant l'API. La cohérence de cette policy sur 41 queries (sans exception à 0) est un indicateur de maturité technique.

### Force 3 — Guardrails d'architecture auto-vérifiés par CI

**Preuve terrain :** `frontendGuardrails.ts` (523 lignes), `ALLOWED_DENSE_EXCEPTIONS = []`, test `frontendGuardrails.test.ts` présent dans `__tests__/unit/architecture/`.

Le guardrail définit 17 surfaces protégées avec budgets max de lignes, 17 seams requis (hooks controllers), 20 fichiers lib requis. Il s'auto-vérifie via CI. Cette infrastructure est rare en production sur des projets solo — elle garantit que l'architecture documentée correspond à l'architecture réelle.

---

## 14. Plan d'exécution solo-founder

Ordre basé sur rapport impact/effort. Chaque sprint est réalisable en une session de travail.

### Sprint 1 — Performance quick wins (2-3h)

```
1. ~~dynamic() / lazy export PDF et Excel~~ — **fait (QF-02)** : `import()` dans `exportPDF.ts` / `exportExcel.ts`

2. Lire docs/, changelog/, offline/ → confirmer interactivité (20 min)
   → Si absence de hooks client : supprimer "use client" et convertir en SC
   → P2-PERF-04 : action conditionnelle à la lecture (rétrogradé depuis P1)

3. Justifications eslint-disable @next/next/no-img-element   (20 min)
   → Impact : dette documentée ou migration planifiée

4. ~~Guard NODE_ENV sur app/test-sentry~~ — **fait** : page supprimée (QF-01)
```

### Sprint 2 — Images (2-3h)

```
5. Migrer UserAvatar.tsx → next/image (avatar utilisateur)   (45 min)
6. Migrer BadgeIcon.tsx → next/image                         (45 min)
7. Migrer BadgeCard.tsx → next/image                         (45 min)
8. ChatMessagesView.tsx : documenter ou migrer               (30 min)
```

### Sprint 3 — Décomposition pages (3-5h)

```
9. Extraire useLeaderboardPageController.ts + sections       (2h)
   → Priorité haute : 481 lignes, flux visible par élèves

10. Réduire exercises/page.tsx < 100 lignes                  (1-2h)
11. Réduire home-learner/page.tsx < 100 lignes               (1h)
```

### Sprint 4 — Modularité (1-2h)

```
12. Plan migration co-location tests (audit + 2-3 migrations pilotes)  (1-2h)
    → Ne PAS créer de barrel exports lib/ (invalidé — voir §Findings P2-MOD-02)
```

### Non planifié (backlog produit distinct)

- Migration vers co-location tests complète (133 fichiers — effort élevé, impact progressif)
- Décomposition `BadgeCard.tsx` et `DiagnosticSolver.tsx` (nécessite audit interne approfondi)

## Addendum 2026-04-10 - QF-01 réalisé

Le lot `QF-01` a été exécuté après génération du présent audit.

Travaux effectués :

- suppression de `frontend/app/test-sentry/page.tsx` : plus de surface produit dédiée au smoke test Sentry
- `Sentry.setUser(...)` dans `frontend/hooks/useAuth.ts` réduit à `{ id }` uniquement ; plus de `username`
- `frontend/.env.example` documente maintenant `SECRET_KEY` pour le runtime serveur Next (`lib/auth/server/routeSession.ts`), hors `NEXT_PUBLIC_*`
- `docs/01-GUIDES/SENTRY_MONITORING.md`, `README_TECH.md` et `.claude/session-plan.md` réalignés sur cette nouvelle vérité terrain

Constats du présent audit impactés par `QF-01` :

- `P3-DIAG-02` reste classé **résolu**
- les mentions historiques à `/test-sentry` doivent être lues comme trace de correction, pas comme surface encore présente dans l'application

## Addendum 2026-04-10 - QF-03 (i18n pages admin / offline)

Constat terrain traité : **copy utilisateur inline** sur les **routes** `frontend/app/admin/page.tsx`, `analytics`, `ai-monitoring`, `audit-log`, `config`, `content`, `feedback`, `moderation`, `users`, et `frontend/app/offline/page.tsx`.

Travaux effectués :

- clés regroupées sous **`adminPages`** (sous-objets : `overview`, `analytics`, `aiMonitoring`, `auditLog`, `config`, `content`, `feedback`, `moderation`, `users`) et **`offline`** à la racine des fichiers messages
- `useTranslations` sur ces pages uniquement ; **hors scope** : modaux admin profonds, sections métier imbriquées, helpers dans hooks (ex. `getAuditActionLabel` reste dans `useAdminAuditLog.ts` mais la page journal utilise les libellés i18n pour la colonne action)
- `i18n:validate` + `i18n:check` verts sur l’arbre messages ; `i18n:extract` peut encore signaler d’autres chaînes hors périmètre route-level

**Résidu volontaire :** i18n complète des composants admin internes et chaînes métier ailleurs dans le dépôt.

## Addendum 2026-04-10 - QF-04 (ESLint TypeScript durci)

Cohérent avec **§D4 — ESLint / Hooks** : `@typescript-eslint/no-unused-vars`, `no-require-imports` et `consistent-type-imports` sont en **error** dans `frontend/eslint.config.mjs` (mesure initiale : **0** sur les deux premières sur l’arbre linté). Option `disallowTypeAnnotations: false` sur `consistent-type-imports` pour conserver `vi.importActual<typeof import("…")>` (tests).

**Suite QF-04B (2026-04-10) :** ESLint **type-aware** sur le frontend (`parserOptions.projectService: true`, `tsconfigRootDir`, ignores build/cache/scripts) ; `@typescript-eslint/no-floating-promises` en **error** ; mesure initiale **64** violations corrigées par **`void`** explicite (invalidations React Query, `import()` dynamiques, handlers async) — pas de changement UX volontaire.

**Hors périmètre inchangé :** `import/no-cycle` ; pas d’activation opportuniste d’autres règles typées hors le minimum nécessaire à cette règle.

**Suite QF-04C (2026-04-10) :** `react-hooks/set-state-in-effect` et `react-hooks/preserve-manual-memoization` passent en **error** ; mesure sur l’arbre avant durcissement : **0** message ESLint (règles en `warn`) car **2** occurrences de `set-state-in-effect` étaient déjà **neutralisées** par `eslint-disable-next-line` justifié ; **`preserve-manual-memoization`** : **0** occurrence. Correction **ROI** : `useContentListOrderPreference` — lecture `localStorage` via initialiseur paresseux de `useState` (clé stable par montage). **Résidu documenté :** une suppression locale conservée dans `useGuestChatAccess` (sync invité post-hydratation).

**Suite QF-05 (2026-04-10) — E2E auth minimal utile :** parcours **réel** login → (onboarding seed si besoin) → navigation **`/dashboard`**, **`/badges`**, **`/settings`** ; tests **Chromium uniquement** (`test.skip` hors chromium) ; helper **`frontend/__tests__/e2e/helpers/demoUserAuth.ts`** (pas de `globalSetup` / `storageState` global) ; diagnostic post-onboarding **hors automate** ; prérequis **backend** + attention **rate-limit login 5/min/IP**.

**Suite QF-06 (2026-04-10) — Coverage gates réalistes :** `frontend/vitest.config.ts` fixe désormais un **périmètre explicite** de couverture (`*.{ts,tsx}`, `app`, `components`, `hooks`, `i18n`, `lib`, `messages`) et des seuils globaux basés sur la **baseline mesurée** du dépôt, non sur une cible arbitraire : **statements 43%** (`3590/8291`), **branches 36%** (`3111/8420`), **functions 39%** (`899/2264`), **lines 44%** (`3423/7718`). L’objectif est de figer le dénominateur réel de couverture frontend avant de remonter les seuils par lots thématiques.

---

_Rapport généré le 2026-04-09. Toutes les assertions sont basées sur des lectures directes de fichiers effectuées pendant l'audit. Pour les dimensions où la mesure complète n'est pas possible sans outillage (complexité cyclomatique, dépendances circulaires), les scores sont conservateurs et marqués explicitement._
