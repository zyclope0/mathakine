# Frontend Mathakine - Next.js

**Version produit visible** : `3.6.0-beta.5`
**Statut** : beta  
**Framework** : Next.js `16.2.3` + App Router  
**Langage** : TypeScript strict

---

## Objectif

Ce dossier contient le frontend web de Mathakine :

- application Next.js App Router
- UI React/Tailwind/shadcn
- proxies Next pour certains appels backend
- i18n FR/EN via `next-intl`
- tests Vitest et Playwright

Le frontend est maintenant sur un socle qualite renforce :

- lint type-aware durci
- couverture Vitest avec seuils minimaux
- E2E authentifie Chromium sur les surfaces principales
- CSP nonce-based en production sur `script-src`

---

## Prerequis

- Node.js `18.17+` (20+ recommande)
- npm `9+`
- backend Mathakine joignable, par defaut sur `http://localhost:10000`

---

## Installation

```bash
cd frontend
npm install
```

Creer ensuite `.env.local` a partir de `frontend/.env.example`.

---

## Commandes principales

### Developpement

```bash
npm run dev
npm run build
npm start
npm run lint
npm run format
npm run format:check
```

### Tests

```bash
npm run test
npm run test:coverage
npm run test:e2e
npm run test:all
npm run architecture:check
```

### i18n

```bash
npm run i18n:validate
npm run i18n:check
npm run i18n:extract
npm run i18n:all
```

Regle pratique :

- pour un lot i18n borne : `i18n:validate` + `i18n:check`
- `i18n:extract` / `i18n:all` servent plutot d'audit global, car ils peuvent encore remonter des hardcodes hors du lot traite

---

## Structure

```text
frontend/
|-- app/              # routes App Router, pages et API routes Next
|-- components/       # composants UI et metier
|-- hooks/            # 58 hooks React (majoritairement React Query)
|-- lib/              # utilitaires, stores, auth, securite, API, i18n
|-- messages/         # dictionnaires FR / EN
|-- public/           # assets statiques
|-- scripts/          # scripts utilitaires (dont i18n)
|-- styles/           # styles additionnels
|-- types/            # types TypeScript
`-- __tests__/        # tests Vitest / Playwright
```

Repere utile :

- proxies Next : `app/api/**`
- CSP / nonce : `lib/security/**` + `proxy.ts`
- i18n runtime : `components/providers/NextIntlProvider.tsx`
- auth client : `hooks/useAuth.ts`

---

## Architecture

### Stack

- Next.js 16 App Router
- React 19
- TypeScript strict
- Tailwind CSS v4
- shadcn/ui
- TanStack Query v5
- Zustand
- next-intl
- Sentry
- Vitest + Playwright

### Patterns

- logique reseau dans les hooks et utilitaires `lib/`
- composants de vue aussi purs que possible
- pages route-level fines
- proxies Next minces, logique partagee dans `lib/api/`
- references documentaires actives : `README_TECH.md`, audits actifs sous `docs/03-PROJECT/`, et `.claude/session-plan.md` comme note locale de pilotage (pas comme preuve runtime autonome)

---

## Internationalisation

- bibliotheque : `next-intl` `^4.9.1`
- messages : `messages/fr.json`, `messages/en.json`
- provider : `components/providers/NextIntlProvider.tsx`
- locale stockee dans Zustand (`localeStore`)

Etat actuel :

- les pages route-level admin et `offline` ont ete sorties des hardcodes principaux
- le chrome `app/admin/layout.tsx` est maintenant aligne sur `adminPages.layout.*`
- les descriptions de toasts auth de `hooks/useAuth.ts` passent par `toasts.auth.*`
- `i18n:extract` peut encore remonter des hardcodes hors du lot i18n traite

Reference :

- `../docs/02-FEATURES/I18N.md`
- `../docs/01-GUIDES/I18N_CONTRIBUTION.md`

---

## Tests

### Vitest

- configuration : `vitest.config.ts`
- seuils actifs :
  - `statements: 46`
  - `branches: 38`
  - `functions: 42`
  - `lines: 48`

### Playwright

Specs actuelles :

- `auth.spec.ts`
- `dashboard.spec.ts`
- `badges.spec.ts`
- `settings.spec.ts`
- `exercises.spec.ts`
- `admin.spec.ts`

Etat terrain :

- parcours authentifies reels couverts sur Chromium pour `login`, `dashboard`, `badges`, `settings`
- pas de `globalSetup`
- pas de `storageState` partage par defaut
- helper principal : `__tests__/e2e/helpers/demoUserAuth.ts`

Reference :

- `./__tests__/README.md`
- `../docs/01-GUIDES/TESTING.md`

---

## Securite frontend

Points notables actuellement en place :

- CSP dynamique nonce-based sur `script-src` en production
- emission de la CSP dans `proxy.ts`
- `next.config.ts` ne porte plus la CSP statique
- `style-src 'unsafe-inline'` reste volontairement ouvert pour l'instant

Dette residuelle principale :

- nonce/hash uniquement sur `script-src`, pas encore sur les styles inline

---

## Contribution

Checklist minimale avant PR :

```bash
npm run lint
npx tsc --noEmit
npm run test
npm run i18n:validate
npm run i18n:check
```

Ajouter selon le lot :

- `npm run test:coverage`
- `npm run test:e2e`
- `npm run i18n:extract`
- `npm run build`

---

## Documentation utile

- `../README_TECH.md`
- `../.claude/session-plan.md`
- `../docs/04-FRONTEND/ARCHITECTURE.md`
- `../docs/04-FRONTEND/ACCESSIBILITY.md`
- `../docs/02-FEATURES/I18N.md`
- `../docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
- `../docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`

---

## Derniere mise a jour

`2026-04-10`
