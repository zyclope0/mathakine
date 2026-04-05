# Themes visuels - Mathakine

> Statut : reference active
> Updated : 2026-04-05
> Scope : theming produit visible, pas les archives

---

## Verite actuelle

Mathakine expose **8 themes visibles**, tous disponibles en mode clair et sombre :

| ID           | Libelle UI  | Direction                                         |
| ------------ | ----------- | ------------------------------------------------- |
| `spatial`    | Spatial     | Theme par defaut, univers sombre/violet           |
| `minimalist` | Minimaliste | Noir/blanc, contraste fort                        |
| `ocean`      | Ocean       | Bleus profonds, ambiance calme                    |
| `dune`       | Dune        | Tons sable et chaleur douce                       |
| `forest`     | Foret       | Verts nature                                      |
| `aurora`     | Aurore      | Palette chaude/florale, remplace l'ancien `peach` |
| `dino`       | Dinosaures  | Verts ludiques                                    |
| `unicorn`    | Licorne     | Pastels roses/violets                             |

**Theme par defaut :** `spatial`

---

## Source de verite code

- Store : `frontend/lib/stores/themeStore.ts`
- Variables CSS : `frontend/app/globals.css`
- Selecteur visible : `frontend/components/theme/ThemeSelectorCompact.tsx`
- Toggle clair/sombre : `frontend/components/theme/DarkModeToggle.tsx`
- Decor spatial : `frontend/components/spatial/SpatialBackground.tsx`

Le type TypeScript canonique est :

```ts
type Theme =
  | "spatial"
  | "minimalist"
  | "ocean"
  | "dune"
  | "forest"
  | "aurora"
  | "dino"
  | "unicorn";
```

---

## Migrations de compatibilite

Le store migre automatiquement les anciennes preferences :

- `neutral -> dune`
- `peach -> aurora`

La persistance reste `localStorage` via Zustand `persist`, cle `theme-preferences`.

---

## Application runtime

Le theme actif est applique sur `document.documentElement` via `data-theme`.

Pendant un changement de theme, la classe `html.theme-switching` coupe temporairement
les transitions globales pour eviter l'effet de couches colorees successives pendant
le passage clair/sombre ou theme -> theme.

---

## Tokens critiques

Chaque theme definit notamment :

- les tokens shadcn/ui de base (`--background`, `--foreground`, `--card`, `--primary`, etc.)
- les tokens graphiques (`--chart-1` a `--chart-5`)
- le token apprenant `--bg-learner`

`--bg-learner` existe bien pour les **16 variantes** :

- 8 themes light
- 8 themes dark

Il sert a la couche neuro-inclusive des surfaces apprenant (`LearnerCard`, `LearnerLayout`).

---

## Relation avec les animations

Le theming visible ne se limite pas aux couleurs :

- `Planet.tsx`, `Starfield.tsx` et `Particles.tsx` adaptent leurs couleurs au theme
- `DinoFloating.tsx` est actif uniquement sur `dino`
- `UnicornFloating.tsx` est actif uniquement sur `unicorn`

Voir aussi : [ANIMATIONS.md](../04-FRONTEND/ANIMATIONS.md)

---

## Checklist d'ajout d'un nouveau theme

1. Ajouter l'ID dans `themeStore.ts`
2. Ajouter les blocs CSS light + dark dans `globals.css`
3. Definir `--bg-learner`
4. Definir `--chart-1` a `--chart-5`
5. Ajouter le theme au selecteur compact
6. Si besoin, adapter les composants decoratifs (`Planet`, `Starfield`, `Particles`)
7. Verifier les contrastes et le rendu mobile

---

## Hors scope

Ce document ne gouverne pas :

- les anciens noms historiques dans les archives
- les roles utilisateur
- les rangs gamification
- la version produit visible

Pour les surfaces apprenant/adulte : [UX_SURFACES.md](../04-FRONTEND/UX_SURFACES.md)
