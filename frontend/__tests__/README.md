# 🧪 Tests Frontend Mathakine

## 📋 Structure des Tests

```
__tests__/
├── unit/                    # Tests unitaires
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
import { test, expect } from '@playwright/test';

test('parcours utilisateur complet', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading')).toBeVisible();
});
```

## ✅ Bonnes Pratiques

1. **Tests unitaires** : Tester la logique isolée des composants
2. **Tests E2E** : Tester les parcours utilisateur complets
3. **Tests accessibilité** : Vérifier ARIA, navigation clavier, contraste
4. **Couverture** : Viser au moins 70% de couverture de code
5. **Nommage** : Utiliser des noms descriptifs (`it('should...')`)

## 🔧 Configuration

- **Vitest** : `vitest.config.ts`
- **Playwright** : `playwright.config.ts`
- **Setup** : `vitest.setup.ts` (mocks globaux)

## 📊 Couverture de Code

La couverture est générée dans `coverage/` après `npm run test:coverage`.

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

