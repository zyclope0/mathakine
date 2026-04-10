# ESLint et Prettier — Frontend Mathakine

## Vue d’ensemble

Le frontend utilise **ESLint** (lint) et **Prettier** (formatage) pour garder un style de code cohérent et limiter les erreurs courantes.

## Configuration

### ESLint

- **Config** : `eslint.config.mjs` (flat config)
- **Extensions** : `eslint-config-next` (règles Next.js / TypeScript / React)
- **Complément** : `eslint-config-prettier` pour éviter les conflits avec Prettier
- **Cible** : tout le dossier `frontend/` (`.next`, `node_modules`, etc. exclus)

### Prettier

- **Config** : `.prettierrc`
- **Options** :
  - `semi: true`
  - `singleQuote: false`
  - `tabWidth: 2`
  - `trailingComma: "es5"`
  - `printWidth: 100`
- **Ignores** : `.prettierignore` (`.next`, `node_modules`, lockfiles, etc.)

## Scripts npm

| Script                 | Commande             | Description                                |
| ---------------------- | -------------------- | ------------------------------------------ |
| `npm run lint`         | `eslint .`           | Analyse le code avec ESLint                |
| `npm run format`       | `prettier --write .` | Formate tout le code avec Prettier         |
| `npm run format:check` | `prettier --check .` | Vérifie que le code respecte Prettier (CI) |

## Workflow recommandé

1. **Avant un commit** : `npm run lint` et `npm run format:check`
2. **Correction auto du format** : `npm run format`
3. **CI** : exécuter `npm run lint` et `npm run format:check` en mode strict

## Première mise en forme du projet

Pour formater tout le code existant avec Prettier :

```bash
cd frontend
npm run format
```

Ensuite, vérifier le lint :

```bash
npm run lint
```

## Stratégie pour les problèmes ESLint

Le front a été durci par les lots `QF-04`, `QF-04B` et `QF-04C` :

1. `@typescript-eslint/no-unused-vars` → `error`
2. `@typescript-eslint/no-require-imports` → `error`
3. `@typescript-eslint/consistent-type-imports` → `error`
4. `@typescript-eslint/no-floating-promises` → `error` avec lint typé (`projectService`)
5. `react-hooks/exhaustive-deps` → `error`
6. `react-hooks/set-state-in-effect` → `error`
7. `react-hooks/preserve-manual-memoization` → `error`

Les suppressions locales restantes doivent rester rares, ciblées et justifiées dans le fichier concerné.

## Format on save (IDE)

Pour formater automatiquement à l’enregistrement, active « Format on Save » et définis Prettier comme formateur par défaut pour JS/TS/CSS/JSON.  
Exemple VS Code / Cursor : `"editor.formatOnSave": true` + `"editor.defaultFormatter": "esbenp.prettier-vscode"`.

## Désactiver une règle

- **Global** : dans `eslint.config.mjs`, via un bloc `rules`
- **Ligne** : `// eslint-disable-next-line rule-name`
- **Bloc** : `/* eslint-disable rule-name */` … `/* eslint-enable rule-name */`

## Fichiers concernés

- `frontend/eslint.config.mjs` — configuration ESLint
- `frontend/.prettierrc` — configuration Prettier
- `frontend/.prettierignore` — exclusions Prettier
- `frontend/package.json` — scripts et dépendances
