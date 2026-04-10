# Guide contribution i18n - Mathakine

> Scope : `frontend/messages/` + `frontend/scripts/i18n/`
> Updated : 2026-04-10

---

## Vue d'ensemble

Le frontend Mathakine est bilingue FR/EN via `next-intl`.

Source de verite :

- `frontend/messages/fr.json`
- `frontend/messages/en.json`

Les deux fichiers doivent rester strictement miroirs : meme structure, memes cles, memes profondeurs.

---

## Regles non negociables

1. Toute nouvelle cle est ajoutee en FR et en EN.
2. La structure JSON doit rester identique entre `fr.json` et `en.json`.
3. Le texte utilisateur visible ne doit pas etre hardcode dans les composants si le lot traite une surface i18nisee.
4. Utiliser `useTranslations()` ou un helper derive de `next-intl`.
5. Verification minimale avant commit sur un lot i18n cible :
   - `cd frontend && npm run i18n:validate`
   - `cd frontend && npm run i18n:check`
6. `npm run i18n:extract` et `npm run i18n:all` restent utiles comme audit global du repo, mais peuvent encore signaler des hardcodes hors du lot en cours.

---

## Namespaces

Namespaces actifs majeurs :

- `common`
- `auth`
- `navigation`
- `home`
- `dashboard`
- `exercises`
- `challenges`
- `badges`
- `settings`
- `profile`
- `errors`
- `toasts`
- `offline`
- `adminPages`
- `api`

Principe :

- utiliser un namespace domaine (`dashboard`, `exercises`, `adminPages.users`)
- garder des cles lisibles et stables
- eviter de multiplier les namespaces "temporaires"

---

## Procedure standard

### 1. Ajouter la cle en FR et EN

```jsonc
// fr.json
{
  "dashboard": {
    "stats": {
      "newLabel": "Nouveau libelle"
    }
  }
}

// en.json
{
  "dashboard": {
    "stats": {
      "newLabel": "New label"
    }
  }
}
```

### 2. Consommer la cle dans le composant

```tsx
import { useTranslations } from "next-intl";

export function DashboardStats() {
  const t = useTranslations("dashboard");

  return <span>{t("stats.newLabel")}</span>;
}
```

### 3. Valider le lot

```bash
cd frontend
npm run i18n:validate
npm run i18n:check
```

Option audit global :

```bash
cd frontend
npm run i18n:extract
# ou
npm run i18n:all
```

---

## Scripts disponibles

| Commande                | Usage recommande                                     |
| ----------------------- | ---------------------------------------------------- |
| `npm run i18n:validate` | verifier JSON, profondeur et valeurs                 |
| `npm run i18n:check`    | verifier l'alignement FR/EN                          |
| `npm run i18n:extract`  | audit global des hardcodes potentiels                |
| `npm run i18n:all`      | `validate + check + extract`, utile en revue globale |

---

## Chargement runtime

`frontend/components/providers/NextIntlProvider.tsx` charge aujourd'hui les messages FR et EN par imports statiques, puis selectionne le bon dictionnaire selon la locale Zustand.

Points utiles :

- locale par defaut : `fr`
- store : `frontend/lib/stores/localeStore.ts`
- synchronisation HTML `lang` : `NextIntlProvider` + `LocaleInitializer`

---

## Limitations connues

- `i18n:extract` peut encore remonter des hardcodes hors du lot courant.
- certaines surfaces residuelles ne sont pas encore totalement i18nisees, notamment le chrome de `frontend/app/admin/layout.tsx`.
- une chaine de succes register reste encore inline dans `frontend/hooks/useAuth.ts`.

---

## Troubleshooting

### `MISSING_MESSAGE`

- verifier que la cle existe dans `fr.json` et `en.json`
- verifier le namespace passe a `useTranslations(...)`
- verifier que la structure n'a pas diverge entre FR et EN

### Les scripts i18n ne trouvent pas les fichiers

Executer depuis `frontend/` :

```bash
cd frontend
npm run i18n:check
```

---

## References

- `frontend/messages/fr.json`
- `frontend/messages/en.json`
- `frontend/components/providers/NextIntlProvider.tsx`
- `frontend/scripts/i18n/README.md`
- `docs/02-FEATURES/I18N.md`
