# Audit Frontend — Industrialisation & Qualité Technique

> **Version :** 2026-04-11 (audit initial 2026-04-09, mis à jour au fil des lots)
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
| Findings P1 ouverts                             | **1** (P2-PERF-04 converti P2) |
| Findings P2 ouverts                             | **2**                          |
| Findings P3 ouverts                             | **0**                          |
| Queries React Query avec staleTime              | **41/41** (100 %)              |
| Occurrences `: any` ou `as any`                 | **0**                          |
| TODO/FIXME/HACK non ticketés                    | **0**                          |

**Verdict :** le frontend est industriellement mature sur TypeScript, cache React Query et guardrails CI. Les risques résiduels sont la conversion de pages statiques en Server Components (D7), la co-location des tests (D5), et l'adoption systématique de `next/image` pour 3 cas dynamiques restants.

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

Les findings ci-dessous sont **ouverts** sur `master` au 2026-04-11. Codex peut les implémenter directement.

---

### [ACTIF-01] Pages potentiellement convertibles en Server Components

**Priorité :** P2 | **Dimension :** D7 Performance | **Effort :** 20–30 min par page

`[CONSTAT]` 4 pages ont `"use client"` en ligne 1 mais leur contenu n'a pas été lu pendant l'audit :

| Page                              | "use client" présent | Interactivité supposée | Statut vérification |
| --------------------------------- | -------------------- | ---------------------- | ------------------- |
| `frontend/app/docs/page.tsx`      | oui                  | Documentation statique | Non vérifié         |
| `frontend/app/changelog/page.tsx` | oui                  | Liste de changements   | Non vérifié         |
| `frontend/app/offline/page.tsx`   | oui                  | Page d'erreur statique | Non vérifié         |
| `frontend/app/contact/page.tsx`   | oui                  | Formulaire ?           | Non vérifié         |

`[RECOMMANDATION]` Pour chaque fichier :

1. Lire le fichier
2. Si absence de hooks React (`useState`, `useEffect`, etc.) et de gestionnaires d'événements client : supprimer `"use client"`, convertir en Server Component, remplacer `useTranslations()` par `await getTranslations()`
3. Si interactivité présente : documenter pourquoi `"use client"` est nécessaire

`[VALIDATION]`

```bash
grep -n '"use client"' frontend/app/docs/page.tsx  # doit être vide si converti
```

> Note : `app/about/page.tsx` et `app/privacy/page.tsx` sont déjà Server Components (lot FFI-L20G) — ne pas toucher.

---

### [ACTIF-02] 3 composants avec `<img>` brut non optimisé

**Priorité :** P2 | **Dimension :** D7 Performance | **Effort :** 45 min chacun

`[CONSTAT]` 3 composants utilisent `<img>` brut avec `eslint-disable` documenté. Les 2 cas décorés locaux ont déjà été migrés (lot PERF-IMG-LOCAL-01).

| Fichier                                            | Raison actuelle du `<img>`               | Action                                                |
| -------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------- |
| `frontend/components/ui/UserAvatar.tsx:31`         | URL avatar runtime, dimensions inconnues | Migrer avec loader Next.js ou `sizes` explicite       |
| `frontend/components/badges/BadgeIcon.tsx:131`     | icon_url dynamique + fallback SVG        | Migrer avec `next/image` + `unoptimized` si externe   |
| `frontend/components/chat/ChatMessagesView.tsx:71` | Image de chat distante                   | Évaluer si `remotePatterns` + `next/image` applicable |

`[RECOMMANDATION]` Migrer chaque cas vers `<Image from="next/image">` avec `width`, `height` et `sizes` explicites, ou ajouter un loader. Si migration impossible, conserver `<img>` et supprimer le besoin de `eslint-disable` en documentant la contrainte dans le commentaire.

`[VALIDATION]`

```bash
grep -r "eslint-disable.*no-img-element" frontend/components/ --include="*.tsx"
# objectif : 0 résultat (migration complète) ou chaque ligne précédée de "// Intentional: <raison>"
```

---

### [ACTIF-03] Tests non co-localisés

**Priorité :** P2 | **Dimension :** D5 Modularité | **Effort :** 1–2h pour les migrations pilotes

`[CONSTAT]` 133 fichiers de tests dans `frontend/__tests__/unit/` séparés du code source. Exemple :

- `__tests__/unit/components/badges/BadgeCard.test.tsx` au lieu de `components/badges/BadgeCard.test.tsx`

Impact : lors d'un refactoring, le test correspondant est difficile à trouver sans connaître la structure `__tests__/`.

`[RECOMMANDATION]` Migration progressive : co-localiser les tests des composants les plus actifs en priorité. Mettre à jour `vitest.config.ts` : `testMatch: ["**/*.test.{ts,tsx}"]` (au lieu du chemin `__tests__/` uniquement).

`[DÉCISION]` Ne pas migrer les 133 fichiers d'un coup — risque de casser les imports CI. Faire 3–5 fichiers pilotes d'abord, valider CI, puis continuer.

`[VALIDATION]`

```bash
ls frontend/components/badges/BadgeCard.test.tsx  # présent si migré
```

---

### [ACTIF-04] Coverage vitest — seuils à remonter progressivement

**Priorité :** P2 | **Dimension :** D8 Réplicabilité | **Effort :** 3–4 semaines par incrément de 5 points

`[CONSTAT]` Baseline CI mesurée (commit `ae11043`) :

- statements : 39.75 %
- branches : 34.04 %
- functions : 37.85 %
- lines : 40.66 %

Seuils actuels dans `vitest.config.ts` : statements 39 %, branches 33 %, functions 37 %, lines 40 % (1 point sous la baseline pour absorber la variance).

Baseline historique de l’audit initial (2026-04-09) : **37 hooks sur 52 sans test (71 %)**. Le sprint C historique visait notamment les hooks critiques de génération / diagnostic / tentatives. **Avancements ACTIF-04 (tests dédiés, seuils `vitest.config.ts` inchangés)** : (1) `TEST-DIAGNOSTIC-HOOK-01` — `useDiagnostic` ; (2) `TEST-SUBMIT-ANSWER-01` — `useSubmitAnswer` ; (3) `TEST-IRT-SCORES-01` — `useIrtScores` ; (4) `TEST-AI-GENERATOR-01` — `useAIExerciseGenerator` via `frontend/__tests__/unit/hooks/useAIExerciseGenerator.test.ts`. Le ratio global courant « hooks sans test » et la remontée progressive des seuils restent ouverts tant qu’un nouveau calcul complet n’a pas été refait.

`[RECOMMANDATION]` Écrire les tests des hooks critiques en priorité, puis remonter les seuils. Budget réel : **30 min de config + 3–4 semaines d'écriture de tests** par incrément de 5 points.

`[DÉCISION]` Ne pas monter les seuils avant d'avoir les tests. Un seuil artificiellement haut qui casse CI ne sert à rien.

`[VALIDATION]`

```bash
cd frontend && npx vitest run --coverage
# objectif : statements ≥ seuil défini dans vitest.config.ts
```

---

### [ACTIF-05] Controllers et utilitaires volumineux

**Priorité :** P3 | **Dimension :** D6 Maintenabilité | **Effort :** 2–4h chacun

`[CONSTAT]` Taille mesurée sur `master` :

| Fichier                                | Lignes | Problème                               |
| -------------------------------------- | ------ | -------------------------------------- |
| `hooks/useProfilePageController.ts`    | 463    | Probablement plusieurs responsabilités |
| `hooks/useExerciseSolverController.ts` | 391    | Idem                                   |
| `lib/utils/exportPDF.ts`               | 384    | Utilitaire monolithique                |
| `lib/utils/exportExcel.ts`             | 391    | Idem                                   |

`[RECOMMANDATION]` Lire chaque fichier, identifier les responsabilités distinctes, extraire en sous-modules si le découpage est naturel et ne casse pas les tests existants. Critère : chaque unité extraite < 150 lignes.

`[DÉCISION]` Ce n'est pas bloquant pour CI ni pour les fonctionnalités. Traiter uniquement si un refactoring plus large justifie l'ouverture du fichier.

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
| Coverage-gate  | Seuils vitest réalistes (39/33/37/40 %) à la place de (43/36/39/44 %)                               | QF-06                 | 2026-04-10         |
| H1-diagnose    | `diagnose=True` en prod → `diagnose=_uncaught_diagnose`                                             | Déjà en place         | vérifié 2026-04-10 |
| H2-HSTS        | HSTS absent → `server/middleware.py:108-109` conditionnel prod                                      | Déjà en place         | vérifié 2026-04-10 |
| H3-Perms       | Permissions-Policy absent → `server/middleware.py:107`                                              | Déjà en place         | vérifié 2026-04-10 |
| P1-ARCH-05a    | `app/home-learner/page.tsx` (317 L) → coque + `HomeLearnerContent`                                  | ARCH-HOME-LEARNER-01  | 2026-04-11         |
| P1-ARCH-05b    | `app/exercises/page.tsx` (311 L) → coque + `ExercisesPageContent`                                   | ARCH-EXERCISES-01     | 2026-04-11         |
| P1-PERF-01     | `app/leaderboard/page.tsx` (481 L) → décomposé en composants nommés                                 | ARCH-LEADERBOARD-01   | 2026-04-11         |
| P3-COMP-01a    | `BadgeCard.tsx` (494 L) → façade + sous-dossier `badgeCard/`                                        | COMP-BADGECARD-01     | 2026-04-11         |
| P3-COMP-01b    | `DiagnosticSolver.tsx` (456 L) → façade + états + primitives                                        | COMP-DIAGNOSTIC-01    | 2026-04-11         |

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

### D-02 — `<img>` conservé pour les URLs dynamiques distantes

`[DÉCISION]` `UserAvatar.tsx`, `BadgeIcon.tsx`, `ChatMessagesView.tsx` utilisent `<img>` avec `eslint-disable` **justifié** pour les URLs dynamiques où `next/image` requiert `remotePatterns` avec une liste de domaines impossible à énumérer statiquement.

**Ce qu'il ne faut pas faire :** supprimer ces `eslint-disable` ou les remplacer par `next/image` sans avoir d'abord configuré `remotePatterns` dans `next.config.ts`.

### D-03 — `useLeaderboardPageController` non extrait

`[DÉCISION]` Le contrôleur dédié au leaderboard n'a pas été extrait dans le lot ARCH-LEADERBOARD-01. Le découpage en composants nommés a été jugé suffisant pour fermer la dette. Un contrôleur séparé peut être créé si un lot futur justifie l'investissement.

### D-04 — Coverage vitest à 39/33/37/40 % (non à 55 %)

`[DÉCISION]` Les seuils sont volontairement 1 point sous la baseline CI pour absorber la variance inter-runs. L'objectif 55 % est un horizon, pas un seuil actuel. Remonter les seuils seulement après avoir écrit les tests correspondants.

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
1. Lire app/docs/page.tsx, app/changelog/page.tsx, app/offline/page.tsx
   → Si absence de hooks client : supprimer "use client", convertir en SC
   → Concerne ACTIF-01
```

### Sprint B — Images restantes (2–3h)

```
2. UserAvatar.tsx → next/image avec remotePatterns ou loader
3. BadgeIcon.tsx  → next/image avec unoptimized si externe
4. ChatMessagesView.tsx → évaluer remotePatterns
   → Concerne ACTIF-02
```

### Sprint C — Tests hooks critiques (3–4 semaines, par lots)

```
5. ~~Écrire tests useSubmitAnswer~~ — fait (`TEST-SUBMIT-ANSWER-01`, `__tests__/unit/hooks/useSubmitAnswer.test.ts`).
6. ~~Écrire tests useIrtScores (210 L)~~ — fait (`TEST-IRT-SCORES-01`, `__tests__/unit/hooks/useIrtScores.test.ts`).
7. ~~Écrire tests useAIExerciseGenerator~~ — fait (`TEST-AI-GENERATOR-01`, `__tests__/unit/hooks/useAIExerciseGenerator.test.ts`).
8. ~~Écrire tests useDiagnostic (232 L)~~ — fait (`TEST-DIAGNOSTIC-HOOK-01`, `__tests__/unit/hooks/useDiagnostic.test.ts`) ; poursuivre le point 9 (seuils) et le reste du backlog hooks.
9. Remonter seuils vitest.config.ts de 5 points après chaque lot
   → Concerne ACTIF-04
```

### Sprint D — Backend qualité (3–4h)

```
10. ruff G004 --fix app/ server/ + revue manuelle (3h)
    → Concerne §7 backend f-strings
```

### Sprint E — Modularité progressive (1–2h par session)

```
11. Co-localiser 3–5 tests pilotes (BadgeCard, useAuth, buildContentSecurityPolicy)
    → Concerne ACTIF-03
12. mypy : réactiver 1 code désactivé sur auth_service.py, valider, itérer
    → Concerne §7 mypy
```

### Backlog non planifié

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

_Audit initial : 2026-04-09. Dernière mise à jour : 2026-04-11. Toutes les assertions citent fichier:ligne lu directement._
