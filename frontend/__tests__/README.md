# Tests Frontend Mathakine

Updated : 2026-04-10

## Structure

```text
__tests__/
|-- unit/          # tests unitaires Vitest
|-- integration/   # tests d'integration frontend
|-- e2e/           # tests Playwright
`-- accessibility/ # checks accessibilite ponctuels
```

### E2E actuels

Sous `frontend/__tests__/e2e/` :

- `auth.spec.ts`
- `dashboard.spec.ts`
- `badges.spec.ts`
- `settings.spec.ts`
- `exercises.spec.ts`
- `admin.spec.ts`
- helper : `helpers/demoUserAuth.ts`

Etat terrain :

- les parcours authentifies reels couverts aujourd'hui portent sur `login`, `dashboard`, `badges`, `settings`
- ces scenarios sont limites a Chromium
- il n'y a pas de `globalSetup` ni de `storageState` partage par defaut

---

## Commandes

### Vitest

```bash
npm run test
npm run test:ui
npm run test:coverage
```

### Playwright

```bash
npm run test:e2e
npm run test:e2e:ui
npx playwright test --project=chromium
```

### Garde-fous architecture

```bash
npm run architecture:check
```

---

## Bonnes pratiques

1. tester la logique isolee dans `unit/`
2. garder les E2E sur des contrats visibles et robustes
3. ouvrir explicitement menus et popovers avant assertion
4. fournir les providers requis (`NextIntlClientProvider`, `QueryClientProvider`, etc.)
5. preferer des mocks de hooks/API plutot que du reseau en tests unitaires

---

## Couverture

La source de verite couverture frontend est :

- `frontend/vitest.config.ts`

Le repo a maintenant des seuils minimaux explicites :

- `statements: 43`
- `branches: 36`
- `functions: 39`
- `lines: 44`

Donc :

- ne pas maintenir un pourcentage ecrit en dur dans ce README
- utiliser `npm run test:coverage` et `vitest.config.ts` comme reference

---

## Providers et patterns utiles

### Composants avec i18n ou React Query

Fournir un wrapper de test avec les providers adequats.

Exemples :

- `NextIntlClientProvider`
- `QueryClientProvider`

### Menus / popovers

Pour tester le contenu d'un menu, l'ouvrir d'abord avec `userEvent.click(...)`.

### Hooks et mutations

Mocker les hooks reseau ou API avec `vi.mock(...)` pour garder les tests unitaires deterministes.

---

## Debug

### Vitest

```bash
npm run test -- --inspect-brk
```

### Playwright

```bash
npm run test:e2e:ui
```

---

## References

- `frontend/vitest.config.ts`
- `frontend/playwright.config.ts`
- `docs/01-GUIDES/TESTING.md`
