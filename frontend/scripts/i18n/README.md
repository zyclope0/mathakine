# Scripts i18n - Verification automatique

Updated : 2026-04-10

Scripts de verification pour les messages FR/EN du frontend.

---

## Scripts disponibles

### `npm run i18n:validate`

Valide :

- syntaxe JSON
- profondeur des cles
- valeurs vides
- structure generale des fichiers

### `npm run i18n:check`

Verifie :

- memes cles en FR et EN
- structure identique
- absence de cles orphelines

### `npm run i18n:extract`

Audit global :

- scanne le code pour detecter des hardcodes probables
- genere `hardcoded-texts-report.json`
- peut remonter des points hors du lot courant

### `npm run i18n:all`

Enchaine :

1. `i18n:validate`
2. `i18n:check`
3. `i18n:extract`

---

## Usage recommande

### Verification minimale avant commit pour un lot i18n cible

```bash
cd frontend
npm run i18n:validate
npm run i18n:check
```

### Audit global ponctuel

```bash
cd frontend
npm run i18n:all
```

ou

```bash
cd frontend
npm run i18n:extract
```

Important :

- `i18n:all` n'est pas toujours un gate strict de lot, car `extract` peut signaler des hardcodes non traites ailleurs dans le repo
- pour une cloture de lot scope, `validate` + `check` sont la base fiable

---

## Workflow

1. ajouter ou modifier les cles dans `frontend/messages/fr.json`
2. mirrorer la structure dans `frontend/messages/en.json`
3. brancher la cle via `useTranslations(...)`
4. lancer `i18n:validate`
5. lancer `i18n:check`
6. lancer `i18n:extract` si tu veux un audit global plus large

---

## Documentation

- `../../docs/02-FEATURES/I18N.md`
- `../../docs/01-GUIDES/I18N_CONTRIBUTION.md`

---

## Troubleshooting

### `Cannot find module`

Executer les scripts depuis `frontend/` :

```bash
cd frontend
npm run i18n:check
```

### `SyntaxError` JSON

```bash
cd frontend
npm run i18n:validate
```
