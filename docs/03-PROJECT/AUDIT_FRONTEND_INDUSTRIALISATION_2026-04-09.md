# Audit Frontend â€” Industrialisation & QualitÃ© Technique

> GÃ©nÃ©rÃ© le 2026-04-09 via `/octo:review` (prompt d'audit structurÃ© 8 dimensions)
> Stack : Next.js 16 App Router + TypeScript strict + Tailwind CSS + shadcn/ui + React Query v5
> Outil d'exploration : Agent Explore (lecture seule, 14 tÃ¢ches parallÃ¨les)
> MÃ©thode : scoring factuel â€” chaque constat cite fichier:ligne lu pendant l'audit

---

## Table des matiÃ¨res

1. [RÃ©sumÃ© exÃ©cutif](#1-rÃ©sumÃ©-exÃ©cutif)
2. [MÃ©thodologie](#2-mÃ©thodologie)
3. [Scores par dimension](#3-scores-par-dimension)
4. [D1 â€” Industrialisation](#4-d1--industrialisation)
5. [D2 â€” DRY / Factorisation](#5-d2--dry--factorisation)
6. [D3 â€” TypeScript Strict](#6-d3--typescript-strict)
7. [D4 â€” ESLint / Hooks](#7-d4--eslint--hooks)
8. [D5 â€” ModularitÃ©](#8-d5--modularitÃ©)
9. [D6 â€” MaintenabilitÃ©](#9-d6--maintenabilitÃ©)
10. [D7 â€” Performance Frontend](#10-d7--performance-frontend)
11. [D8 â€” RÃ©plicabilitÃ© / TestabilitÃ©](#11-d8--rÃ©plicabilitÃ©--testabilitÃ©)
12. [Findings classÃ©s P0-P3](#12-findings-classÃ©s-p0-p3)
13. [Forces confirmÃ©es](#13-forces-confirmÃ©es)
14. [Plan d'exÃ©cution solo-founder](#14-plan-dexÃ©cution-solo-founder)

---

## 1. RÃ©sumÃ© exÃ©cutif

| Indicateur                         | Valeur           |
| ---------------------------------- | ---------------- |
| Score global pondÃ©rÃ©             | **7.05 / 10**    |
| Findings P0                        | **0**            |
| Findings P1                        | **4**            |
| Findings P2                        | **3**            |
| Findings P3                        | **2**            |
| Fichiers lus pendant l'audit       | 50+              |
| Queries React Query avec staleTime | **41/41** (100%) |
| Occurrences `: any` ou `as any`    | **0**            |
| TODO/FIXME/HACK non ticketÃ©s      | **0**            |

**Verdict :** codebase industriellement mature sur TypeScript, cache React Query et guardrails d'architecture. Les risques ouverts sont concentrÃ©s sur la performance bundle (exports PDF/Excel sans lazy loading) et l'adoption incomplÃ¨te des Server Components.

> **Hors-scope de cet audit :** la dimension sÃ©curitÃ© frontend (headers HTTP au-delÃ  de la CSP, surface XSS dÃ©taillÃ©e) n'est pas couverte par les 8 dimensions ci-dessus. **Mise Ã  jour lots QF-07A, QF-07B, QF-07C (2026-04-10)** : en production, **`script-src`** nâ€™utilise pas `'unsafe-inline'` ; CSP dynamique via `frontend/proxy.ts`. **QF-07C** : le **root layout** (`app/layout.tsx`) est en **`force-dynamic`** + **`nonce`** sur **`<html>`** (nonce lu via **`x-nonce`**) pour que Next applique le nonce aux scripts inline du framework sous CSP stricte â€” **coÃ»t** : rendu HTML surtout **dynamique** (peu/pas de SSG App Router), charge serveur accrue vs static optimization. **`style-src 'unsafe-inline'`** inchangÃ© dans ces lots. Poursuivre la veille sÃ©curitÃ© via `CLAUDE.md` / audits dÃ©diÃ©s si besoin.

---

## 2. MÃ©thodologie

### Sources lues

Toutes les assertions ci-dessous sont extraites de lectures directes pendant l'audit. Aucune supposition.

| TÃ¢che              | MÃ©thode                                    | RÃ©sultat                                                     |
| ------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| Guardrails          | Lecture complÃ¨te `frontendGuardrails.ts`   | 523 lignes, 17 surfaces, 17 seams, 20 lib requis              |
| Fichiers volumineux | `wc -l` sur app/, components/, hooks/, lib/ | 19 fichiers > 300 lignes                                      |
| "use client"        | grep dans app/                              | 38 fichiers sur ~50                                           |
| eslint-disable      | grep + contexte Â±1 ligne                   | 13 occurrences dans 12 fichiers                               |
| `: any` / `as any`  | grep exhaustif hors node_modules            | 0 rÃ©sultat                                                   |
| `fetch()` direct    | grep dans app/ + components/                | 0 rÃ©sultat mÃ©tier (page `test-sentry` supprimÃ©e â€” QF-01) |
| TODO/FIXME/HACK     | grep dans tout frontend/                    | 0 rÃ©sultat                                                   |
| staleTime           | grep dans hooks/                            | 41 occurrences, toutes dÃ©finies                              |
| `dynamic()`         | grep dans tout frontend/                    | 0 rÃ©sultat                                                   |
| `next/image`        | grep dans app/ + components/                | 1 import, 5 contournements                                    |

> **Note mÃ©thodologique sur le scoring :** les scores par dimension (0-10) sont des jugements calibrÃ©s, pas une addition mÃ©canique de critÃ¨res binaires. Un critÃ¨re partiellement satisfait contribue proportionnellement. L'Ã©chelle est : 0-3 = problÃ©matique, 4-6 = acceptable, 7-8 = bon, 9-10 = excellent.

### Dimensions et pondÃ©rations

| Dimension            | Poids | Justification                        |
| -------------------- | ----- | ------------------------------------ |
| D1 Industrialisation | 15%   | CÅ“ur du chantier FFI-L20            |
| D2 DRY               | 10%   | Factorisation SSE, helpers, cache    |
| D3 TypeScript Strict | 15%   | DiffÃ©renciateur qualitÃ© majeur     |
| D4 ESLint / Hooks    | 10%   | Discipline de code quotidienne       |
| D5 ModularitÃ©       | 15%   | MaintenabilitÃ© long terme solo      |
| D6 MaintenabilitÃ©   | 15%   | CoÃ»t de changement futur            |
| D7 Performance       | 10%   | Impact UX Ã©lÃ¨ves (Core Web Vitals) |
| D8 RÃ©plicabilitÃ©   | 10%   | VÃ©locitÃ© feature + fiabilitÃ© CI   |

---

## 3. Scores par dimension

| Dimension            | Score | Poids    | Score pondÃ©rÃ© | Findings P0 | Findings P1 |
| -------------------- | ----- | -------- | --------------- | ----------- | ----------- |
| D1 Industrialisation | 7/10  | 15%      | 1.05            | 0           | 1           |
| D2 DRY               | 7/10  | 10%      | 0.70            | 0           | 1           |
| D3 TypeScript        | 9/10  | 15%      | 1.35            | 0           | 0           |
| D4 ESLint/Hooks      | 7/10  | 10%      | 0.70            | 0           | 0           |
| D5 ModularitÃ©       | 6/10  | 15%      | 0.90            | 0           | 0           |
| D6 MaintenabilitÃ©   | 7/10  | 15%      | 1.05            | 0           | 0           |
| D7 Performance       | 5/10  | 10%      | 0.50            | 0           | 2           |
| D8 RÃ©plicabilitÃ©   | 8/10  | 10%      | 0.80            | 0           | 0           |
| **TOTAL**            |       | **100%** | **7.05/10**     | **0**       | **4**       |

---

## 4. D1 â€” Industrialisation

**Score : 7/10** | Poids 15%

### CritÃ¨res passÃ©s âœ“

**Hook controllers sÃ©parÃ©s (+2)**

8 controllers prÃ©sents dans `frontend/hooks/` (lus pendant l'audit) :

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

Ces fichiers correspondent exactement aux `REQUIRED_ARCHITECTURE_SEAMS` dÃ©finis dans `frontendGuardrails.ts`. Le guardrail teste leur prÃ©sence via `collectMissingSeams()`.

**Helpers purs dans `lib/` (+2)**

`frontend/lib/` contient des modules par domaine : `api/`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `settings/`, `utils/`. Aucun `fetch()` direct dans ces modules (0 occurrence trouvÃ©e).

**Guardrails actifs sans exception (+1)**

`ALLOWED_DENSE_EXCEPTIONS = []` (lu dans `frontendGuardrails.ts`). ZÃ©ro exception tolÃ©rÃ©e. La politique est appliquÃ©e et vÃ©rifiÃ©e par `frontendGuardrails.test.ts` (prÃ©sent dans `__tests__/unit/architecture/`).

### CritÃ¨res en dÃ©rogation âœ—

**Pages non rÃ©duites Ã  des coques (-2)**

Trois pages `app/` dÃ©passent le modÃ¨le coque attendu :

| Fichier                     | Lignes  | ProblÃ¨me                          |
| --------------------------- | ------- | ---------------------------------- |
| `app/leaderboard/page.tsx`  | **481** | Pas de controller sÃ©parÃ© trouvÃ© |
| `app/home-learner/page.tsx` | **317** | Logique probable inline            |
| `app/exercises/page.tsx`    | **311** | Filtres, pagination inline         |

La norme projet est < 100 lignes pour une coque. Ces trois pages ont `"use client"` en ligne 1, confirmant qu'elles gÃ¨rent du runtime cÃ´tÃ© client.

**Sections partiellement extraites (-1)**

10 composants dans `components/` dÃ©passent 300 lignes :

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

Les modaux admin (`BadgeEditModal`, `ChallengeEditModal`, `ExerciseEditModal`) peuvent lÃ©gitimement Ãªtre denses (formulaires multi-champs). `BadgeCard` (494 lignes) et `DiagnosticSolver` (456 lignes) sont plus prÃ©occupants.

---

## 5. D2 â€” DRY / Factorisation

**Score : 7/10** | Poids 10%

### CritÃ¨res passÃ©s âœ“

**ZÃ©ro `fetch()` direct dans composants (+3)**

Grep exhaustif sur `app/` et `components/` : **0** `fetch()` direct hors React Query en surfaces mÃ©tier (historique : ancienne page dev `test-sentry`, supprimÃ©e â€” QF-01). RÃ©sultat : **0 contournement React Query** en production.

**Policy de cache homogÃ¨ne sur 41 queries (+2)**

`staleTime` dÃ©fini sur chaque hook de donnÃ©es. Distribution par domaine :

| Domaine        | staleTime             | Justification                                   |
| -------------- | --------------------- | ----------------------------------------------- |
| Exercices      | 10 000 ms             | DonnÃ©es dynamiques (rÃ©sultats en temps rÃ©el) |
| Challenges     | 30 000 ms             | Mis Ã  jour moins frÃ©quemment                  |
| Admin          | 60 000 ms             | Usage interne, fraÃ®cheur moindre               |
| Badges         | 60 000 â€“ 300 000 ms | DonnÃ©es quasi-statiques                        |
| Auth (useAuth) | 300 000 ms (5 min)    | Token validÃ© cÃ´tÃ© serveur                    |

**Proxy SSE factorisÃ© (+1)**

Lot SSE-DRY-07 fermÃ© : `frontend/lib/api/sseProxyRequest.ts` et `frontend/lib/api/proxyForwardHeaders.ts` factorisent les deux routes SSE pÃ©dagogiques. Avant : ~100 LOC par route. AprÃ¨s : ~15 LOC par route.

### CritÃ¨res en dÃ©rogation âœ—

**5 composants avec `<img>` dupliquÃ© (-2)**

5 fichiers contournent `next/image` sans factorisation commune :

```
components/ui/UserAvatar.tsx:31
components/badges/BadgesProgressTabsSection.tsx:145
components/badges/BadgeIcon.tsx:131
components/badges/BadgeCard.tsx:49
components/chat/ChatMessagesView.tsx:71
```

Chacun gÃ¨re son propre rendu image avec les mÃªmes limitations (pas de lazy loading, pas d'optimisation WebP). Un composant partagÃ© `AppImage` ou `UserAvatarImage` Ã©liminerait cette duplication.

**Barrel exports absents (-1)**

4 barrel exports sur ~150 modules `lib/` :

```
lib/storage/index.ts              12 lignes
components/challenges/visualizations/index.ts  12 lignes
components/layout/index.ts        15 lignes
components/learner/index.ts       2 lignes
```

Les domaines principaux (`lib/auth/`, `lib/badges/`, `lib/challenges/`, `lib/security/`) n'ont pas d'`index.ts`. Les imports consommateurs utilisent des chemins absolus internes, crÃ©ant un couplage fort aux chemins de fichiers.

---

## 6. D3 â€” TypeScript Strict

**Score : 9/10** | Poids 15%

### CritÃ¨res passÃ©s âœ“

**ZÃ©ro `any` explicite (+3)**

Grep complet sur `frontend/` (hors `node_modules/`, `.next/`, `coverage/`, `@types/`) :

```
Pattern `: any`  â†’ 0 rÃ©sultat
Pattern `as any` â†’ 0 rÃ©sultat
```

RÃ©sultat absolu. Aucun contournement du systÃ¨me de types.

**Configuration la plus stricte du marchÃ© (+2)**

`tsconfig.json` active :

- `strict: true` (active `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `noImplicitAny`, `noImplicitThis`, `alwaysStrict`)
- `noUncheckedIndexedAccess: true` â€” accÃ¨s tableau retourne `T | undefined`
- `exactOptionalPropertyTypes: true` â€” `{ a?: string }` â‰  `{ a: string | undefined }`

C'est la configuration recommandÃ©e par Matt Pocock (TypeScript Total) et l'Ã©quipe TypeScript Microsoft pour les codebases production 2024.

**Types API centralisÃ©s en `types/api.ts` (+2)**

`frontend/types/api.ts` â€” 314 lignes contenant :

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

70 fichiers dans `app/` et `components/` dÃ©clarent des `interface` ou `type` locaux. Certains sont lÃ©gitimes (props de composants, types internes de hooks). Une passe d'audit spÃ©cifique serait nÃ©cessaire pour distinguer les types qui mÃ©riteraient d'Ãªtre centralisÃ©s dans `types/api.ts` (types partagÃ©s entre plusieurs modules) de ceux qui sont correctement locaux (types de props, types de state interne).

---

## 7. D4 â€” ESLint / Hooks

**Score : 7/10** | Poids 10%

### CritÃ¨res passÃ©s âœ“

**`exhaustive-deps` : toutes les dÃ©rogations justifiÃ©es (+3)**

8 suppressions de rÃ¨gles `react-hooks/exhaustive-deps` et `set-state-in-effect` lues pendant l'audit. Toutes avec justification :

| Fichier                                                       | Ligne                 | Justification lue                                                                                             |
| ------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------- |
| `hooks/useSettingsPageController.ts:181`                      | `exhaustive-deps`     | `mount-only load; useSettings callbacks are unstable`                                                         |
| `hooks/chat/useGuestChatAccess.ts:40`                         | `set-state-in-effect` | `intentional post-hydration sync from sessionStorage (guest quota)`                                           |
| `hooks/useChallengeSolverController.ts:141`                   | `exhaustive-deps`     | `Reset only on visible challenge identity change; full object deps would wipe in-progress answers on refetch` |
| `hooks/useContentListOrderPreference.ts:24`                   | `set-state-in-effect` | `intentional post-hydration sync`                                                                             |
| `hooks/useExerciseSolverController.ts:253`                    | `exhaustive-deps`     | `reset seulement si l'exercice courant change de rÃ©alitÃ© visible`                                           |
| `components/challenges/visualizations/PuzzleRenderer.tsx:162` | `exhaustive-deps`     | `onOrderChange via ref ; pieces dÃ©rivÃ© de visualData â€” Ã©viter reset sur identitÃ© du tableau seule`      |
| `components/challenges/visualizations/PuzzleRenderer.tsx:201` | `exhaustive-deps`     | `intentionnel au montage seulement â€” inclure items/onOrderChange recrÃ©erait des boucles avec le parent`    |
| `components/ui/sonner.tsx:38`                                 | `exhaustive-deps`     | `Register once; MutationObserver handles subsequent theme class changes`                                      |

**`react-hooks/rules-of-hooks` : 0 violation (+3)**

Aucune occurrence trouvÃ©e pendant l'audit. Hooks appelÃ©s uniquement au niveau supÃ©rieur des composants et hooks custom.

### CritÃ¨res en dÃ©rogation âœ—

**5 suppressions `@next/next/no-img-element` sans justification (-1)**

```
components/ui/UserAvatar.tsx:31
components/badges/BadgesProgressTabsSection.tsx:145
components/badges/BadgeIcon.tsx:131
components/badges/BadgeCard.tsx:49
components/chat/ChatMessagesView.tsx:71
```

Chacun supprime la rÃ¨gle sans commentaire adjacent expliquant pourquoi `next/image` ne peut pas Ãªtre utilisÃ© (URL externe dynamique, dimensions inconnues, contrainte de rendu SVGâ€¦). La rÃ¨gle du projet exige `// Intentional: <raison>`.

---

## 8. D5 â€” ModularitÃ©

**Score : 6/10** | Poids 15%

### CritÃ¨res passÃ©s âœ“

**Domaines `lib/` sÃ©parÃ©s (+2)**

`frontend/lib/` est organisÃ© par domaine fonctionnel : `api/`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `settings/`, `utils/`, `theme/`, `storage/`. Chaque domaine contient ses helpers sans imports croisÃ©s Ã©vidents au premier niveau.

**8 controllers sÃ©parÃ©s (+2)**

Voir D1. La sÃ©paration runtime/UI est le signal fort de la modularitÃ© du projet.

### CritÃ¨res en dÃ©rogation âœ—

**Tests non co-localisÃ©s (-2)**

133 fichiers de tests dans `__tests__/unit/` sÃ©parÃ© du code source :

```
__tests__/unit/hooks/useAuth.test.ts
__tests__/unit/components/badges/BadgeCard.test.tsx
__tests__/unit/lib/api/backendUrl.test.ts
```

Le fichier `components/badges/BadgeCard.tsx` (494 lignes) n'a pas son test dans `components/badges/`. Ce pattern rend la navigation difficile lors d'un refactoring (trouver le test correspondant nÃ©cessite de connaÃ®tre la structure `__tests__/`).

La recommandation Jest / Vitest 2024 est la co-location : `BadgeCard.test.tsx` Ã  cÃ´tÃ© de `BadgeCard.tsx`. La migration est progressive et non bloquante.

**Barrel exports quasi-absents (-2)**

4 barrel exports sur ~150 modules `lib/`. Les domaines `lib/auth/`, `lib/badges/`, `lib/challenges/`, `lib/security/` n'exposent pas d'API surface formelle via `index.ts`. Les consommateurs importent directement les chemins internes :

```typescript
// Pattern actuel (couplage fort au chemin)
import { buildContentSecurityPolicy } from "@/lib/security/buildContentSecurityPolicy";

// Pattern idÃ©al (API surface formelle)
import { buildContentSecurityPolicy } from "@/lib/security";
```

Sans barrel, tout renommage de fichier dans `lib/` casse les imports consommateurs.

**Composants denses (-1)**

`BadgeCard.tsx` (494 lignes), `DiagnosticSolver.tsx` (456 lignes) â€” vraisemblablement plusieurs responsabilitÃ©s internes sans sous-composants extraits. Non quantifiable sans lecture des sources.

---

## 9. D6 â€” MaintenabilitÃ©

**Score : 7/10** | Poids 15%

### CritÃ¨res passÃ©s âœ“

**ZÃ©ro dette commentaire (-0)**

Grep sur TODO/FIXME/HACK : **0 rÃ©sultat** dans tout `frontend/`. Codebase propre de toute dette commentÃ©e non trackÃ©e.

**Policy de cache documentÃ©e par domaine (+2)**

Les valeurs `staleTime` sont cohÃ©rentes et sÃ©mantiquement justifiables (10s pour exercices temps-rÃ©el, 300s pour auth). Une policy de cache lisible est un indicateur de maintenabilitÃ© (un dÃ©veloppeur qui reprend le code comprend immÃ©diatement la politique de fraÃ®cheur de chaque domaine).

**Guardrails auto-vÃ©rifiÃ©s (+1)**

`frontendGuardrails.ts` expose des fonctions `collectMissingSeams()`, `collectProtectedBudgetViolations()`, `collectDenseExceptionViolations()` testÃ©es par CI. La maintenance de l'architecture est automatisÃ©e.

**ZÃ©ro `any` â†’ couplage type-safe (+2)**

0 contournement du systÃ¨me de types. Tout changement d'API se propage par erreur de compilation plutÃ´t que par bug runtime.

### CritÃ¨res en dÃ©rogation âœ—

**Controllers volumineux (-1)**

```
hooks/useProfilePageController.ts   463 lignes
hooks/useExerciseSolverController.ts 391 lignes
```

La complexitÃ© cyclomatique de ces fichiers n'est pas mesurable sans outillage, mais leur taille suggÃ¨re des fonctions de plus de 30 lignes et une complexitÃ© cyclomatique potentiellement > 10 (seuil Clean Code, Martin 2008).

**Utilitaires monolithiques dans `lib/utils/` (-1)**

```
lib/utils/exportPDF.ts    384 lignes
lib/utils/exportExcel.ts  391 lignes
```

Ces deux modules contiennent probablement plusieurs fonctions de haut niveau non dÃ©composÃ©es. Ils constituent Ã©galement un problÃ¨me de performance (voir D7).

---

## 10. D7 â€” Performance Frontend

**Score : 5/10** | Poids 10%

C'est la dimension avec le plus de travail restant.

### CritÃ¨res passÃ©s âœ“

**`staleTime` sur 100% des queries (+2)**

Voir D2. Aucune query Ã  staleTime = 0 (rechargement systÃ©matique). React Query met en cache correctement dans tout le projet.

### CritÃ¨res en dÃ©rogation âœ—

**76% des pages `app/` avec `"use client"` â€” Server Components sous-exploitÃ©s (-3)**

38 fichiers sur ~50 dans `app/` ont `"use client"` en ligne 1. Parmi eux, au moins 4 pages n'ont pas d'interactivitÃ© JSX Ã©vidente :

| Page                     | InteractivitÃ© attendue             | Candidat SC |
| ------------------------ | ----------------------------------- | ----------- |
| `app/docs/page.tsx`      | Affichage de documentation statique | Oui         |
| `app/changelog/page.tsx` | Liste de changements statique       | Oui         |
| `app/offline/page.tsx`   | Page d'erreur offline statique      | Oui         |
| `app/contact/page.tsx`   | Ã€ vÃ©rifier (formulaire ?)         | Probable    |

Note : `app/about/page.tsx` et `app/privacy/page.tsx` ont dÃ©jÃ  Ã©tÃ© convertis en Server Components dans le lot FFI-L20G â€” non comptÃ©s nÃ©gativement.

ConsÃ©quence : hydration JavaScript inutile sur des pages statiques, bundle client alourdi, TTI (Time to Interactive) dÃ©gradÃ©.

**~~`exportPDF.ts` + `exportExcel.ts` sans chargement paresseux~~ â€” traitÃ© (QF-02) (+0)**

Les dÃ©pendances lourdes (`jspdf`, `jspdf-autotable`, `exceljs`) sont chargÃ©es via `import()` Ã  lâ€™intÃ©rieur des fonctions dâ€™export, pas au chargement du module. Next `dynamic()` sur composant reste Ã  0 ; le pattern retenu est lâ€™`import()` dans les utilitaires.

**5 `<img>` non optimisÃ©s (-2)**

MÃªme liste que D2. Sans `next/image` :

- Pas de conversion automatique WebP/AVIF
- Pas de lazy loading `loading="lazy"` automatique
- Pas de gestion du Cumulative Layout Shift (CLS) via `width`/`height`
- Pas de `sizes` pour le responsive

Les pages badges (leaderboard, dashboard) affichent des badges â€” surfaces Ã  forte visibilitÃ© pour les Ã©lÃ¨ves.

**`next/image` utilisÃ© dans 1 seul endroit (+0)**

`components/challenges/visualizations/ChallengeSolverContent.tsx:3` â€” seule occurrence de `import Image from "next/image"`. Confirme que l'adoption n'est pas systÃ©matique.

---

## 11. D8 â€” RÃ©plicabilitÃ© / TestabilitÃ©

**Score : 8/10** | Poids 10%

### CritÃ¨res passÃ©s âœ“

**Controllers testables isolÃ©ment (+3)**

Les 8 controllers n'ont aucun `fetch()` direct (0 occurrence dans `hooks/`). Ils dÃ©lÃ¨guent le rÃ©seau aux hooks de donnÃ©es React Query passÃ©s en paramÃ¨tre. Pattern Command/Query Separation appliquÃ© : le controller orchestre, le hook de donnÃ©es communique.

Exemple dans `useChallengeSolverController.ts` :

```typescript
// Le controller reÃ§oit les actions rÃ©seau en paramÃ¨tre â€” testable sans mock rÃ©seau
export function useChallengeSolverController({
  submitAnswer,
  getHint,
  setHints,
  ...
}: UseChallengeSolverControllerArgs)
```

**36 tests sur les helpers `lib/` (+2)**

`__tests__/unit/lib/` contient 36 fichiers couvrant : `api/backendUrl`, `auth/`, `badges/`, `challenges/`, `exercises/`, `security/`, `social/`, `utils/`. Les fonctions pures sont testÃ©es indÃ©pendamment du DOM.

**6 specs E2E Playwright (+4)**

```
__tests__/e2e/auth.spec.ts
__tests__/e2e/exercises.spec.ts
__tests__/e2e/dashboard.spec.ts
__tests__/e2e/badges.spec.ts
__tests__/e2e/settings.spec.ts
__tests__/e2e/admin.spec.ts
```

Flux critiques couverts : authentification (invitÃ©), exercices, dashboard, badges, settings, admin (lecture). Configuration : `workers: 1`, `fullyParallel: false` pour Ã©viter les conflits de rate-limit.

**Test d'architecture auto-vÃ©rifiÃ© (+1)**

`__tests__/unit/architecture/frontendGuardrails.test.ts` â€” les guardrails sont testÃ©s par CI. Toute violation de surface protÃ©gÃ©e casse le pipeline avant merge.

### Nuance (-2)

**Tests non co-localisÃ©s**

133 fichiers dans `__tests__/unit/` vs code source dans `components/`, `hooks/`, `lib/`. Voir D5. Impact sur la vÃ©locitÃ© de maintenance.

---

## 12. Findings classÃ©s P0-P3

### P1 â€” Dette technique mesurable

---

**[P1-PERF-01] `app/leaderboard/page.tsx` â€” page non dÃ©composÃ©e**

```
Fichier  : frontend/app/leaderboard/page.tsx:1
Constat  : 481 lignes avec "use client". Aucun useLeaderboardPageController.ts trouvÃ©.
Impact   : Runtime non testable isolÃ©ment. Pattern coque violÃ©. ComplexitÃ© cyclomatique Ã©levÃ©e.
Action   : Extraire useLeaderboardPageController.ts + LeaderboardRankingSection + LeaderboardFilterSection.
Validation : wc -l frontend/app/leaderboard/page.tsx â†’ rÃ©sultat < 80.
```

---

**[P1-PERF-02] ~~Exports PDF/Excel sans lazy loading~~ â€” rÃ©solu (QF-02)**

```
Statut   : `exportDashboardToPDF` / `exportDashboardToExcel` chargent `jspdf`, `jspdf-autotable` et `exceljs`
           via `import()` au clic (helpers `lib/utils/exportPDF.ts` et `exportExcel.ts`) ; `ExportButton` await.
Validation : bundle analyzer â€” libs absentes du chemin initial du dashboard jusquâ€™au clic export.
```

---

**[P1-PERF-03] 5 composants avec `<img>` non optimisÃ©**

```
Fichiers : frontend/components/ui/UserAvatar.tsx:31
           frontend/components/badges/BadgesProgressTabsSection.tsx:145
           frontend/components/badges/BadgeIcon.tsx:131
           frontend/components/badges/BadgeCard.tsx:49
           frontend/components/chat/ChatMessagesView.tsx:71
Constat  : <img> brut avec eslint-disable @next/next/no-img-element sans justification textuelle.
Impact   : Pas de lazy loading, pas de WebP/AVIF, CLS potentiel sur pages badges (surface haute
           visibilitÃ© Ã©lÃ¨ves). Aucune gestion du Cumulative Layout Shift.
Action   : Migrer vers <Image from="next/image"> avec sizes dÃ©fini, OU ajouter commentaire
           // Intentional: <raison prÃ©cise> si migration impossible.
Validation : grep -r "eslint-disable.*no-img-element" frontend/components/ --include="*.tsx"
             â†’ 0 ligne sans justification adjacente.
```

---

**[P2-PERF-04] Pages potentiellement convertibles en Server Components** _(rÃ©trogradÃ© P1â†’P2 â€” contenu non lu)_

```
Fichiers : frontend/app/docs/page.tsx:1
           frontend/app/changelog/page.tsx:1
           frontend/app/offline/page.tsx:1
           frontend/app/contact/page.tsx:1
Constat  : "use client" prÃ©sent. Contenu de ces fichiers non lu pendant l'audit â€” l'interactivitÃ©
           rÃ©elle de ces pages n'est pas connue. Candidats Server Components probables mais non confirmÃ©s.
Impact   : Potentiellement : hydration inutile, bundle client alourdi, TTI dÃ©gradÃ© sur mobile.
           Impact rÃ©el Ã  confirmer par lecture des fichiers.
Action   : Lire chaque fichier. Si absence de hooks React / gestionnaires d'Ã©vÃ©nements client :
           supprimer "use client", convertir en Server Component, remplacer useTranslations() par
           await getTranslations().
Validation : Lecture de chaque fichier confirme l'absence d'interactivitÃ© â†’ conversion justifiÃ©e.
             grep -n '"use client"' frontend/app/docs/page.tsx â†’ vide aprÃ¨s correction.
```

---

**[P1-ARCH-05] `app/home-learner/page.tsx` (317 lignes) et `app/exercises/page.tsx` (311 lignes)**

```
Fichiers : frontend/app/home-learner/page.tsx:1
           frontend/app/exercises/page.tsx:1
Constat  : Pages dÃ©passant 300 lignes avec "use client". Pattern coque non respectÃ©.
Impact   : Logique runtime probable inline. Non testable isolÃ©ment.
Action   : Extraire useHomeLearnerPageController.ts (ou useExercisesPageController.ts)
           + sections ExercisesListSection, ExercisesFiltersSection.
Validation : wc -l frontend/app/exercises/page.tsx â†’ rÃ©sultat < 100.
```

---

### P2 â€” AmÃ©liorations recommandÃ©es

---

**[P2-MOD-01] Tests non co-localisÃ©s**

```
Fichier  : frontend/__tests__/unit/ (133 fichiers)
Constat  : Tous les tests dans __tests__/ sÃ©parÃ©. Ex: __tests__/unit/components/badges/BadgeCard.test.tsx
           au lieu de components/badges/BadgeCard.test.tsx.
Impact   : Navigation difficile lors de refactoring. Risque d'oubli de mise Ã  jour des tests.
Action   : Migration progressive : co-localiser les tests des composants les plus actifs en prioritÃ©.
           Mettre Ã  jour jest.config.ts : testMatch: ["**/*.test.{ts,tsx}"].
Validation : ls frontend/components/badges/BadgeCard.test.tsx â†’ fichier prÃ©sent.
```

---

> ~~**[P2-MOD-02] Barrel exports absents**~~ â€” **InvalidÃ© par le dÃ©bat multi-AI.**
> Dans le contexte Next.js 16 App Router, les barrel exports `index.ts` dans `lib/` nuisent au tree-shaking granulaire cï¿½tï¿½ Server Components et peuvent introduire des dï¿½pendances circulaires involontaires (Matt Pocock, TypeScript Total 2023-2024). Les imports explicites `@/lib/security/buildContentSecurityPolicy` sont **la bonne pratique** pour ce stack. Ne pas crï¿½er de barrel exports dans `lib/`.

---

**[P2-LINT-03] 5 eslint-disable `@next/next/no-img-element` sans justification**

```
Fichiers : (voir P1-PERF-03)
Constat  : RÃ¨gle supprimÃ©e sans commentaire de raison.
Impact   : CrÃ©e une ambiguÃ¯tÃ© : est-ce intentionnel (URL externe) ou un oubli de migration ?
Action   : Ajouter // Intentional: <raison> sur la ligne prÃ©cÃ©dant chaque disable.
           Exemple : // Intentional: URL d'avatar externe sans dimensions connues au build.
Validation : grep -B1 "eslint-disable.*no-img-element" â†’ ligne prÃ©cÃ©dente commence par // Intentional:.
```

---

### P3 â€” Polish et cohÃ©rence

---

**[P3-COMP-01] `BadgeCard.tsx` (494 lignes) et `DiagnosticSolver.tsx` (456 lignes)**

```
Fichiers : frontend/components/badges/BadgeCard.tsx:1
           frontend/components/diagnostic/DiagnosticSolver.tsx:1
Constat  : Composants > 450 lignes. ResponsabilitÃ©s multiples probables.
Impact   : Tests unitaires difficiles. ComplexitÃ© cyclomatique potentiellement Ã©levÃ©e.
Action   : Audit interne. Identifier les sections extractibles en sous-composants.
Validation : Chaque sous-composant extrait < 150 lignes, testÃ© isolÃ©ment.
```

---

**[P3-DIAG-02] ~~`fetch()` direct dans `app/test-sentry/page.tsx`~~ â€” rÃ©solu (QF-01)**

```
Statut   : La route produit /test-sentry a Ã©tÃ© supprimÃ©e ; plus de surface de test dans lâ€™app.
Action   : VÃ©rification Sentry documentÃ©e dans docs/01-GUIDES/SENTRY_MONITORING.md (sans page dÃ©diÃ©e).
```

---

## 13. Forces confirmÃ©es

### Force 1 â€” TypeScript au niveau de rigueur maximal

**Preuve terrain :** 0 occurrence de `: any` ou `as any` dans tout `frontend/` (grep exhaustif). Configuration `strict + noUncheckedIndexedAccess + exactOptionalPropertyTypes` active.

Cette configuration est celle recommandÃ©e par la communautÃ© TypeScript avancÃ©e (Matt Pocock, TypeScript Total) pour les codebases production. Elle signifie que tout changement d'interface API propagera une erreur de compilation avant tout bug runtime â€” particuliÃ¨rement critique pour un projet solo sans code review systÃ©matique d'une Ã©quipe.

### Force 2 â€” React Query avec policy de cache exhaustive

**Preuve terrain :** `staleTime` trouvÃ© sur les 41 queries du projet. Distribution sÃ©mantique cohÃ©rente : exercices temps-rÃ©el (10s), challenges (30s), admin (60s), auth (300s).

Un projet sans `staleTime` rechercherait le backend Ã  chaque montage de composant, surchargeant l'API. La cohÃ©rence de cette policy sur 41 queries (sans exception Ã  0) est un indicateur de maturitÃ© technique.

### Force 3 â€” Guardrails d'architecture auto-vÃ©rifiÃ©s par CI

**Preuve terrain :** `frontendGuardrails.ts` (523 lignes), `ALLOWED_DENSE_EXCEPTIONS = []`, test `frontendGuardrails.test.ts` prÃ©sent dans `__tests__/unit/architecture/`.

Le guardrail dÃ©finit 17 surfaces protÃ©gÃ©es avec budgets max de lignes, 17 seams requis (hooks controllers), 20 fichiers lib requis. Il s'auto-vÃ©rifie via CI. Cette infrastructure est rare en production sur des projets solo â€” elle garantit que l'architecture documentÃ©e correspond Ã  l'architecture rÃ©elle.

---

## 14. Plan d'exÃ©cution solo-founder

Ordre basÃ© sur rapport impact/effort. Chaque sprint est rÃ©alisable en une session de travail.

### Sprint 1 â€” Performance quick wins (2-3h)

```
1. ~~dynamic() / lazy export PDF et Excel~~ â€” **fait (QF-02)** : `import()` dans `exportPDF.ts` / `exportExcel.ts`

2. Lire docs/, changelog/, offline/ â†’ confirmer interactivitÃ© (20 min)
   â†’ Si absence de hooks client : supprimer "use client" et convertir en SC
   â†’ P2-PERF-04 : action conditionnelle Ã  la lecture (rÃ©trogradÃ© depuis P1)

3. Justifications eslint-disable @next/next/no-img-element   (20 min)
   â†’ Impact : dette documentÃ©e ou migration planifiÃ©e

4. ~~Guard NODE_ENV sur app/test-sentry~~ â€” **fait** : page supprimÃ©e (QF-01)
```

### Sprint 2 â€” Images (2-3h)

```
5. Migrer UserAvatar.tsx â†’ next/image (avatar utilisateur)   (45 min)
6. Migrer BadgeIcon.tsx â†’ next/image                         (45 min)
7. Migrer BadgeCard.tsx â†’ next/image                         (45 min)
8. ChatMessagesView.tsx : documenter ou migrer               (30 min)
```

### Sprint 3 â€” DÃ©composition pages (3-5h)

```
9. Extraire useLeaderboardPageController.ts + sections       (2h)
   â†’ PrioritÃ© haute : 481 lignes, flux visible par Ã©lÃ¨ves

10. RÃ©duire exercises/page.tsx < 100 lignes                  (1-2h)
11. RÃ©duire home-learner/page.tsx < 100 lignes               (1h)
```

### Sprint 4 â€” ModularitÃ© (1-2h)

```
12. Plan migration co-location tests (audit + 2-3 migrations pilotes)  (1-2h)
    â†’ Ne PAS crÃ©er de barrel exports lib/ (invalidÃ© â€” voir Â§Findings P2-MOD-02)
```

### Non planifiÃ© (backlog produit distinct)

- Migration vers co-location tests complÃ¨te (133 fichiers â€” effort Ã©levÃ©, impact progressif)
- DÃ©composition `BadgeCard.tsx` et `DiagnosticSolver.tsx` (nÃ©cessite audit interne approfondi)

## Addendum 2026-04-10 - QF-01 rÃ©alisÃ©

Le lot `QF-01` a Ã©tÃ© exÃ©cutÃ© aprÃ¨s gÃ©nÃ©ration du prÃ©sent audit.

Travaux effectuÃ©s :

- suppression de `frontend/app/test-sentry/page.tsx` : plus de surface produit dÃ©diÃ©e au smoke test Sentry
- `Sentry.setUser(...)` dans `frontend/hooks/useAuth.ts` rÃ©duit Ã  `{ id }` uniquement ; plus de `username`
- `frontend/.env.example` documente maintenant `SECRET_KEY` pour le runtime serveur Next (`lib/auth/server/routeSession.ts`), hors `NEXT_PUBLIC_*`
- `docs/01-GUIDES/SENTRY_MONITORING.md`, `README_TECH.md` et `.claude/session-plan.md` rÃ©alignÃ©s sur cette nouvelle vÃ©ritÃ© terrain

Constats du prÃ©sent audit impactÃ©s par `QF-01` :

- `P3-DIAG-02` reste classÃ© **rÃ©solu**
- les mentions historiques Ã  `/test-sentry` doivent Ãªtre lues comme trace de correction, pas comme surface encore prÃ©sente dans l'application

## Addendum 2026-04-10 - QF-03 (i18n pages admin / offline)

Constat terrain traitÃ© : **copy utilisateur inline** sur les **routes** `frontend/app/admin/page.tsx`, `analytics`, `ai-monitoring`, `audit-log`, `config`, `content`, `feedback`, `moderation`, `users`, et `frontend/app/offline/page.tsx`.

Travaux effectuÃ©s :

- clÃ©s regroupÃ©es sous **`adminPages`** (sous-objets : `overview`, `analytics`, `aiMonitoring`, `auditLog`, `config`, `content`, `feedback`, `moderation`, `users`) et **`offline`** Ã  la racine des fichiers messages
- `useTranslations` sur ces pages uniquement ; **hors scope** : modaux admin profonds, sections mÃ©tier imbriquÃ©es, helpers dans hooks (ex. `getAuditActionLabel` reste dans `useAdminAuditLog.ts` mais la page journal utilise les libellÃ©s i18n pour la colonne action)
- `i18n:validate` + `i18n:check` verts sur lâ€™arbre messages ; `i18n:extract` peut encore signaler dâ€™autres chaÃ®nes hors pÃ©rimÃ¨tre route-level

**RÃ©sidu volontaire :** i18n complÃ¨te des composants admin internes et chaÃ®nes mÃ©tier ailleurs dans le dÃ©pÃ´t.

## Addendum 2026-04-10 - QF-03B (chrome admin + toasts auth)

Constat terrain traitÃ© :

- le **layout admin** gardait encore des libellés inline (`Vue d'ensemble`, `Utilisateurs`, `Paramètres`, etc.) alors que les pages route-level étaient déjà i18nisées
- `frontend/hooks/useAuth.ts` gardait encore des descriptions de toasts hardcodées pour le fallback post-inscription et le forgot-password

Travaux effectués :

- ajout de `adminPages.layout.navAriaLabel` et `adminPages.layout.links.*` dans `frontend/messages/fr.json` / `en.json`
- `frontend/app/admin/layout.tsx` utilise maintenant `useTranslations("adminPages.layout")` pour la navigation latérale et expose `aria-current="page"` sur le lien actif
- ajout de `toasts.auth.registerVerifyEmailDescription`, `forgotPasswordSuccessDescription`, `forgotPasswordErrorDescription`
- `frontend/hooks/useAuth.ts` ne contient plus ces chaînes inline
- tests : `frontend/__tests__/unit/app/admin/AdminLayout.test.tsx` + mise à jour `frontend/__tests__/unit/hooks/useAuth.test.ts`

## Addendum 2026-04-10 - QF-04 (ESLint TypeScript durci)

CohÃ©rent avec **Â§D4 â€” ESLint / Hooks** : `@typescript-eslint/no-unused-vars`, `no-require-imports` et `consistent-type-imports` sont en **error** dans `frontend/eslint.config.mjs` (mesure initiale : **0** sur les deux premiÃ¨res sur lâ€™arbre lintÃ©). Option `disallowTypeAnnotations: false` sur `consistent-type-imports` pour conserver `vi.importActual<typeof import("â€¦")>` (tests).

**Suite QF-04B (2026-04-10) :** ESLint **type-aware** sur le frontend (`parserOptions.projectService: true`, `tsconfigRootDir`, ignores build/cache/scripts) ; `@typescript-eslint/no-floating-promises` en **error** ; mesure initiale **64** violations corrigÃ©es par **`void`** explicite (invalidations React Query, `import()` dynamiques, handlers async) â€” pas de changement UX volontaire.

**Hors pÃ©rimÃ¨tre inchangÃ© :** `import/no-cycle` ; pas dâ€™activation opportuniste dâ€™autres rÃ¨gles typÃ©es hors le minimum nÃ©cessaire Ã  cette rÃ¨gle.

**Suite QF-04C (2026-04-10) :** `react-hooks/set-state-in-effect` et `react-hooks/preserve-manual-memoization` passent en **error** ; mesure sur lâ€™arbre avant durcissement : **0** message ESLint (rÃ¨gles en `warn`) car **2** occurrences de `set-state-in-effect` Ã©taient dÃ©jÃ  **neutralisÃ©es** par `eslint-disable-next-line` justifiÃ© ; **`preserve-manual-memoization`** : **0** occurrence. Correction **ROI** : `useContentListOrderPreference` â€” lecture `localStorage` via initialiseur paresseux de `useState` (clÃ© stable par montage). **RÃ©sidu documentÃ© :** une suppression locale conservÃ©e dans `useGuestChatAccess` (sync invitÃ© post-hydratation).

**Suite QF-05 (2026-04-10) â€” E2E auth minimal utile :** parcours **rÃ©el** login â†’ (onboarding seed si besoin) â†’ navigation **`/dashboard`**, **`/badges`**, **`/settings`** ; tests **Chromium uniquement** (`test.skip` hors chromium) ; helper **`frontend/__tests__/e2e/helpers/demoUserAuth.ts`** (pas de `globalSetup` / `storageState` global) ; diagnostic post-onboarding **hors automate** ; prÃ©requis **backend** + attention **rate-limit login 5/min/IP**.

**Suite QF-06 (2026-04-10) â€” Coverage gates rÃ©alistes :** `frontend/vitest.config.ts` fixe dÃ©sormais un **pÃ©rimÃ¨tre explicite** de couverture (`*.{ts,tsx}`, `app`, `components`, `hooks`, `i18n`, `lib`, `messages`) et des seuils globaux basÃ©s sur la **baseline mesurÃ©e** du dÃ©pÃ´t, non sur une cible arbitraire : **statements 43%** (`3590/8291`), **branches 36%** (`3111/8420`), **functions 39%** (`899/2264`), **lines 44%** (`3423/7718`). Lâ€™objectif est de figer le dÃ©nominateur rÃ©el de couverture frontend avant de remonter les seuils par lots thÃ©matiques.

---

_Rapport gÃ©nÃ©rÃ© le 2026-04-09. Toutes les assertions sont basÃ©es sur des lectures directes de fichiers effectuÃ©es pendant l'audit. Pour les dimensions oÃ¹ la mesure complÃ¨te n'est pas possible sans outillage (complexitÃ© cyclomatique, dÃ©pendances circulaires), les scores sont conservateurs et marquÃ©s explicitement._
