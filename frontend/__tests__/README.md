# 🧪 Tests Frontend Mathakine

## 📋 Structure des Tests

```
__tests__/
├── unit/                    # Tests unitaires
│   ├── architecture/       # FFI-L17A+B — garde-fous structure (budgets LOC, seams, ancres lib/, ownership)
│   ├── components/         # Tests des composants React
│   └── hooks/              # Tests des hooks personnalisés
├── integration/            # Tests d'intégration (à venir)
├── e2e/                    # Tests end-to-end (Playwright)
│   ├── auth.spec.ts       # Tests d'authentification
│   └── exercises.spec.ts  # Tests des exercices
└── accessibility/          # Tests d'accessibilité
    └── accessibility.test.tsx
```

## 🚀 Commandes Disponibles

### Garde-fous architecture (FFI-L17A + FFI-L17B)

Vérifie l’existence des seams critiques, les budgets LOC des facades/pages livrées FFI-L11–L16, les fichiers `lib/` canoniques listés dans `REQUIRED_CANONICAL_LIB_FILES`, et l’ownership du chatbot global (`components/chat/ChatbotFloatingGlobal.tsx` uniquement — pas de doublon sous `components/home/` ni `components/layout/`). Source de vérité unique : `lib/architecture/frontendGuardrails.ts` (y compris `OWNERSHIP_RULE_GROUPS` pour les conventions documentées).

```bash
cd frontend && npm run architecture:check
```

### Tests Unitaires (Vitest)

```bash
# Lancer tous les tests unitaires
npm run test

# Mode watch (re-exécution automatique)
npm run test -- --watch

# Interface UI interactive
npm run test:ui

# Avec couverture de code
npm run test:coverage
```

### Tests E2E (Playwright)

```bash
# Lancer tous les tests E2E
npm run test:e2e

# Interface UI interactive
npm run test:e2e:ui

# Tests sur navigateur spécifique
npx playwright test --project=chromium
```

### Tous les Tests

```bash
# Lancer unitaires + E2E
npm run test:all
```

## 📝 Écrire des Tests

### Test Unitaire de Composant

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('affiche le contenu correctement', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Test E2E

```typescript
import { test, expect } from "@playwright/test";

test("parcours utilisateur complet", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading")).toBeVisible();
});
```

## ✅ Bonnes Pratiques

1. **Tests unitaires** : Tester la logique isolée des composants
2. **Tests E2E** : Tester les parcours utilisateur complets
3. **Tests accessibilité** : Vérifier ARIA, navigation clavier, contraste
4. **Couverture** : ~71 % actuellement sur les fichiers testés
5. **Nommage** : Utiliser des noms descriptifs (`it('affiche...')`, `it('should...')`)

## 🔧 Configuration

- **Vitest** : `vitest.config.ts`
- **Playwright** : `playwright.config.ts`
- **Setup** : `vitest.setup.ts` (mocks globaux : next/navigation, next/image, matchMedia)

## 📊 Couverture de Code

`npm run test:coverage` génère les rapports dans `coverage/` (text, json, html, lcov). Le lcov est envoyé à Codecov en CI.

## 🔌 Providers pour composants avec contexte

Composants utilisant `useTranslations`, `useCompletedExercises`, etc. : fournir un wrapper avec `NextIntlClientProvider` + `QueryClientProvider`. Voir `ExerciseCard.test.tsx` en exemple. Mocker les hooks API avec `vi.mock('@/hooks/useCompletedItems')` pour éviter les appels réseau.

## 📂 Menu / Popover fermé par défaut

Pour tester le contenu d’un menu (ex. AccessibilityToolbar) : ouvrir le menu avec `userEvent.click()` avant les assertions. Les options sont en `role="switch"` avec `aria-label`.

## 🐛 Debugging

### Vitest

```bash
# Mode debug avec breakpoints
npm run test -- --inspect-brk
```

### Playwright

```bash
# Mode debug interactif
npm run test:e2e:ui
```
