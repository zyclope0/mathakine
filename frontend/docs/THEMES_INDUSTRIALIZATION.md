# 🎨 Guide d'Industrialisation et Standardisation des Thèmes

**Date** : Janvier 2025  
**Objectif** : Standardiser la création et la maintenance des thèmes pour faciliter l'ajout de nouveaux thèmes

---

## 📋 **Structure Actuelle**

### **Thèmes Disponibles**

1. **Spatial** (`spatial`) - Thème par défaut, sombre avec couleurs violettes
2. **Minimaliste** (`minimalist`) - Thème clair/sombre avec inversion complète
3. **Océan** (`ocean`) - Thème sombre avec couleurs bleues/cyan
4. **Neutre** (`neutral`) - Thème clair/sombre avec gris élégants

### **Architecture**

```
frontend/
├── app/
│   └── globals.css              # Définition des thèmes et variantes dark
├── components/
│   └── theme/
│       ├── ThemeSelector.tsx           # Sélecteur complet
│       ├── ThemeSelectorCompact.tsx    # Sélecteur compact (header)
│       └── DarkModeToggle.tsx          # Toggle clair/sombre
├── lib/
│   └── stores/
│       └── themeStore.ts       # Store Zustand pour gestion état
└── docs/
    └── THEMES_INDUSTRIALIZATION.md  # Ce document
```

---

## 🎯 **Standard de Création d'un Thème**

### **1. Définition CSS (globals.css)**

Chaque thème doit définir **toutes** les variables CSS suivantes :

```css
/* Thème [Nom] - Mode Normal */
[data-theme='theme-id'] {
  /* Couleurs de base */
  --background: #ffffff;           /* Fond principal */
  --foreground: #000000;           /* Texte principal */
  --card: #f5f5f5;                 /* Fond des cartes */
  --card-foreground: #000000;      /* Texte sur cartes */
  --popover: #ffffff;              /* Fond des popovers */
  --popover-foreground: #000000;   /* Texte sur popovers */
  
  /* Couleurs primaires */
  --primary: #000000;              /* Couleur principale */
  --primary-foreground: #ffffff;   /* Texte sur primary */
  --primary-light: #333333;        /* Variante claire (optionnel) */
  --primary-text-on-dark: #cccccc; /* Primary sur fond sombre */
  
  /* Couleurs secondaires */
  --secondary: #666666;
  --secondary-foreground: #ffffff;
  
  /* Couleurs d'accentuation */
  --accent: #000000;
  --accent-foreground: #ffffff;
  
  /* Couleurs muettes */
  --muted: #f5f5f5;
  --muted-foreground: #4a4a4a;     /* WCAG AAA : >= 7:1 */
  
  /* Couleurs d'état */
  --destructive: #ef4444;
  --success: #22c55e;              /* Optionnel */
  --warning: #f59e0b;              /* Optionnel */
  --info: #3b82f6;                 /* Optionnel */
  
  /* Bordures et inputs */
  --border: #000000;
  --input: #f5f5f5;
  --ring: #000000;                 /* Couleur du focus ring */
  
  /* Rayon de bordure */
  --radius: 0.625rem;              /* 10px par défaut */
}
```

### **2. Variante Dark Mode (obligatoire)**

Chaque thème **doit** avoir une variante dark mode :

```css
/* Thème [Nom] - Mode Dark */
.dark [data-theme='theme-id'] {
  /* Modifier les variables nécessaires */
  --background: #000000;
  --foreground: #ffffff;
  --card: #1a1a1a;
  /* ... autres modifications */
  
  /* Toujours améliorer le contraste en dark mode */
  --muted-foreground: #cccccc;     /* Plus clair pour meilleur contraste */
  --border: rgba(255, 255, 255, 0.3); /* Plus visible */
}
```

### **3. Checklist de Validation**

Avant de considérer un thème comme complet, vérifier :

- [ ] **Toutes les variables CSS définies** (voir liste ci-dessus)
- [ ] **Variante dark mode créée** avec `.dark [data-theme='...']`
- [ ] **Contraste WCAG AAA** : `--muted-foreground` >= 7:1 avec `--background`
- [ ] **Contraste WCAG AA** : `--primary` >= 4.5:1 avec `--primary-foreground`
- [ ] **Test visuel** : Utiliser `/themes-test` pour vérifier tous les composants
- [ ] **Documentation** : Ajouter le thème dans `ThemeSelector.tsx` et `ThemeSelectorCompact.tsx`

---

## 🔧 **Processus d'Ajout d'un Nouveau Thème**

### **Étape 1 : Définir le thème dans globals.css**

```css
/* Thème NouveauThème */
[data-theme='nouveau-theme'] {
  /* Copier la structure d'un thème existant et modifier les couleurs */
  --background: #...;
  /* ... */
}

/* Thème NouveauThème - Mode Dark */
.dark [data-theme='nouveau-theme'] {
  /* Définir les variantes dark */
  /* ... */
}
```

### **Étape 2 : Ajouter au store TypeScript**

```typescript
// lib/stores/themeStore.ts
export type Theme = 'spatial' | 'minimalist' | 'ocean' | 'neutral' | 'nouveau-theme';
```

### **Étape 3 : Ajouter aux sélecteurs**

```typescript
// components/theme/ThemeSelectorCompact.tsx
const themes = [
  // ... thèmes existants
  { id: 'nouveau-theme' as const, name: 'Nouveau Thème', icon: '🎨' },
] as const;
```

### **Étape 4 : Tester**

1. Aller sur `/themes-test`
2. Sélectionner le nouveau thème
3. Tester avec dark mode activé/désactivé
4. Vérifier tous les composants (boutons, cards, inputs, badges)
5. Vérifier les contrastes avec les outils de développement

### **Étape 5 : Documenter**

Ajouter une entrée dans ce document avec :
- Description du thème
- Couleurs principales
- Cas d'usage recommandé

---

## 📐 **Règles de Contraste WCAG**

### **WCAG 2.1 AA (Minimum requis)**

- **Texte normal** : Ratio >= 4.5:1
- **Texte large** (>= 18pt ou >= 14pt bold) : Ratio >= 3:1

### **WCAG 2.1 AAA (Recommandé)**

- **Texte normal** : Ratio >= 7:1
- **Texte large** : Ratio >= 4.5:1

### **Variables à vérifier**

| Variable | Contraste requis | Contre |
|----------|------------------|--------|
| `--foreground` | >= 7:1 (AAA) | `--background` |
| `--muted-foreground` | >= 7:1 (AAA) | `--background` |
| `--primary` | >= 4.5:1 (AA) | `--primary-foreground` |
| `--card-foreground` | >= 7:1 (AAA) | `--card` |

### **Outils de vérification**

- Chrome DevTools : Lighthouse → Accessibility
- Extension : WAVE (Web Accessibility Evaluation Tool)
- En ligne : [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

## 🎨 **Palettes de Couleurs Recommandées**

### **Thème Sombre (comme Spatial/Océan)**

```css
--background: #0a0a0f à #0c1220;    /* Fond très sombre */
--foreground: #ffffff à #f1f5f9;    /* Texte clair */
--card: #12121a à #1e293b;          /* Cartes légèrement plus claires */
--muted-foreground: #c0c0c0 à #cbd5e1; /* Texte secondaire clair */
```

### **Thème Clair (comme Minimaliste/Neutre)**

```css
--background: #ffffff;               /* Fond blanc */
--foreground: #000000 à #111827;    /* Texte sombre */
--card: #f5f5f5 à #f9fafb;          /* Cartes gris très clair */
--muted-foreground: #4a4a4a à #4b5563; /* Texte secondaire sombre */
```

### **Couleurs Primaires Recommandées**

- **Violet/Pourpre** : `#7c3aed` (Spatial)
- **Noir** : `#000000` (Minimaliste)
- **Bleu** : `#0369a1` à `#0ea5e9` (Océan)
- **Gris** : `#6b7280` à `#9ca3af` (Neutre)

---

## 🔄 **Synchronisation Dark Mode ↔ Thèmes**

### **Architecture Actuelle**

1. **DarkModeToggle** : Ajoute/enlève la classe `.dark` sur `document.documentElement`
2. **ThemeStore** : Gère `data-theme` sur `document.documentElement`
3. **CSS** : Les variantes dark sont activées via `.dark [data-theme='...']`

### **Règles de Synchronisation**

- Le dark mode est **indépendant** du thème choisi
- Chaque thème peut avoir un dark mode différent
- Le dark mode est **persisté** dans `localStorage` (`dark-mode`)
- Le thème est **persisté** dans `localStorage` (`theme-preferences`)

### **Comportement Attendu**

- Changer de thème → Le dark mode reste actif/inactif selon la préférence
- Activer dark mode → Les variantes dark du thème actuel s'appliquent
- Les deux toggles fonctionnent **indépendamment** mais **ensemble**

---

## 🧪 **Tests et Validation**

### **Page de Test**

Une page dédiée `/themes-test` permet de :
- Voir tous les thèmes côte à côte
- Tester chaque composant avec chaque thème
- Basculer entre dark/light mode
- Vérifier visuellement les contrastes

### **Tests Automatisés (À venir)**

```typescript
// __tests__/themes/theme-contrast.test.ts
describe('Theme Contrast', () => {
  it('should have WCAG AAA contrast for muted-foreground', () => {
    // Vérifier que chaque thème respecte les ratios
  });
});
```

### **Checklist de Validation Manuelle**

Pour chaque nouveau thème :

- [ ] Tous les composants UI sont lisibles
- [ ] Les boutons ont un contraste suffisant
- [ ] Les inputs sont bien visibles
- [ ] Les badges sont lisibles
- [ ] Le dark mode fonctionne correctement
- [ ] Les transitions sont fluides
- [ ] Pas de flash de contenu non stylé (FOUC)

---

## 📚 **Exemples de Thèmes**

### **Thème Spatial**

**Description** : Thème sombre spatial avec couleurs violettes, inspiré de l'espace.

**Couleurs principales** :
- Primary : `#7c3aed` (violet)
- Background : `#0a0a0f` (noir profond)
- Dark mode : Plus sombre avec couleurs plus claires

**Cas d'usage** : Par défaut, expérience immersive

### **Thème Minimaliste**

**Description** : Thème épuré noir et blanc avec inversion complète en dark mode.

**Couleurs principales** :
- Primary : `#000000` (noir)
- Background : `#ffffff` (blanc)
- Dark mode : Inversion complète

**Cas d'usage** : Utilisateurs préférant la simplicité

### **Thème Océan**

**Description** : Thème sombre avec couleurs bleues/cyan apaisantes.

**Couleurs principales** :
- Primary : `#0369a1` (bleu profond)
- Background : `#0c1220` (bleu très sombre)
- Dark mode : Profondeur océanique plus sombre

**Cas d'usage** : Ambiance apaisante, réduction de la fatigue visuelle

### **Thème Neutre**

**Description** : Thème clair/sombre avec gris élégants.

**Couleurs principales** :
- Primary : `#6b7280` (gris)
- Background : `#ffffff` (blanc) / `#111827` (dark)
- Dark mode : Gris foncé élégant

**Cas d'usage** : Professionnel, polyvalent

---

## 🚀 **Bonnes Pratiques**

### **1. Nommage**

- **ID du thème** : `kebab-case` (ex: `nouveau-theme`)
- **Nom affiché** : Titre avec majuscule (ex: `Nouveau Thème`)
- **Icon** : Emoji représentatif (ex: `🎨`)

### **2. Couleurs**

- **Toujours** définir toutes les variables CSS
- **Toujours** créer une variante dark mode
- **Toujours** vérifier les contrastes WCAG
- **Éviter** les couleurs trop saturées qui fatiguent les yeux

### **3. Accessibilité**

- Respecter WCAG 2.1 AAA pour `--muted-foreground`
- Respecter WCAG 2.1 AA minimum pour `--primary`
- Tester avec les outils de développement
- Vérifier avec les lecteurs d'écran (si possible)

### **4. Performance**

- Les thèmes sont appliqués via CSS variables (performant)
- Pas de JavaScript nécessaire pour le changement de thème
- Le dark mode utilise une simple classe CSS

---

## 📝 **Template pour Nouveau Thème**

```css
/* Thème [Nom] - Description courte */
[data-theme='theme-id'] {
  --radius: 0.625rem;
  --background: #ffffff;
  --foreground: #000000;
  --card: #f5f5f5;
  --card-foreground: #000000;
  --popover: #ffffff;
  --popover-foreground: #000000;
  --primary: #000000;
  --primary-foreground: #ffffff;
  --primary-light: #333333;
  --primary-text-on-dark: #cccccc;
  --secondary: #666666;
  --secondary-foreground: #ffffff;
  --muted: #f5f5f5;
  --muted-foreground: #4a4a4a; /* WCAG AAA : >= 7:1 */
  --accent: #000000;
  --accent-foreground: #ffffff;
  --destructive: #ef4444;
  --border: #000000;
  --input: #f5f5f5;
  --ring: #000000;
}

/* Thème [Nom] - Mode Dark */
.dark [data-theme='theme-id'] {
  --background: #000000;
  --foreground: #ffffff;
  --card: #1a1a1a;
  --card-foreground: #ffffff;
  --popover: #000000;
  --popover-foreground: #ffffff;
  --primary: #ffffff;
  --primary-foreground: #000000;
  --secondary: #999999;
  --secondary-foreground: #000000;
  --muted: #1a1a1a;
  --muted-foreground: #cccccc; /* Plus clair pour meilleur contraste */
  --accent: #ffffff;
  --accent-foreground: #000000;
  --border: #ffffff;
  --input: #1a1a1a;
  --ring: #ffffff;
}
```

---

## ✅ **Checklist Finale**

Avant de considérer un thème comme **production-ready** :

- [ ] Toutes les variables CSS définies
- [ ] Variante dark mode créée et testée
- [ ] Contraste WCAG AAA vérifié pour `--muted-foreground`
- [ ] Contraste WCAG AA vérifié pour `--primary`
- [ ] Ajouté au `Theme` type dans `themeStore.ts`
- [ ] Ajouté aux sélecteurs (`ThemeSelectorCompact.tsx`)
- [ ] Testé sur `/themes-test` avec tous les composants
- [ ] Testé avec dark mode activé/désactivé
- [ ] Documenté dans ce guide
- [ ] Pas de régression visuelle sur les autres pages

---

**Dernière mise à jour** : Janvier 2025  
**Maintenu par** : Équipe Frontend Mathakine

