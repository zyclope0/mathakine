# 🌌 Animations Spatiales - Documentation

**Date** : Janvier 2025  
**Status** : ✅ **Complété**

---

## 📋 **Vue d'Ensemble**

Système d'animations spatiales modérées pour créer une immersion visuelle cohérente avec le thème Mathakine. Les animations s'adaptent automatiquement aux 4 thèmes disponibles et respectent les préférences d'accessibilité.

---

## 🎨 **Composants Créés**

### **1. Starfield** (`components/spatial/Starfield.tsx`)

**Description** : Système d'étoiles multi-couches avec effet de profondeur.

**Fonctionnalités** :
- ✅ 3 couches d'étoiles avec vitesses différentes :
  - Couche lointaine : 100 étoiles, vitesse 0.5, taille 1px, opacité 0.8
  - Couche moyenne : 150 étoiles, vitesse 1, taille 1.5px, opacité 0.6
  - Couche proche : 200 étoiles, vitesse 2, taille 2px, opacité 0.4
- ✅ Couleurs adaptées aux 4 thèmes :
  - **Spatial** : Blanc (`rgba(255, 255, 255)`)
  - **Minimaliste** : Noir (`rgba(0, 0, 0)`)
  - **Océan** : Blanc (`rgba(255, 255, 255)`)
  - **Neutre** : Gris (`rgba(107, 114, 128)`)
- ✅ Animation fluide avec `requestAnimationFrame`
- ✅ Responsive (s'adapte à la taille de l'écran)
- ✅ Désactivation automatique en mode Focus ou reduced motion

**Z-index** : `-10` (arrière-plan)

---

### **2. Planet** (`components/spatial/Planet.tsx`)

**Description** : Planète rotative avec cratères 3D et symboles mathématiques orbitants.

**Fonctionnalités** :
- ✅ Planète rotative (0.5° par frame)
- ✅ 3 cratères 3D avec effets d'ombre
- ✅ Anneau pulsant autour de la planète (animation `pulse-ring`)
- ✅ 6 symboles mathématiques orbitants : **∑∫π∞√Δ**
- ✅ Animations orbitales individuelles (20s par rotation)
- ✅ Couleurs adaptées aux 4 thèmes :
  - **Spatial** : Violet (`rgba(139, 92, 246)`)
  - **Minimaliste** : Noir (`rgba(0, 0, 0)`)
  - **Océan** : Bleu ciel (`rgba(14, 165, 233)`)
  - **Neutre** : Gris (`rgba(107, 114, 128)`)
- ✅ Désactivation automatique en mode Focus ou reduced motion

**Position** : `fixed bottom-8 right-8`  
**Z-index** : `-5` (devant le starfield)

---

### **3. Particles** (`components/spatial/Particles.tsx`)

**Description** : Système de particules subtiles en arrière-plan.

**Fonctionnalités** :
- ✅ 50 particules flottantes
- ✅ Mouvement aléatoire (rebond sur les bords)
- ✅ Couleurs adaptées aux 4 thèmes :
  - **Spatial** : Violet (`rgba(139, 92, 246, 0.3)`)
  - **Minimaliste** : Noir subtil (`rgba(0, 0, 0, 0.2)`)
  - **Océan** : Bleu ciel (`rgba(14, 165, 233, 0.3)`)
  - **Neutre** : Gris (`rgba(107, 114, 128, 0.2)`)
- ✅ Opacité variable par particule (0.2-0.7)
- ✅ Taille variable (1-3px)
- ✅ Désactivation automatique en mode Focus ou reduced motion

**Z-index** : `-8` (entre starfield et planète)

---

### **4. SpatialBackground** (`components/spatial/SpatialBackground.tsx`)

**Description** : Conteneur combinant tous les composants spatiaux.

**Fonctionnalités** :
- ✅ Combine `Starfield`, `Planet`, et `Particles`
- ✅ Intégré dans `app/layout.tsx` pour toutes les pages
- ✅ S'adapte automatiquement au thème et aux préférences d'accessibilité

---

## 🎯 **Adaptation aux Thèmes**

### **Thème Spatial** 🚀
- Étoiles : Blanc brillant
- Planète : Violet spatial avec brillance violette
- Particules : Violet subtil

### **Thème Minimaliste** ⚪
- Étoiles : Noir (visible sur fond clair)
- Planète : Noir avec brillance noire
- Particules : Noir subtil

### **Thème Océan** 🌊
- Étoiles : Blanc brillant
- Planète : Bleu ciel avec brillance bleue
- Particules : Bleu ciel subtil

### **Thème Neutre** ⚫
- Étoiles : Gris
- Planète : Gris avec brillance grise
- Particules : Gris subtil

---

## ♿ **Accessibilité**

### **Respect des Préférences**

1. **Mode Focus TSA/TDAH** :
   - ✅ Toutes les animations sont désactivées automatiquement
   - ✅ Les composants retournent `null` si `focusMode === true`

2. **Reduced Motion** :
   - ✅ Désactivation automatique si `reducedMotion === true`
   - ✅ Respect de `prefers-reduced-motion` via CSS

3. **Performance** :
   - ✅ Utilisation de `requestAnimationFrame` pour animations fluides
   - ✅ Nettoyage propre des event listeners et animations
   - ✅ Canvas optimisé avec `clearRect` pour éviter les fuites mémoire

---

## 📐 **Animations CSS**

### **Animations Définies** (`app/globals.css`)

```css
/* Anneau pulsant de la planète */
@keyframes pulse-ring {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 0.1; }
}

/* Orbites des symboles mathématiques */
@keyframes orbit-0 { /* ∑ */ }
@keyframes orbit-1 { /* ∫ */ }
@keyframes orbit-2 { /* π */ }
@keyframes orbit-3 { /* ∞ */ }
@keyframes orbit-4 { /* √ */ }
@keyframes orbit-5 { /* Δ */ }
```

**Durée** : 20 secondes par rotation complète  
**Easing** : `linear` (mouvement constant)

---

## 🔧 **Intégration**

### **Layout Principal**

```typescript
// app/layout.tsx
import { SpatialBackground } from "@/components/spatial/SpatialBackground";

<Providers>
  <SpatialBackground />
  {/* ... autres composants ... */}
</Providers>
```

### **Ordre de Z-index**

```
-10 : Starfield (arrière-plan)
-8  : Particles (milieu)
-5  : Planet (avant-plan)
0+  : Contenu principal
```

---

## ✅ **Checklist de Validation**

- [x] **Starfield** : 3 couches fonctionnelles
- [x] **Planet** : Rotation + cratères + symboles orbitants
- [x] **Particles** : Système de particules subtiles
- [x] **Adaptation thèmes** : 4 thèmes supportés
- [x] **Accessibilité** : Mode Focus et reduced motion respectés
- [x] **Performance** : Animations fluides avec requestAnimationFrame
- [x] **Responsive** : S'adapte à toutes les tailles d'écran
- [x] **Intégration** : Ajouté dans layout.tsx

---

## 🎨 **Personnalisation**

### **Modifier le Nombre d'Étoiles**

```typescript
// components/spatial/Starfield.tsx
const layers = [
  { count: 100, speed: 0.5, size: 1, opacity: 0.8 }, // Modifier count
  // ...
];
```

### **Modifier la Vitesse de Rotation de la Planète**

```typescript
// components/spatial/Planet.tsx
const rotationSpeed = 0.5; // Modifier cette valeur (degrés par frame)
```

### **Modifier le Nombre de Particules**

```typescript
// components/spatial/Particles.tsx
const particleCount = 50; // Modifier cette valeur
```

### **Ajouter un Nouveau Thème**

1. Ajouter les couleurs dans `Starfield.tsx` :
```typescript
const starColors: Record<string, string> = {
  // ... thèmes existants
  nouveauTheme: 'rgba(..., ..., ..., ',
};
```

2. Ajouter les couleurs dans `Planet.tsx` :
```typescript
const planetColors: Record<string, { bg: string; glow: string }> = {
  // ... thèmes existants
  nouveauTheme: {
    bg: 'radial-gradient(...)',
    glow: 'rgba(...)',
  },
};
```

3. Ajouter les couleurs dans `Particles.tsx` :
```typescript
const themeColors: Record<string, string> = {
  // ... thèmes existants
  nouveauTheme: 'rgba(..., ..., ..., 0.3)',
};
```

---

## 🚀 **Prochaines Améliorations Possibles**

- [ ] Ajouter des étoiles filantes occasionnelles
- [ ] Varier les tailles des symboles orbitants
- [ ] Ajouter des effets de brillance sur les étoiles
- [ ] Optimiser pour mobile (réduire le nombre d'éléments)

---

**Dernière mise à jour** : Janvier 2025  
**Maintenu par** : Équipe Frontend Mathakine

