# Animations Spatiales — Mathakine

> Dernière mise à jour : 22/02/2026  
> Composants dans `frontend/components/spatial/`

Système d'animations d'arrière-plan pour l'immersion visuelle. S'adaptent aux 7 thèmes et respectent toutes les préférences d'accessibilité (Focus Mode, reduced motion).

---

## Composants

### `SpatialBackground`

Conteneur orchestrateur — inclut tous les composants ci-dessous. Intégré dans `app/layout.tsx` pour être présent sur toutes les pages.

```tsx
import { SpatialBackground } from "@/components/spatial/SpatialBackground";
// Intégré dans app/layout.tsx — rien à faire dans les pages
```

---

### `Starfield` — z-index `-10`

Champ d'étoiles multi-couches avec effet de profondeur (canvas + `requestAnimationFrame`).

| Couche | Étoiles | Vitesse | Taille | Opacité |
|---|---|---|---|---|
| Lointaine | 100 | 0.5 | 1px | 0.8 |
| Moyenne | 150 | 1.0 | 1.5px | 0.6 |
| Proche | 200 | 2.0 | 2px | 0.4 |

```tsx
// Modifier le nombre d'étoiles
// components/spatial/Starfield.tsx
const layers = [
  { count: 100, speed: 0.5, size: 1, opacity: 0.8 },
  // ...
];
```

---

### `Planet` — z-index `-5`

Planète rotative (0.5°/frame) avec cratères 3D et 6 symboles mathématiques en orbite (∑∫π∞√Δ, rotation 20s). Sur le thème Dinosaures, remplacée par un T-Rex emoji.

```tsx
// Modifier la vitesse de rotation
// components/spatial/Planet.tsx
const rotationSpeed = 0.5; // degrés par frame
```

---

### `Particles` — z-index `-8`

50 particules flottantes avec rebond sur les bords, opacité et taille variables.

```tsx
// Modifier le nombre de particules
// components/spatial/Particles.tsx
const particleCount = 50;
```

---

### `DinoFloating` — z-index `-5`

Emoji 🦕 flottant en haut à gauche — **visible uniquement avec le thème Dinosaures**. Animation `dino-bob` (balancement doux).

---

## Adaptation aux 7 thèmes

| Thème | Étoiles | Planète | Particules | Spécial |
|---|---|---|---|---|
| Spatial | Blanc brillant | Violet | Violet subtil | — |
| Minimaliste | Noir | Noir | Noir subtil | — |
| Océan | Blanc brillant | Bleu ciel | Bleu subtil | — |
| Dune | Ambre/Sable | Ambre | Ambre subtil | — |
| Forêt | Blanc | Vert menthe | Vert subtil | — |
| Lumière | Blanc | Pêche/Orange | Pêche subtil | — |
| Dinosaures | Vert lime | T-Rex emoji | Vert lime | DinoFloating actif |

---

## Accessibilité

Tous les composants vérifient au rendu :
```tsx
// Retourne null si focus mode ou reduced motion actif
if (focusMode || reducedMotion) return null;
```

- **Mode Focus TSA/TDAH** (`Alt+F`) : tous désactivés → `null`
- **Reduced Motion** (store ou `prefers-reduced-motion`) : tous désactivés → `null`
- **Performance** : canvas avec `clearRect` propre, nettoyage des event listeners au démontage

---

## Animations CSS (`app/globals.css`)

```css
@keyframes pulse-ring { /* Anneau planète */ }
@keyframes orbit-0 { /* ∑ */ }
@keyframes orbit-1 { /* ∫ */ }
@keyframes orbit-2 { /* π */ }
@keyframes orbit-3 { /* ∞ */ }
@keyframes orbit-4 { /* √ */ }
@keyframes orbit-5 { /* Δ */ }
@keyframes dino-bob { /* Dinosaure flottant */ }
```

Durée orbites : 20s, easing : `linear`.

---

## Ajouter un nouveau thème

1. **`Starfield.tsx`** — ajouter dans `starColors` :
```tsx
const starColors: Record<string, string> = {
  // thèmes existants...
  nouveauTheme: "rgba(R, G, B, ",
};
```

2. **`Planet.tsx`** — ajouter dans `planetColors` :
```tsx
const planetColors: Record<string, { bg: string; glow: string }> = {
  nouveauTheme: {
    bg: "radial-gradient(...)",
    glow: "rgba(...)",
  },
};
```

3. **`Particles.tsx`** — ajouter dans `themeColors` :
```tsx
const themeColors: Record<string, string> = {
  nouveauTheme: "rgba(R, G, B, 0.3)",
};
```

> Voir aussi [Thèmes](../02-FEATURES/THEMES.md) pour la procédure complète d'ajout de thème (CSS variables + themeStore).

---

## Ordre z-index

```
-10 : Starfield       (arrière-plan)
 -8 : Particles       (milieu)
 -5 : Planet, DinoFloating (avant-plan décoratif)
  0+: Contenu principal
```

---

## Évolutions possibles

- Étoiles filantes occasionnelles
- Variation des tailles des symboles orbitants
- Effets de brillance (scintillement) sur les étoiles
- Optimisation mobile (réduire le count de particules/étoiles sur petit écran)
