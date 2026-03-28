# Guide contribution i18n — Mathakine

> Scope : `frontend/messages/` + `frontend/scripts/i18n/`
> Updated : 2026-03-27

---

## Vue d'ensemble

Mathakine est bilingue FR/EN via **next-intl**. Les traductions sont dans deux fichiers JSON miroirs :

```
frontend/messages/
├── fr.json   ← source de vérité (langue de rédaction)
└── en.json   ← miroir obligatoire (même structure exacte)
```

**Namespaces actifs** (25 sections) :
`common`, `progressionRanks`, `auth`, `diagnostic`, `onboarding`, `navigation`, `exercises`, `challenges`, `dashboard`, `badges`, `leaderboard`, `accessibility`, `theme`, `errors`, `toasts`, `home`, `profile`, `settings`, `docs`, `about`, `contact`, `privacy`, `changelog`, `feedback`, `api`

---

## Règles

1. **Toujours ajouter la clé dans les deux fichiers** (FR + EN) au même endroit.
2. **Profondeur maximale : 3 niveaux** (`namespace.section.key`).
3. **Nommer dans le namespace approprié** — voir tableau ci-dessous.
4. **Pas de texte français hardcodé** dans les `.tsx` / `.ts` — utiliser `useTranslations()`.
5. **Toujours vérifier avant commit** : `npm run i18n:all`.

---

## Mapping namespace → domaine

| Namespace | Domaine | Exemple de clé |
|-----------|---------|----------------|
| `common` | Libellés génériques réutilisables | `common.save`, `common.cancel` |
| `auth` | Login, register, reset password | `auth.login.title` |
| `exercises` | Page exercices, cartes, génération | `exercises.card.difficulty` |
| `challenges` | Page défis, génération IA | `challenges.filter.type` |
| `dashboard` | Stats, widgets, export | `dashboard.stats.streak` |
| `badges` | Noms et descriptions de badges | `badges.daily_streak.name` |
| `leaderboard` | Classement | `leaderboard.rank` |
| `progressionRanks` | Noms des 8 rangs publics | `progressionRanks.explorer` |
| `navigation` | Menu, breadcrumbs | `navigation.home` |
| `toasts` | Messages toast (succès/erreur) | `toasts.exercise.submitted` |
| `errors` | Messages d'erreur génériques | `errors.network` |
| `profile` | Page profil utilisateur | `profile.edit.username` |
| `settings` | Paramètres compte | `settings.notifications` |
| `accessibility` | Labels ARIA, préférences a11y | `accessibility.fontSize` |
| `theme` | Noms de thèmes | `theme.spatial` |
| `onboarding` | Flux d'onboarding pédagogique | `onboarding.step1.title` |
| `home` | Page d'accueil | `home.hero.cta` |
| `feedback` | Formulaire de feedback | `feedback.submit` |
| `api` | Messages d'erreur API exposés côté client | `api.rateLimit` |

---

## Procédure standard

### 1. Ajouter une nouvelle clé

```jsonc
// fr.json — ajouter dans le namespace approprié
{
  "exercises": {
    "card": {
      "difficulty": "Difficulté",
      "newKey": "Nouveau libellé"     // ← ajouté
    }
  }
}

// en.json — même position, même structure
{
  "exercises": {
    "card": {
      "difficulty": "Difficulty",
      "newKey": "New label"           // ← ajouté
    }
  }
}
```

### 2. Utiliser dans un composant

```tsx
import { useTranslations } from "next-intl";

export function ExerciseCard() {
  const t = useTranslations("exercises");
  return <span>{t("card.newKey")}</span>;
}
```

### 3. Vérifier avant commit

```bash
cd frontend
npm run i18n:all
# Exécute dans l'ordre : validate → check → extract
```

---

## Scripts disponibles

| Commande | Action |
|----------|--------|
| `npm run i18n:check` | Vérifie la cohérence clés FR ↔ EN |
| `npm run i18n:validate` | Valide syntaxe JSON, profondeur, valeurs vides |
| `npm run i18n:extract` | Détecte les textes français hardcodés dans le code |
| `npm run i18n:all` | Les trois en séquence (à lancer avant chaque commit) |

### Sortie attendue (tout OK)

```
✅ Toutes les traductions sont cohérentes !
   - 281 clés vérifiées
   - Structure identique entre FR et EN

✅ Structure valide et cohérente !
```

### Sortie avec erreur

```
❌ Clés manquantes en EN :
   - exercises.card.newKey

Rapport généré : hardcoded-texts-report.json
```

---

## Chargement runtime

`frontend/components/locale/LocaleInitializer.tsx` synchronise la locale détectée (cookie `NEXT_LOCALE` ou préférence navigateur) avec le store Zustand (`localeStore`) au montage.

La locale par défaut est `fr`. Pour basculer en `en`, utiliser le `LanguageSelector` en header.

---

## Limitations connues

- Pas de pluralisation complexe : les clés de comptage sont gérées manuellement (`"1 exercice"` / `"N exercices"`).
- Pas de traductions pour les contenus dynamiques (titres d'exercices, énoncés) — ils restent dans la langue de création.
- `i18n:extract` génère des faux positifs sur les chaînes contenant des accents dans les commentaires de code.

---

## Troubleshooting

### `Cannot find module` à l'exécution des scripts

```bash
# Toujours exécuter depuis frontend/
cd frontend
npm run i18n:check
```

### Clé présente en FR mais absente en EN après ajout

Vérifier que la structure JSON est identique (même imbrication, même parent). `i18n:check` liste exactement les clés manquantes.
