# Audit externe — Dette qualité frontend

**Date** : 20/02/2026  
**Méthode** : Exécution `npm run lint` et `npm run test:coverage` sur l'état actuel du dépôt.

---

## 1. Constatation 3.2 — Validation

### 1.1 Lint : volume élevé d'erreurs/avertissements

**Constat réel** : ✅ **Confirmé**

```
✖ 209 problems (139 errors, 70 warnings)
1 error et 1 warning fixables avec --fix
```

| Catégorie | Quantité estimée | Exemples |
|-----------|------------------|----------|
| `@typescript-eslint/no-explicit-any` | ~60 | `any` dans tests, hooks, utils, types/api.ts |
| `react-hooks/set-state-in-effect` | ~5 | admin/config, admin/content — setState synchrone dans useEffect |
| `react-hooks/static-components` | ~4 | SortIcon défini dans le render (admin/content) |
| `@typescript-eslint/no-require-imports` | ~8 | scripts i18n (check-translations.js, extract-hardcoded.js, validate-structure.js), vitest.setup.ts |
| `@typescript-eslint/no-unused-vars` | ~20+ | Variables/imports non utilisés |

**Précision** : Les `require()` dans les scripts i18n (.js) et vitest.setup.ts sont des imports CommonJS. Les pages/admin (config, content) concentrent plusieurs erreurs React (setState dans effect, composant dans render).

---

### 1.2 Tests : sous-ensemble réduit vs surface fonctionnelle

**Constat réel** : ✅ **Confirmé**

| Métrique | Valeur |
|----------|--------|
| Fichiers de test | 4 |
| Tests unitaires | 20 |
| Couverture statements | 68,91 % |
| Couverture branches | 55,42 % |
| Couverture fonctions | 54,68 % |

**Composants/pages couverts** :
- BadgeCard, ExerciseCard, ContentCardBase
- useAccessibleAnimation, AccessibilityToolbar
- utils (cn, lib), constants partiels

**Surface non couverte** (exemples) :
- Pages : dashboard, challenges, badges, profile, admin/*, register, login, etc.
- Composants : Header, PageTransition, ChallengeSolver, visualizations (7+), Recommendations, StatsCard, etc.
- Hooks : useAdminUsers, useAdminExercises, useTranslations (38 %), stores (themeStore 56 %, accessibilityStore 17 %)

**Ratio** : ~120+ fichiers .tsx vs 4 fichiers de test ≈ 3 % des modules couverts par des tests.

---

## 2. Plan d'action (optionnel)

### P1 — Corrections rapides (peu de risque)

| Action | Effort | Impact |
|--------|--------|--------|
| `npm run lint -- --fix` | 1 min | Corrige 1 error + 1 warning |
| Typer les `any` dans vitest.setup.ts (2) | 10 min | Réduit erreurs tests |
| Typer les `any` dans __tests__ (11) | 20 min | Tests conformes au lint |
| Déplacer SortIcon hors du render (admin/content) | 15 min | Corrige 4 erreurs static-components |
| Remplacer setState direct dans useEffect par initialisation dérivée (admin/config, admin/content) | 30 min | Corrige set-state-in-effect |

**Estimation** : ~1h pour ~20 erreurs corrigées.

### P2 — Scripts i18n (CommonJS)

| Action | Effort | Risque |
|--------|--------|--------|
| Convertir `require()` en `import` dans scripts i18n | 30 min | Faible — exécutés en Node |
| Ou : exclure `scripts/` du lint | 5 min | Règle le conflit sans changer le code |

### P3 — Couverture tests (post-MVP)

| Priorité | Cible | Effort |
|----------|-------|--------|
| Haute | Pages critiques : dashboard, challenges, profile | 2–3 j |
| Moyenne | Hooks métier (useTranslations, stores) | 1–2 j |
| Basse | Visualisations, admin | 2–3 j |

---

## 3. Conclusion

| Constatation | Validée | Gravité |
|--------------|---------|---------|
| Lint : volume élevé erreurs/warnings | Oui | Moyenne — 209 problèmes, majoritairement types et patterns React |
| Tests : sous-ensemble réduit | Oui | Élevée — ~3 % des modules testés, zones sensibles non couvertes |

**Recommandation MVP** : Appliquer P1 (corrections rapides) pour réduire le bruit du lint. Reporter P2 et P3 après sortie MVP si besoin de prioriser le déploiement.

---

## 4. Corrections appliquées (15/02/2026)

Suite à l'audit, les corrections suivantes ont été appliquées (commit `379fa47`).

### 4.1 Typage TypeScript strict — visualData

**Problème** : Les renderers de visualisation (`ChessRenderer`, `CodingRenderer`, `DeductionRenderer`, etc.) reçoivent `visualData: Record<string, unknown>`. Les valeurs extraites (`visualData.description`, `visualData.piece`, etc.) étaient inférées en `unknown` ou `{}`, provoquant des erreurs TypeScript au build.

**Corrections** : Typage explicite des extractions dans tous les renderers :
- `String(visualData.xxx ?? "")` pour les chaînes affichées en JSX
- `Array.isArray(visualData.xxx) ? visualData.xxx : []` pour les tableaux
- `Boolean(condition) && <jsx>` au lieu de `condition && <jsx>` pour éviter `unknown` comme ReactNode
- Casts `as Record<string, unknown>` pour accès aux propriétés d'objets dynamiques

**Fichiers modifiés** : `ChessRenderer`, `CodingRenderer`, `DeductionRenderer`, `DefaultRenderer`, `GraphRenderer`, `PatternRenderer`, `ProbabilityRenderer`, `PuzzleRenderer`, `RiddleRenderer`, `SequenceRenderer`, `VisualRenderer`.

### 4.2 Hook useAccessibleAnimation (framer-motion)

**Problème** : `createVariants` et `createTransition` retournaient `Record<string, unknown>`, incompatible avec les types stricts `Variants` et `Transition` de framer-motion.

**Correction** : Import des types `Variants` et `Transition`, signature et retours typés. Cast `as Transition` pour les objets de transition construits dynamiquement.

### 4.3 Validation dashboard

**Problème** : `safeValidateUserStats` accédait à `stats.level.current` sans typage, et les objets `progress_over_time`, `exercises_by_day` étaient assignés sans validation de forme.

**Correction** : Vérifications `typeof`, extraction typée de `level`, cast `NonNullable<UserStats["progress_over_time"]>` après validation des champs requis.

### 4.4 Autres corrections

| Fichier | Correction |
|---------|------------|
| `vitest.setup.ts` | Cast `localStorageMock as unknown as Storage` (mock incomplet) |
| `eslint.config.mjs` | Exclusion `scripts/**` du lint (P2) |
| Divers | `any` → types précis, `no-unused-vars`, `error-boundaries`, `purity`, `static-components`, `no-img-element`, `no-unescaped-entities` |

### 4.5 Résultat

- **Build** : ✅ `npm run build` OK
- **Tests unitaires** : ✅ 20 tests Vitest passés
- **Tests E2E** : requièrent `npx playwright install` (navigateurs non installés en local)
