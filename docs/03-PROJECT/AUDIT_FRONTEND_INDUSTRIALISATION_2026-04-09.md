# Audit Frontend — Industrialisation & Qualité Technique

> **Version :** 2026-04-12 (audit initial 2026-04-09, mis à jour au fil des lots)
> **Stack :** Next.js 16 App Router · TypeScript strict · Tailwind CSS · shadcn/ui · React Query v5
> **Méthode :** lectures directes de fichiers — chaque constat cite `fichier:ligne`
> **Objectif :** atteindre 9.5/10

---

## Légende

Chaque entrée de ce document est typée explicitement pour que Codex puisse agir sans ambiguïté.

| Type               | Signification                                                                        |
| ------------------ | ------------------------------------------------------------------------------------ |
| `[CONSTAT]`        | Fait observé dans le code. Vérité terrain mesurée.                                   |
| `[RECOMMANDATION]` | Action suggérée pour améliorer le score. Codex peut l'implémenter.                   |
| `[DÉCISION]`       | Choix d'implémentation délibéré. Ne **pas** contredire sans nouveau constat terrain. |
| `[RÉSOLU]`         | Point fermé. Ne **pas** réimplémenter.                                               |
| `[NON VÉRIFIÉ]`    | Constat non relu sur master — à vérifier avant d'agir.                               |

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Scores par dimension](#2-scores-par-dimension)
3. [Forces confirmées](#3-forces-confirmées)
4. [Findings actifs — à traiter](#4-findings-actifs--à-traiter)
5. [Findings résolus — référence](#5-findings-résolus--référence)
6. [Décisions délibérées — ne pas contredire](#6-décisions-délibérées--ne-pas-contredire)
7. [Findings backend/sécurité hors périmètre frontend](#7-findings-backendsécurité-hors-périmètre-frontend)
8. [Plan d'exécution solo-founder vers 9.5/10](#8-plan-dexécution-solo-founder-vers-9510)
9. [Méthodologie](#9-méthodologie)

---

## 1. Résumé exécutif

| Indicateur                                      | Valeur                         |
| ----------------------------------------------- | ------------------------------ |
| Score global pondéré (audit initial 2026-04-09) | **7.05 / 10**                  |
| Score estimé après lots exécutés (2026-04-11)   | **~7.8 / 10**                  |
| Findings P0 ouverts                             | **0**                          |
| Findings P1 ouverts                             | **0**                          |
| Findings P2 ouverts                             | **3** (ACTIF-03/04/06)         |
| Findings P3 ouverts                             | **2** (ACTIF-05 backlog + ACTIF-07 DRY) |
| Queries React Query avec staleTime              | **41/41** (100 %)              |
| Occurrences `: any` ou `as any`                 | **0**                          |
| TODO/FIXME/HACK non ticketés                    | **0**                          |

**Verdict :** le frontend est industriellement mature sur TypeScript, cache React Query et guardrails CI. Les risques résiduels sont la co-location progressive des tests (D5), la remontée mesurée de la couverture et des seuils Vitest (D8). Le finding **ACTIF-02** (images dynamiques D7) est **clos** : hybrides `next/image` / `<img>` pour avatar et badges ; **exception documentée** `<img>` pour le chat (**`ChatMessagesView`**).

> **Hors périmètre de cet audit :** sécurité HTTP au-delà de la CSP, surface XSS détaillée, backend Python, DevOps. Ces points sont traités dans la section §7 et dans l'audit complet multi-stack séparé.

---

## 2. Scores par dimension

| Dimension                | Score | Poids     | Score pondéré | P1 ouverts |
| ------------------------ | ----- | --------- | ------------- | ---------- |
| D1 Industrialisation     | 8/10  | 15 %      | 1.20          | 0          |
| D2 DRY / Factorisation   | 7/10  | 10 %      | 0.70          | 0          |
| D3 TypeScript Strict     | 9/10  | 15 %      | 1.35          | 0          |
| D4 ESLint / Hooks        | 8/10  | 10 %      | 0.80          | 0          |
| D5 Modularité            | 6/10  | 15 %      | 0.90          | 0          |
| D6 Maintenabilité        | 7/10  | 15 %      | 1.05          | 0          |
| D7 Performance           | 6/10  | 10 %      | 0.60          | 0          |
| D8 Réplicabilité / Tests | 8/10  | 10 %      | 0.80          | 0          |
| **TOTAL**                |       | **100 %** | **~7.4/10**   | **0**      |

> Les scores D1, D4, D7, D8 reflètent les lots exécutés depuis l'audit initial (pages décomposées, ESLint durci, lazy loading PDF/Excel).

---

## 3. Forces confirmées

### F1 — TypeScript au niveau de rigueur maximal

`[CONSTAT]` Grep exhaustif sur `frontend/` (hors `node_modules/`, `.next/`, `coverage/`) :

- `: any` → **0 résultat**
- `as any` → **0 résultat**

`tsconfig.json` active `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` — configuration recommandée par Matt Pocock (TypeScript Total, 2024) pour les codebases production.

Conséquence : tout changement d'interface API se propage par erreur de compilation avant tout bug runtime.

### F2 — React Query avec policy de cache exhaustive

`[CONSTAT]` `staleTime` présent sur les 41 queries du projet (grep dans `hooks/` → 41 occurrences).

| Domaine    | staleTime          | Justification             |
| ---------- | ------------------ | ------------------------- |
| Exercices  | 10 000 ms          | Résultats temps réel      |
| Challenges | 30 000 ms          | Moins fréquents           |
| Admin      | 60 000 ms          | Usage interne             |
| Badges     | 60 000–300 000 ms  | Quasi-statiques           |
| Auth       | 300 000 ms (5 min) | Token validé côté serveur |

Aucune query à staleTime = 0 : zéro rechargement systématique non intentionnel.

### F3 — Guardrails d'architecture auto-vérifiés par CI

`[CONSTAT]` `frontendGuardrails.ts` (523 lignes) :

- `ALLOWED_DENSE_EXCEPTIONS = []` — zéro exception tolérée
- 17 surfaces protégées avec budgets max de lignes
- 17 seams requis (hooks controllers)
- 20 fichiers lib requis
- `frontendGuardrails.test.ts` présent dans `__tests__/unit/architecture/` — toute violation casse le pipeline avant merge

### F4 — Controllers séparés et testables isolément

`[CONSTAT]` 8 controllers dans `frontend/hooks/` :

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

Zéro `fetch()` direct dans les controllers. Le réseau est délégué aux hooks React Query passés en paramètre (pattern Command/Query Separation). Exemple dans `useChallengeSolverController.ts` :

```typescript
export function useChallengeSolverController({
  submitAnswer, // injecté — testable sans mock réseau
  getHint,
  setHints,
}: UseChallengeSolverControllerArgs);
```

### F5 — ESLint : toutes les suppressions justifiées

`[CONSTAT]` 8 suppressions `exhaustive-deps` / `set-state-in-effect` lues pendant l'audit — toutes avec commentaire adjacent :

| Fichier                                                       | Règle               | Justification lue                                         |
| ------------------------------------------------------------- | ------------------- | --------------------------------------------------------- |
| `hooks/useSettingsPageController.ts:181`                      | exhaustive-deps     | mount-only load; useSettings callbacks are unstable       |
| `hooks/chat/useGuestChatAccess.ts:40`                         | set-state-in-effect | intentional post-hydration sync from sessionStorage       |
| `hooks/useChallengeSolverController.ts:141`                   | exhaustive-deps     | Reset only on visible challenge identity change           |
| `hooks/useContentListOrderPreference.ts:24`                   | set-state-in-effect | intentional post-hydration sync                           |
| `hooks/useExerciseSolverController.ts:253`                    | exhaustive-deps     | reset seulement si l'exercice courant change              |
| `components/challenges/visualizations/PuzzleRenderer.tsx:162` | exhaustive-deps     | onOrderChange via ref ; éviter reset sur identité tableau |
| `components/challenges/visualizations/PuzzleRenderer.tsx:201` | exhaustive-deps     | intentionnel au montage seulement                         |
| `components/ui/sonner.tsx:38`                                 | exhaustive-deps     | Register once; MutationObserver handles theme changes     |

---

## 4. Findings actifs — à traiter

> **ORDRE D'EXÉCUTION IMPOSÉ — ne pas déroger.**
> Les findings sont listés du plus prioritaire au moins prioritaire. ACTIF-05 est intentionnellement en dernier : c'est un backlog optionnel. Si Codex cherche quoi faire, il commence par **ACTIF-03**.

| Finding | Priorité | Effort | Premier geste concret |
|---------|----------|--------|-----------------------|
| ~~ACTIF-01~~ | ~~P2~~ — FERMÉ | — | Vérifié terrain 2026-04-11 (`ACTIF-01-TRUTH-01`) : 1 page convertie SC, 3 restées client avec preuve code |
| ~~ACTIF-02~~ | ~~P2~~ — **FERMÉ** | — | D7 images dynamiques : `UserAvatar` + `BadgeIcon` hybrides ; `ChatMessagesView` **exception `<img>`** (`ACTIF-02-CHATMESSAGES-01`, 2026-04-12) |
| ACTIF-03 | P2 — EN COURS | 1–2h par lot | Poursuivre la co-localisation par lots (`useAuth` + sécurité **`lib/security/*.test.ts`** + hooks **`useIrtScores`** / **`useAIExerciseGenerator`** / **`useSettingsPageController`** / **`useBadgesPageController`** / **`useDashboardPageController`** / **`useContentListPageController`** / **`useChallengeSolverController`** / **`useExerciseSolverController`** validés **`ACTIF-03-USEAUTH-COLOCATE-01`** / **`ACTIF-03-BUILDCSP-COLOCATE-01`** / **`ACTIF-03-MIDDLEWARECSP-COLOCATE-01`** / **`ACTIF-03-USEIRT-COLOCATE-01`** / **`ACTIF-03-USEAI-COLOCATE-01`** / **`ACTIF-03-USESETTINGS-COLOCATE-01`** / **`ACTIF-03-USEBADGES-COLOCATE-01`** / **`ACTIF-03-DASHBOARD-COLOCATE-01`** / **`ACTIF-03-CONTENTLIST-COLOCATE-01`** / **`ACTIF-03-CHALLENGESOLVER-COLOCATE-01`** / **`ACTIF-03-EXERCISESOLVER-COLOCATE-01`**, 2026-04-12) |
| ACTIF-04 | P2 — EN COURS | 30 min config | Seuils remontés **`ACTIF-04-COVERAGE-01`** (2026-04-12) ; poursuivre par nouveaux tests puis **nouvelle mesure** avant tout bump suivant |
| ACTIF-06 | P2 — EN COURS | 2–3h/page | Extraire `useAdminAiMonitoringPageController` (**users** : lot **`ACTIF-06-ADMIN-USERS-01`**, 2026-04-12) |
| ACTIF-07 | P3 — NOUVEAU | 1h | Créer `_colorMap.ts` partagé entre renderers |
| ACTIF-05 | P3 — BACKLOG | 2–4h | **Ne pas toucher sans raison fonctionnelle** |

---

### ~~[ACTIF-01]~~ Pages Server Components — FERMÉ (vérité terrain)

`[RÉSOLU]` Lot **`ACTIF-01-TRUTH-01`** (2026-04-11) — lecture code des quatre routes ; décision explicite page par page :

| Page | Verdict | Raison factuelle (code) |
|------|---------|-------------------------|
| `frontend/app/docs/page.tsx` | **Convertie** (Server Component) | Aucun handler ni API navigateur requise ; `getTranslations` côté serveur ; animation d’en-tête portée par utilitaires Tailwind **`motion-safe:*`** (équivalent à l’ancien `useAccessibleAnimation` sur le hero uniquement ; bloc FAQ inchangé). |
| `frontend/app/changelog/page.tsx` | **Reste client** | `framer-motion` (`motion.*`) + `useAccessibleAnimation` (variants / transitions). |
| `frontend/app/offline/page.tsx` | **Reste client** | `useRouter`, `navigator.onLine`, `window.addEventListener("online", …)`, `router.refresh()`. |
| `frontend/app/contact/page.tsx` | **Reste client** | `useState` sur les champs + `onSubmit` / `onChange` + `window.location.href` (mailto). |

`[DÉCISION]` Ne pas rouvrir sans nouveau constat. Trois pages conservent `"use client"` pour des dépendances runtime client réelles ; une page a été alignée sur le même modèle que `about` / `privacy` (SC + layout client enfant).

---

### ~~[ACTIF-02]~~ Composants `<img>` dynamiques (D7) — **FERMÉ**

**Priorité :** ~~P2~~ | **Dimension :** D7 | **`[RÉSOLU]`** 2026-04-12

Synthèse des trois sous-lots :

| Sous-lot | Fichier / périmètre | Verdict |
|----------|---------------------|---------|
| **ACTIF-02-USERAVATAR-01** | `UserAvatar.tsx` | Hybride **`next/image`** / **`<img>`** via **`resolveNextImageRemoteDelivery`** |
| **ACTIF-02-BADGEICON-01** | `BadgeIcon.tsx` | Idem + fallback erreur en **state React** |
| **ACTIF-02-CHATMESSAGES-01** | `ChatMessagesView.tsx` | **Exception délibérée** : **`<img>` natif** conservé — `message.imageUrl` vient du SSE sans contrat de dimensions ni d’hôte (**HTTP(S)** arbitraire, **`blob:`**, **`data:`**) ; le layout **`max-h-64 w-full object-cover`** s’appuie sur les dimensions intrinsèques — **`next/image`** sans largeur/hauteur fictives ou **`fill`** re-dimensionnant le conteneur aurait dévié du rendu validé produit. Commentaire **`eslint-disable`** renforcé in-file ; tests **`__tests__/unit/components/chat/ChatMessagesView.test.tsx`** (placeholder + loader, image seule, texte + image, HTTPS hors allowlist, `blob:` / `data:`, KaTeX, `role="alert"`, parité **embedded** / **drawer**).

`[VALIDATION]`

```bash
grep -r "eslint-disable.*no-img-element" frontend/components/ --include="*.tsx"
# chaque occurrence restante doit être couverte par un commentaire Intentional / exception documentée (avatar, badge hors-liste, chat).
```

---

### [ACTIF-03] Tests non co-localisés

**Priorité :** P2 | **Dimension :** D5 Modularité | **Effort :** 1–2h pour les migrations pilotes

`[CONSTAT]` La majorité des tests reste sous `frontend/__tests__/unit/` (structure historique). L’outillage Vitest découvre déjà les `*.test.{ts,tsx}` hors `__tests__/` (préco `lib/auth/server/validateTokenBackendHeaders.test.ts`).

**Avancement 2026-04-11 (lot `TEST-COLOCATE-PILOT-01`, pilote ACTIF-03)** : 4 fichiers co-localisés sans changement de logique ni de `vitest.config.ts` :
- `frontend/components/badges/BadgeCard.test.tsx`
- `frontend/components/diagnostic/DiagnosticSolver.test.tsx`
- `frontend/hooks/useDiagnostic.test.ts`
- `frontend/hooks/useSubmitAnswer.test.ts`

**Avancement 2026-04-12 (lot `ACTIF-03-USEAUTH-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useAuth.test.ts`** co-localisé auprès de **`useAuth.ts`** (même discipline : pas de changement de logique de test ni de `vitest.config.ts`).

**Avancement 2026-04-12 (lot `ACTIF-03-BUILDCSP-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/lib/security/buildContentSecurityPolicy.test.ts`** co-localisé auprès de **`buildContentSecurityPolicy.ts`** (aligné sur le précédent **`lib/auth/server/validateTokenBackendHeaders.test.ts`**). Le déplacement retire le test du chemin historique **`__tests__/unit/lib/...`**, fragile au tracking Git (conflit potentiel avec des règles **`.gitignore`** sur `lib/` imbriqués sous `__tests__/unit/`) au profit d’un chemin **`frontend/lib/security/*.test.ts`** durablement versionné.

**Avancement 2026-04-12 (lot `ACTIF-03-MIDDLEWARECSP-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/lib/security/middlewareCsp.test.ts`** co-localisé auprès de **`middlewareCsp.ts`**. La vague tests sécurité sous **`frontend/lib/security/*.test.ts`** est désormais cohérente (**`buildContentSecurityPolicy.test.ts`** + **`middlewareCsp.test.ts`**) sans changer **`vitest.config.ts`**.

**Avancement 2026-04-12 (lot `ACTIF-03-USEIRT-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useIrtScores.test.ts`** co-localisé auprès de **`useIrtScores.ts`**. La série hooks co-localisés se poursuit : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`** (même discipline : pas de changement de logique de test ni de **`vitest.config.ts`**).

**Avancement 2026-04-12 (lot `ACTIF-03-USEAI-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useAIExerciseGenerator.test.ts`** co-localisé auprès de **`useAIExerciseGenerator.ts`**. Série hooks co-localisés : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**.

**Avancement 2026-04-12 (lot `ACTIF-03-USESETTINGS-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useSettingsPageController.test.ts`** co-localisé auprès de **`useSettingsPageController.ts`**. Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**.

**Avancement 2026-04-12 (lot `ACTIF-03-USEBADGES-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useBadgesPageController.test.ts`** co-localisé auprès de **`useBadgesPageController.ts`** (FFI-L12). Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**, **`useBadgesPageController`**.

**Avancement 2026-04-12 (lot `ACTIF-03-DASHBOARD-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useDashboardPageController.test.ts`** co-localisé auprès de **`useDashboardPageController.ts`**. Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**, **`useBadgesPageController`**, **`useDashboardPageController`**.

**Avancement 2026-04-12 (lot `ACTIF-03-CONTENTLIST-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useContentListPageController.test.tsx`** co-localisé auprès de **`useContentListPageController.ts`**. Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**, **`useBadgesPageController`**, **`useDashboardPageController`**, **`useContentListPageController`**.

**Avancement 2026-04-12 (lot `ACTIF-03-CHALLENGESOLVER-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useChallengeSolverController.test.tsx`** co-localisé auprès de **`useChallengeSolverController.ts`**. Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**, **`useBadgesPageController`**, **`useDashboardPageController`**, **`useContentListPageController`**, **`useChallengeSolverController`**.

**Avancement 2026-04-12 (lot `ACTIF-03-EXERCISESOLVER-COLOCATE-01`, pilote ACTIF-03)** : **`frontend/hooks/useExerciseSolverController.test.ts`** co-localisé auprès de **`useExerciseSolverController.ts`**. Série étendue : **`useAuth`**, **`useDiagnostic`**, **`useSubmitAnswer`**, **`useIrtScores`**, **`useAIExerciseGenerator`**, **`useSettingsPageController`**, **`useBadgesPageController`**, **`useDashboardPageController`**, **`useContentListPageController`**, **`useChallengeSolverController`**, **`useExerciseSolverController`**.

La migration globale des ~130 autres fichiers **n’est pas** revendiquée ; **ACTIF-03** reste ouvert.

`[RECOMMANDATION]` Poursuivre par petits lots nommés (même discipline : pas de `vitest.config.ts` ni vague massive sans validation).

`[DÉCISION]` Ne pas migrer les fichiers restants « au passage » dans un lot fonctionnel non dédié.

`[VALIDATION]`

```bash
ls frontend/components/badges/BadgeCard.test.tsx
npx vitest run components/badges/BadgeCard.test.tsx
```

---

### [ACTIF-04] Coverage vitest — seuils à remonter progressivement

**Priorité :** P2 | **Dimension :** D8 Réplicabilité | **Effort :** 3–4 semaines par incrément de 5 points

`[CONSTAT]` Historique — baseline CI (commit `ae11043`) : statements 39.75 %, branches 34.04 %, functions 37.85 %, lines 40.66 % ; seuils conservateurs **39 / 33 / 37 / 40** (1 point sous le réel).

**Avancement 2026-04-12 (lot `ACTIF-04-COVERAGE-01`, corrigé après échec CI)** : la mesure **autoritative** est désormais celle du job frontend GitHub Actions (**`ubuntu-latest`**, Node **20**, commande **`npx vitest --coverage --reporter=junit --outputFile=./junit.xml --run`**), pas la machine locale Windows. Agrégat **All files** observé en CI :

- statements : **44.57 %**
- branches : **37.22 %**
- functions : **41.47 %**
- lines : **45.68 %**

Des reproductions locales Windows/Node 20 montent plus haut (~**47.9 / 39.93 / 43.3 / 49.14**), mais elles ne servent plus de baseline tant qu’elles divergent de la CI.

Seuils dans `vitest.config.ts` recalibrés à **43 / 36 / 40 / 44** (règle **`floor(mesure CI %) − 1`** par axe, tout en restant au-dessus des anciens **39 / 33 / 37 / 40**). **ACTIF-04** reste ouvert : l’horizon « couverture large » (ex. 55 %) n’est pas atteint ; les prochains bumps exigent une **nouvelle mesure** après lots de tests, idéalement sur l’environnement CI, pas une hausse « par principe ».

**Ratio hooks recalculé terrain (2026-04-11)** : 22 hooks avec test / 56 total = **34 hooks sans test (61 %)**. Historique audit initial : 71 % (52 hooks, avant les lots de tests ci-dessous). Avancements : (1) `TEST-DIAGNOSTIC-HOOK-01` — `useDiagnostic` ; (2) `TEST-SUBMIT-ANSWER-01` — `useSubmitAnswer` ; (3) `TEST-IRT-SCORES-01` — `useIrtScores` ; (4) `TEST-AI-GENERATOR-01` — `useAIExerciseGenerator`. Hooks sans test prioritaires : `useAdminUsers`, `useBadges`, `useChallenges`, `useExercises`, `useSettings`, `useLeaderboard`. (`useAuth` : **`hooks/useAuth.test.ts`** — **`ACTIF-03-USEAUTH-COLOCATE-01`** ; `useIrtScores` : **`hooks/useIrtScores.test.ts`** — **`ACTIF-03-USEIRT-COLOCATE-01`** ; `useAIExerciseGenerator` : **`hooks/useAIExerciseGenerator.test.ts`** — **`ACTIF-03-USEAI-COLOCATE-01`** ; `useSettingsPageController` : **`hooks/useSettingsPageController.test.ts`** — **`ACTIF-03-USESETTINGS-COLOCATE-01`** ; `useBadgesPageController` : **`hooks/useBadgesPageController.test.ts`** — **`ACTIF-03-USEBADGES-COLOCATE-01`** ; `useDashboardPageController` : **`hooks/useDashboardPageController.test.ts`** — **`ACTIF-03-DASHBOARD-COLOCATE-01`** ; `useContentListPageController` : **`hooks/useContentListPageController.test.tsx`** — **`ACTIF-03-CONTENTLIST-COLOCATE-01`** ; `useChallengeSolverController` : **`hooks/useChallengeSolverController.test.tsx`** — **`ACTIF-03-CHALLENGESOLVER-COLOCATE-01`** ; `useExerciseSolverController` : **`hooks/useExerciseSolverController.test.ts`** — **`ACTIF-03-EXERCISESOLVER-COLOCATE-01`**.)

`[RECOMMANDATION]` Écrire les tests des hooks critiques en priorité, puis remonter les seuils **après mesure**. Budget réel : **30 min de config + 3–4 semaines d'écriture de tests** par incrément de couverture significatif.

`[DÉCISION]` Ne pas monter les seuils sans mesure réelle défendable. Un seuil artificiellement haut qui casse CI ne sert à rien.

`[VALIDATION]`

```bash
cd frontend && npx vitest run --coverage
# objectif : statements ≥ seuil défini dans vitest.config.ts
```

---

### [ACTIF-06] Pages admin volumineuses sans controller — violation guardrail

**Priorité :** P2 | **Dimension :** D1 Industrialisation | **Effort :** 2–3h chacune

`[CONSTAT]` ~~Deux~~ **Une** page admin restante avec logique métier inline dense sans controller dédié ; la page **users** a été traitée (lot **`ACTIF-06-ADMIN-USERS-01`**, 2026-04-12).

| Fichier | Lignes | État |
|---------|--------|------|
| `app/admin/users/page.tsx` | ~385 (vue) | Logique portée par **`hooks/useAdminUsersPageController.ts`** (~212 L) — filtres, pagination, modales rôle/suppression, toasts, wiring **`useAdminUsers`** inchangé côté contrat. |
| `app/admin/ai-monitoring/page.tsx` | 572 | state `days` + `formatWorkloadLabel` + `daysOptions` useMemo + JSX toolbar inline à lignes 39–102 — **à extraire** (`useAdminAiMonitoringPageController` ou équivalent). |

Le projet dispose de `useAdminContentPageController.ts` ; **`useAdminUsersPageController`** suit la même discipline que `useDashboardPageController`, `useBadgesPageController`.

**Avancement 2026-04-12** : tests **`hooks/useAdminUsersPageController.test.tsx`** (params **`useAdminUsers`**, reset page sur recherche, filtres rôle / statut).

`[RECOMMANDATION]` Extraire **`useAdminAiMonitoringPageController.ts`** pour **ai-monitoring**. Les pages restent des coques qui consomment le controller.

`[VALIDATION]`

```bash
grep -c "useState" frontend/app/admin/users/page.tsx
# objectif : 0 sur la page (état dans le controller)
npx vitest run hooks/useAdminUsersPageController.test.tsx
```

---

### [ACTIF-07] Duplication `colorMap` entre renderers visuels

**Priorité :** P3 | **Dimension :** D2 DRY | **Effort :** 1h

`[CONSTAT]` Deux maps couleur quasi-identiques (clés FR/EN → hex) co-existent dans des fichiers séparés sans module partagé :

| Fichier | Symbole | Lignes |
|---------|---------|--------|
| `components/challenges/visualizations/VisualRenderer.tsx:27` | `colorMap` dans `parseShapeWithColor()` | ~20 entrées |
| `components/challenges/visualizations/VisualRenderer.tsx:95` | deuxième `colorMap` dans `resolveColor()` | ~15 entrées |
| `components/challenges/visualizations/ProbabilityRenderer.tsx:15` | `COLOR_MAP` constante | ~20 entrées (+ `marron`) |

Risque : une couleur ajoutée dans un fichier ne se propage pas automatiquement aux autres. La divergence est silencieuse.

`[RECOMMANDATION]` Créer `components/challenges/visualizations/_colorMap.ts` avec la map canonique. Les trois usages importent cette constante. Pas de changement de comportement, juste élimination de la copie.

`[DÉCISION]` Ne pas fusionner tant qu'une feature n'impose pas de toucher plusieurs renderers simultanément — le risque de divergence est faible à court terme.

---

### [ACTIF-05] Controllers et utilitaires volumineux — BACKLOG OPTIONNEL

> ⛔ **NE PAS COMMENCER CE FINDING EN PREMIER.**
> ACTIF-06 et les autres findings actifs sont prioritaires. Ce finding est listé pour traçabilité, pas comme tâche immédiate. La `[DÉCISION]` ci-dessous l'interdit explicitement.

**Priorité :** P3 — BACKLOG | **Dimension :** D6 Maintenabilité | **Effort :** 2–4h chacun

`[CONSTAT]` Taille mesurée sur `master` (information seulement, pas d'action requise) :

| Fichier | Lignes | Note |
|---------|--------|------|
| `hooks/useProfilePageController.ts` | 463 | Aucun bug connu |
| `hooks/useExerciseSolverController.ts` | 391 | Aucun bug connu |
| `lib/utils/exportPDF.ts` | 384 | Lazy loading déjà fait (P1-PERF-02 résolu) |
| `lib/utils/exportExcel.ts` | 391 | Idem |

`[DÉCISION]` **Ne pas toucher ces fichiers sans raison fonctionnelle.** Ils fonctionnent, sont couverts par des tests, et leur découpage ne génère pas de gain mesurable à court terme. Ouvrir uniquement si un lot fonctionnel impose de modifier l'un d'eux.

---

## 5. Findings résolus — référence

Ces points sont **fermés**. Ne pas les réimplémenter. Ils sont listés ici pour traçabilité.

| ID             | Description                                                                                         | Lot                   | Date               |
| -------------- | --------------------------------------------------------------------------------------------------- | --------------------- | ------------------ |
| P3-DIAG-02     | `fetch()` direct dans `app/test-sentry/page.tsx` — page supprimée                                   | QF-01                 | 2026-04-10         |
| P1-PERF-02     | Exports PDF/Excel sans lazy loading                                                                 | QF-02                 | 2026-04-10         |
| P2-LINT-03     | `eslint-disable @next/next/no-img-element` sans justification                                       | AUDIT-QUICKWINS-01    | 2026-04-10         |
| BUG-DOCKER     | `.dockerignore:147` excluait `migrations/versions/*`                                                | AUDIT-QUICKWINS-01    | 2026-04-10         |
| F1-SECU        | `X-XSS-Protection: "1"` déprécié → remplacé par `"0"`                                               | AUDIT-QUICKWINS-01    | 2026-04-10         |
| PERF-IMG-LOCAL | `BadgeCard.tsx`, `BadgesProgressTabsSection.tsx` → `next/image` pour SVG locaux                     | PERF-IMG-LOCAL-01     | 2026-04-10         |
| M5-PII         | `username`/`email` en clair dans les logs auth — remplacés par `user_id` + alias HMAC               | SEC-PII-LOGS-01       | 2026-04-10         |
| i18n-admin     | Copy inline sur routes admin + layout admin + toasts auth                                           | QF-03, QF-03B         | 2026-04-10         |
| ESLint-strict  | `no-unused-vars`, `consistent-type-imports`, `no-floating-promises`, `set-state-in-effect` en error | QF-04, QF-04B, QF-04C | 2026-04-10         |
| E2E-auth       | Parcours login → dashboard/badges/settings ajouté                                                   | QF-05                 | 2026-04-10         |
| Coverage-gate  | Seuils vitest : historique **QF-06** (43/36/39/44 puis 39/33/37/40 %) puis recalibrage **`ACTIF-04-COVERAGE-01`** → **43/36/40/44** depuis la baseline CI GitHub Actions 2026-04-12 (**44.57 / 37.22 / 41.47 / 45.68 %**, règle **floor−1**) | QF-06 + ACTIF-04-COVERAGE-01 | 2026-04-12         |
| H1-diagnose    | `diagnose=True` en prod → `diagnose=_uncaught_diagnose`                                             | Déjà en place         | vérifié 2026-04-10 |
| H2-HSTS        | HSTS absent → `server/middleware.py:108-109` conditionnel prod                                      | Déjà en place         | vérifié 2026-04-10 |
| H3-Perms       | Permissions-Policy absent → `server/middleware.py:107`                                              | Déjà en place         | vérifié 2026-04-10 |
| P1-ARCH-05a    | `app/home-learner/page.tsx` (317 L) → coque + `HomeLearnerContent`                                  | ARCH-HOME-LEARNER-01  | 2026-04-11         |
| P1-ARCH-05b    | `app/exercises/page.tsx` (311 L) → coque + `ExercisesPageContent`                                   | ARCH-EXERCISES-01     | 2026-04-11         |
| P1-PERF-01     | `app/leaderboard/page.tsx` (481 L) → décomposé en composants nommés                                 | ARCH-LEADERBOARD-01   | 2026-04-11         |
| P3-COMP-01a    | `BadgeCard.tsx` (494 L) → façade + sous-dossier `badgeCard/`                                        | COMP-BADGECARD-01     | 2026-04-11         |
| P3-COMP-01b    | `DiagnosticSolver.tsx` (456 L) → façade + états + primitives                                        | COMP-DIAGNOSTIC-01    | 2026-04-11         |
| ACTIF-01       | Pages SC candidates — `docs` convertie SC ; changelog / offline / contact restent client (preuve code) | ACTIF-01-TRUTH-01     | 2026-04-11         |
| ACTIF-02-UserAvatar | `UserAvatar` : `next/image` si URL ∈ remotePatterns ; sinon `<img>` (`nextImageRemoteSource.ts` + tests) | ACTIF-02-USERAVATAR-01 | 2026-04-11         |
| ACTIF-02-BadgeIcon | `BadgeIcon` : hybride `next/image` / `<img>` + fallback emoji via state ; utilitaire partagé `nextImageRemoteSource.ts` ; tests `BadgeIcon.test.tsx` | ACTIF-02-BADGEICON-01 | 2026-04-11         |
| ACTIF-02-ChatMessages | `ChatMessagesView` : exception native `<img>` (SSE / blob / data / dimensions intrinsèques) ; tests `ChatMessagesView.test.tsx` | ACTIF-02-CHATMESSAGES-01 | 2026-04-12         |
| ACTIF-06-users | `app/admin/users/page.tsx` → coque ; état + handlers dans **`hooks/useAdminUsersPageController.ts`** ; tests **`useAdminUsersPageController.test.tsx`** | ACTIF-06-ADMIN-USERS-01 | 2026-04-12         |

---

## 6. Décisions délibérées — ne pas contredire

Ces points ont fait l'objet d'une décision explicite. Codex ne doit **pas** les implémenter dans l'autre sens sans nouveau constat terrain.

### D-01 — Pas de barrel exports (`index.ts`) dans `lib/`

`[DÉCISION]` Les imports explicites `@/lib/security/buildContentSecurityPolicy` sont **la bonne pratique** pour Next.js 16 App Router.

**Pourquoi :** les barrel exports `index.ts` dans `lib/` nuisent au tree-shaking granulaire côté Server Components et peuvent introduire des dépendances circulaires (Matt Pocock, TypeScript Total 2023–2024). Invalidé par le débat multi-AI 2026-04-10.

**Ce qu'il ne faut pas faire :**

```typescript
// NE PAS créer cela dans lib/security/index.ts
export { buildContentSecurityPolicy } from "./buildContentSecurityPolicy";

// NE PAS importer ainsi
import { buildContentSecurityPolicy } from "@/lib/security";
```

**Ce qu'il faut faire :**

```typescript
// Import explicite — correct
import { buildContentSecurityPolicy } from "@/lib/security/buildContentSecurityPolicy";
```

### D-02 — `<img>` pour URLs dynamiques hors périmètre `remotePatterns` (révisé 2026-04-11)

`[DÉCISION]` Source de vérité partagée : **`lib/utils/nextImageRemoteSource.ts`** (`resolveNextImageRemoteDelivery`) — **à maintenir alignée** sur `images.remotePatterns` dans `next.config.ts`. **`userAvatarImageSource.ts`** délègue à ce module pour **`UserAvatar`**.

`[DÉCISION]` **`UserAvatar.tsx`** (lot **ACTIF-02-USERAVATAR-01**) : `next/image` si l’URL matche ce helper ; sinon **`<img>`** + `eslint-disable` ciblé.

`[DÉCISION]` **`BadgeIcon.tsx`** (lot **ACTIF-02-BADGEICON-01**) : même hybride pour `icon_url` HTTP ; pas de manipulation DOM impérative sur erreur de chargement.

`[DÉCISION]` **`ChatMessagesView.tsx`** (lot **ACTIF-02-CHATMESSAGES-01**) : **`<img>` natif** par **exception produit délibérée** — pas seulement « en attendant » : toute bascule **`next/image`** exigerait contrat URL/dimensions ou **`fill`** avec conteneur dimensionné, ce qui **n’est pas** acceptable sans changement UX (voir commentaire in-file et tests **`ChatMessagesView.test.tsx`**). **`resolveNextImageRemoteDelivery`** ne s’applique pas à ce flux.

**Ce qu'il ne faut pas faire :** forcer **`next/image`** avec dimensions fictives ou ratio inventé sur les illustrations chat ; rouvrir sans contrat backend/SSE et maquette validée.

### D-03 — `useLeaderboardPageController` non extrait

`[DÉCISION]` Le contrôleur dédié au leaderboard n'a pas été extrait dans le lot ARCH-LEADERBOARD-01. Le découpage en composants nommés a été jugé suffisant pour fermer la dette. Un contrôleur séparé peut être créé si un lot futur justifie l'investissement.

### D-04 — Coverage vitest : seuils ancrés sur mesure réelle (non à 55 % sans preuve)

`[DÉCISION]` Les seuils suivent une **mesure `vitest --coverage` réelle sur l’environnement le plus contraignant**, puis une marge conservatrice documentée (**`floor(mesure CI %) − 1`** par axe depuis le lot **`ACTIF-04-COVERAGE-01`**, 2026-04-12 : gates **43 / 36 / 40 / 44** pour une baseline GitHub Actions **44.57 / 37.22 / 41.47 / 45.68 %**). Les runs locaux plus hauts ne suffisent pas à justifier un bump. L'objectif 55 % reste un **horizon**, pas un seuil imposé sans nouvelle mesure CI-compatible. Ne pas augmenter les gates « par principe ».

---

## 7. Findings backend/sécurité hors périmètre frontend

Ces points concernent le backend Python ou la sécurité HTTP et ne changent pas le score frontend (7.05/10). Ils sont listés ici pour que Codex puisse les référencer sans confusion avec les findings frontend.

### Backend — 165 f-strings dans les loggers

`[CONSTAT]` Mesuré sur `master` :

- `app/` : 134 occurrences dans 36 fichiers
- `server/` : 31 occurrences dans 13 fichiers
- **Total : 165 exactement** — correspond au chiffre de l'audit complet

**Convention projet :** `logger.error("msg: %s", var)` — pas de f-string. Ruff règle G004.

`[RECOMMANDATION]` Corriger avec `ruff check --select G004 --fix app/ server/` + revue manuelle (3–4h).

`[VALIDATION]`

```bash
ruff check --select G004 app/ server/  # objectif : 0 warning
```

### Backend — mypy : 10 codes désactivés globalement

`[CONSTAT]` `pyproject.toml:41-52` désactive globalement : `no-any-return`, `assignment`, `arg-type`, `return-value`, `union-attr`, `attr-defined`, `var-annotated`, `call-overload`, `operator`, `index`. La vérification de types est quasi symbolique.

`[RECOMMANDATION]` Réactiver progressivement module par module, en commençant par les modules les plus critiques (`auth_service.py`, `challenge_validator.py`). Effort : 4–8h.

### Backend — H4 Fallback refresh token 7 jours

`[NON VÉRIFIÉ]` `auth_service.py:613-617`. Effort corrigé par le débat : 2h → **6–8h** (analyse impact sessions actives + rollout progressif).

### Backend — Rate limit `/api/users/me`

`[NON VÉRIFIÉ]` Endpoint exposé potentiellement sans rate-limit dédié. À confirmer par lecture des handlers.

### Backend — Décomposition `user_service.py` (1506 lignes)

`[NON VÉRIFIÉ]` Effort réel : 4–5h → **3–5 jours** (écriture de tests préalables obligatoire avant tout découpage).

---

## 8. Plan d'exécution solo-founder vers 9.5/10

Ordre par ratio impact/effort. Chaque sprint est réalisable en une session.

### Sprint A — Server Components (1–2h)

```
1. ~~ACTIF-01 clos (2026-04-11)~~ — `docs` en SC ; `changelog` / `offline` / `contact` documentées client.
```

### Sprint B — Images restantes (2–3h)

```
2. ~~UserAvatar.tsx~~ — fait (ACTIF-02-USERAVATAR-01)
3. ~~BadgeIcon.tsx~~ — fait (ACTIF-02-BADGEICON-01)
4. ~~ChatMessagesView.tsx~~ — fait (ACTIF-02-CHATMESSAGES-01 : exception `<img>` documentée + tests)
   → ~~ACTIF-02~~ **clos**
```

### Sprint C — Tests hooks critiques (3–4 semaines, par lots)

```
5. ~~Écrire tests useSubmitAnswer~~ — fait (`TEST-SUBMIT-ANSWER-01`, `hooks/useSubmitAnswer.test.ts` co-localisé).
6. ~~Écrire tests useIrtScores (210 L)~~ — fait (`TEST-IRT-SCORES-01`) ; test désormais co-localisé **`hooks/useIrtScores.test.ts`** (lot **`ACTIF-03-USEIRT-COLOCATE-01`**).
7. ~~Écrire tests useAIExerciseGenerator~~ — fait (`TEST-AI-GENERATOR-01`) ; test désormais co-localisé **`hooks/useAIExerciseGenerator.test.ts`** (lot **`ACTIF-03-USEAI-COLOCATE-01`**).
8. ~~Écrire tests useDiagnostic (232 L)~~ — fait (`TEST-DIAGNOSTIC-HOOK-01`, `hooks/useDiagnostic.test.ts` co-localisé) ; poursuivre le point 9 (seuils) et le reste du backlog hooks.
9. Remonter seuils `vitest.config.ts` **après mesure** `npx vitest run --coverage` (logique documentée in-config ; lot **`ACTIF-04-COVERAGE-01`** = rebaseline 2026-04-12) ; itérer avec nouveaux tests puis nouvelle mesure
   → Concerne ACTIF-04
```

### Sprint D — Backend qualité (3–4h)

```
10. ruff G004 --fix app/ server/ + revue manuelle (3h)
    → Concerne §7 backend f-strings
```

### Sprint E — Modularité progressive (1–2h par session)

```
11. ~~Co-localiser 3–5 tests pilotes~~ — pilotes `TEST-COLOCATE-PILOT-01` (4 fichiers : BadgeCard, DiagnosticSolver, useDiagnostic, useSubmitAnswer) puis **`ACTIF-03-USEAUTH-COLOCATE-01`** (`hooks/useAuth.test.ts`) puis **`ACTIF-03-BUILDCSP-COLOCATE-01`** / **`ACTIF-03-MIDDLEWARECSP-COLOCATE-01`** (`lib/security/buildContentSecurityPolicy.test.ts`, `lib/security/middlewareCsp.test.ts`) puis **`ACTIF-03-USEIRT-COLOCATE-01`** (`hooks/useIrtScores.test.ts`) puis **`ACTIF-03-USEAI-COLOCATE-01`** (`hooks/useAIExerciseGenerator.test.ts`) puis **`ACTIF-03-USESETTINGS-COLOCATE-01`** (`hooks/useSettingsPageController.test.ts`) puis **`ACTIF-03-USEBADGES-COLOCATE-01`** (`hooks/useBadgesPageController.test.ts`) puis **`ACTIF-03-DASHBOARD-COLOCATE-01`** (`hooks/useDashboardPageController.test.ts`) puis **`ACTIF-03-CONTENTLIST-COLOCATE-01`** (`hooks/useContentListPageController.test.tsx`) puis **`ACTIF-03-CHALLENGESOLVER-COLOCATE-01`** (`hooks/useChallengeSolverController.test.tsx`) puis **`ACTIF-03-EXERCISESOLVER-COLOCATE-01`** (`hooks/useExerciseSolverController.test.ts`) ; poursuivre par nouveaux lots ciblés — **ACTIF-03** toujours ouvert.
    → Concerne ACTIF-03
12. mypy : réactiver 1 code désactivé sur auth_service.py, valider, itérer
    → Concerne §7 mypy
```

### Sprint F — Admin controllers (2–3h par page)

```
13. ~~Extraire useAdminUsersPageController.ts depuis app/admin/users/page.tsx~~ — fait (**`ACTIF-06-ADMIN-USERS-01`**, 2026-04-12)
    → Concerne ACTIF-06
14. Extraire useAdminAiMonitoringPageController.ts depuis app/admin/ai-monitoring/page.tsx (572L)
    → Concerne ACTIF-06
```

### Backlog non planifié

- `_colorMap.ts` partagé entre renderers (ACTIF-07) — 1h, non bloquant
- `console.error` sans garde dev : `useAcademyStats.ts:88`, `useSettings.ts:140`, `auth-session-sync.ts:111` — remplacer par `debugError()` de `lib/utils/debug.ts` — 15 min
- Décomposition `useProfilePageController.ts` (463 L) — non bloquant
- Décomposition `exportPDF.ts` / `exportExcel.ts` — non bloquant
- Décomposition `user_service.py` backend (1506 L) — nécessite tests préalables

---

## 9. Méthodologie

### Sources lues pendant l'audit initial (2026-04-09)

| Tâche               | Méthode                                     | Résultat                                         |
| ------------------- | ------------------------------------------- | ------------------------------------------------ |
| Guardrails          | Lecture complète `frontendGuardrails.ts`    | 523 lignes, 17 surfaces, 17 seams, 20 lib requis |
| Fichiers volumineux | `wc -l` sur app/, components/, hooks/, lib/ | 19 fichiers > 300 lignes                         |
| `"use client"`      | grep dans app/                              | 38 fichiers sur ~50                              |
| `eslint-disable`    | grep + contexte ±1 ligne                    | 13 occurrences dans 12 fichiers                  |
| `: any` / `as any`  | grep exhaustif hors node_modules            | 0 résultat                                       |
| `fetch()` direct    | grep dans app/ + components/                | 0 résultat métier                                |
| TODO/FIXME/HACK     | grep dans tout frontend/                    | 0 résultat                                       |
| staleTime           | grep dans hooks/                            | 41 occurrences, toutes définies                  |
| `next/image`        | grep dans app/ + components/                | 1 import, 5 contournements                       |

### Vérifications terrain post-audit (2026-04-10/11)

| Point                 | Fichier lu                        | Résultat                                          |
| --------------------- | --------------------------------- | ------------------------------------------------- |
| H1 diagnose prod      | `logging_config.py:113,122`       | RÉSOLU — conditionnel `_is_production_like_env()` |
| H2 HSTS               | `server/middleware.py:108-109`    | RÉSOLU — conditionnel `_is_production()`          |
| H3 Permissions-Policy | `server/middleware.py:107`        | RÉSOLU — présent                                  |
| BUG .dockerignore     | `.dockerignore:147-148`           | CORRIGÉ (AUDIT-QUICKWINS-01)                      |
| M5 PII usernames      | `auth_service.py` (grep username) | RÉSOLU (SEC-PII-LOGS-01)                          |
| F1 X-XSS-Protection   | `server/middleware.py:31`         | CORRIGÉ (AUDIT-QUICKWINS-01)                      |
| 165 f-strings logger  | `app/` + `server/` (grep)         | CONFIRMÉ OUVERT — 134 + 31 = 165                  |
| mypy codes désactivés | `pyproject.toml:41-52`            | CONFIRMÉ OUVERT — 10 codes                        |

### Note sur le scoring

Les scores par dimension (0–10) sont des jugements calibrés, pas une addition mécanique de critères binaires. Échelle : 0–3 = problématique, 4–6 = acceptable, 7–8 = bon, 9–10 = excellent.

---

_Audit initial : 2026-04-09. Dernière mise à jour : 2026-04-12. Dernière vérification terrain : 2026-04-12 (**ACTIF-02-CHATMESSAGES-01** : `ChatMessagesView` exception `<img>` + tests ; **ACTIF-03-USEAUTH-COLOCATE-01** : `hooks/useAuth.test.ts` co-localisé ; **ACTIF-03-BUILDCSP-COLOCATE-01** / **ACTIF-03-MIDDLEWARECSP-COLOCATE-01** : `lib/security/buildContentSecurityPolicy.test.ts` + `lib/security/middlewareCsp.test.ts` co-localisés ; **ACTIF-03-USEIRT-COLOCATE-01** : `hooks/useIrtScores.test.ts` co-localisé ; **ACTIF-03-USEAI-COLOCATE-01** : `hooks/useAIExerciseGenerator.test.ts` co-localisé ; **ACTIF-03-USESETTINGS-COLOCATE-01** : `hooks/useSettingsPageController.test.ts` co-localisé ; **ACTIF-03-USEBADGES-COLOCATE-01** : `hooks/useBadgesPageController.test.ts` co-localisé ; **ACTIF-03-DASHBOARD-COLOCATE-01** : `hooks/useDashboardPageController.test.ts` co-localisé ; **ACTIF-03-CONTENTLIST-COLOCATE-01** : `hooks/useContentListPageController.test.tsx` co-localisé ; **ACTIF-03-CHALLENGESOLVER-COLOCATE-01** : `hooks/useChallengeSolverController.test.tsx` co-localisé ; **ACTIF-03-EXERCISESOLVER-COLOCATE-01** : `hooks/useExerciseSolverController.test.ts` co-localisé ; **ACTIF-04-COVERAGE-01** : seuils vitest **43/36/40/44** depuis baseline CI GitHub Actions **44.57/37.22/41.47/45.68 %** ; **ACTIF-06-ADMIN-USERS-01** : `useAdminUsersPageController` + page users allégée ; **finding ACTIF-02 fermé**). Toutes les assertions citent fichier:ligne lu directement._
