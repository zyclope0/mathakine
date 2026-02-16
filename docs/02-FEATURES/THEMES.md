# Thèmes visuels — Mathakine

> 7 thèmes personnalisables, mode clair/sombre  
> **Date :** 15/02/2026

---

## Vue d'ensemble

| ID | Nom | Style | Palette principale |
|----|-----|-------|--------------------|
| `spatial` | Spatial | Sombre, violet | `#7c3aed`, `#0a0a0f` |
| `minimalist` | Minimaliste | Clair/sombre, noir & blanc | `#000`, `#fff` |
| `ocean` | Océan | Bleu profond | `#0369a1`, `#0c1220` |
| `dune` | Dune | Sable, chaud | `#b45309`, `#fef7ed` |
| `forest` | Forêt | Verts nature | `#047857`, `#f0fdf4` |
| `peach` | Lumière (Pêche) | Tons chauds | `#ea580c`, `#fff7ed` |
| `dino` | Dinosaures | Lime, jungle préhistorique | `#65a30d`, `#fef9c3` |

**Thème par défaut :** `spatial`

---

## Architecture

```
frontend/
├── app/globals.css           # Variables CSS [data-theme="xxx"]
├── lib/stores/themeStore.ts  # Zustand + persist localStorage
├── components/
│   └── spatial/              # Animations adaptées aux thèmes
│       ├── Planet.tsx        # Thème dino → emoji T-Rex
│       ├── DinoFloating.tsx  # Visible uniquement thème dino
│       ├── Starfield.tsx
│       ├── Particles.tsx
│       └── SpatialBackground.tsx
└── (ThemeSelector dans settings/header)
```

**Persistance :** `localStorage` via Zustand `persist` (clé `theme-preferences`).

**Application :** `document.documentElement.setAttribute("data-theme", theme)`.

---

## Utilisation côté code

```tsx
import { useThemeStore } from "@/lib/stores/themeStore";

function MyComponent() {
  const { theme, setTheme } = useThemeStore();

  // Changer de thème
  setTheme("ocean");

  // Lire le thème actuel
  console.log(theme); // "spatial" | "minimalist" | ...
}
```

**Type TypeScript :** `Theme = "spatial" | "minimalist" | "ocean" | "dune" | "forest" | "peach" | "dino"`

---

## Ajouter un nouveau thème

### 1. themeStore.ts

```ts
// Ajouter l'ID dans le type et le tableau valid
export type Theme = "spatial" | ... | "nouveau";
const valid: Theme[] = ["spatial", ..., "nouveau"];
```

### 2. globals.css

```css
[data-theme="nouveau"] {
  --background: #ffffff;
  --foreground: #000000;
  --primary: #...;
  /* ... toutes les variables (voir THEMES_INDUSTRIALIZATION) */
}

.dark[data-theme="nouveau"] {
  /* Variante dark obligatoire */
}
```

### 3. Composants spécifiques (optionnel)

Si le thème a des éléments décoratifs particuliers (ex. DinoFloating pour dino) :
- `Planet.tsx` — palette couleur planète
- `Starfield.tsx`, `Particles.tsx` — couleurs
- Nouveau composant conditionnel si besoin

### 4. ThemeSelector / ThemeSelectorCompact

Ajouter l'entrée dans la liste des thèmes proposés à l'utilisateur.

---

## Migration (neutral → dune)

Les utilisateurs avec l'ancien thème `neutral` (obsolète) sont migrés automatiquement vers `dune` au chargement via `onRehydrateStorage` du store.

---

## Règles WCAG

- **Muted-foreground** : contraste ≥ 7:1 avec background (WCAG AAA)
- **Primary** : contraste ≥ 4.5:1 avec primary-foreground (WCAG AA)
- Chaque thème a une variante **dark** pour `.dark[data-theme="..."]`

---

## Documents complémentaires

| Document | Rôle |
|----------|------|
| [THEMES_INDUSTRIALIZATION.md](../../frontend/docs/THEMES_INDUSTRIALIZATION.md) | Standard création, checklist, variables CSS |
| [SPATIAL_ANIMATIONS.md](../../frontend/docs/SPATIAL_ANIMATIONS.md) | Planet, Starfield, DinoFloating, couleurs par thème |
