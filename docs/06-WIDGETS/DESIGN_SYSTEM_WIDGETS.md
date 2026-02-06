# Design System - Widgets Dashboard

> Documentation du design system pour les widgets du dashboard Mathakine

## 🎨 Principes du design system

### Architecture CSS
Le projet utilise **CSS Variables** pour le theming automatique :
- ✅ **Multi-thème** : Dark mode / Light mode / Thèmes personnalisés (Spatial, Minimaliste, Océan, Neutre)
- ✅ **Variables CSS** : `bg-card`, `text-foreground`, `border-primary`, etc.
- ✅ **Classes Tailwind** : Utilisation systématique des classes avec variables CSS

### Composants de base (shadcn/ui)
Tous les widgets doivent utiliser les composants de base :
- `Card`, `CardContent`, `CardHeader`, `CardTitle`
- `Badge`
- `Progress`
- `Button`

---

## 📦 Structure d'un widget

### Template de base

```tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MyIcon } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { cn } from '@/lib/utils/cn';
import { motion } from 'framer-motion';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

interface MyWidgetProps {
  data: any;
  isLoading?: boolean;
}

export function MyWidget({ data, isLoading }: MyWidgetProps) {
  const t = useTranslations('dashboard.myWidget');
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  // Loading skeleton
  if (isLoading) {
    return (
      <Card className="bg-card border-primary/20 animate-pulse">
        <CardHeader>
          <div className="h-6 w-32 bg-muted rounded"></div>
        </CardHeader>
        <CardContent>
          <div className="h-12 w-full bg-muted rounded"></div>
        </CardContent>
      </Card>
    );
  }

  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="bg-card border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <MyIcon className="w-5 h-5 text-primary-on-dark" />
            {t('title')}
          </CardTitle>
        </CardHeader>

        <CardContent>
          {/* Contenu du widget */}
        </CardContent>
      </Card>
    </motion.div>
  );
}
```

---

## 🎨 Palette de couleurs

### Classes CSS variables (recommandées)

**Arrière-plans :**
- `bg-card` : Fond de carte (s'adapte au thème)
- `bg-muted` : Fond atténué pour skeleton
- `bg-background` : Fond de page

**Textes :**
- `text-foreground` : Texte principal
- `text-muted-foreground` : Texte secondaire
- `text-primary-on-dark` : Icônes principales

**Bordures :**
- `border-primary/20` : Bordure principale (20% opacité)
- `border-border` : Bordure standard

### Couleurs avec opacité (pour accents)

**Format :** `bg-{color}-500/{opacity}` et `text-{color}-{shade}`

**Exemples :**
```tsx
// Vert (succès, excellent)
className="bg-green-500/20 text-green-400 border-green-500/30"

// Bleu (information)
className="bg-blue-500/20 text-blue-400 border-blue-500/30"

// Orange (attention, streak)
className="bg-orange-500/20 text-orange-400 border-orange-500/30"

// Jaune (avertissement)
className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30"

// Rouge (erreur)
className="bg-red-500/20 text-red-400 border-red-500/30"
```

**Shades recommandés :**
- Fond : `/10` ou `/20` (très subtil)
- Bordure : `/30` ou `/40`
- Texte : `-400` (pour dark mode) ou `-600` (pour light mode)

---

## 🧩 Patterns communs

### 1. Widget avec accent coloré

Pour mettre en valeur un widget (ex: Streak actif) :

```tsx
<Card className={cn(
  'bg-card border-2',
  isActive ? 'border-orange-500/40 bg-orange-500/5' : 'border-primary/20'
)}>
```

### 2. Stats dans des boxes colorées

```tsx
<div className="grid grid-cols-2 gap-4">
  <div className="rounded-lg p-3 bg-green-500/10 border border-green-500/20">
    <div className="flex items-center gap-2 mb-1">
      <Target className="w-4 h-4 text-green-400" />
      <div className="text-xs text-muted-foreground">
        Taux de réussite
      </div>
    </div>
    <div className="text-lg font-bold text-green-400">
      85%
    </div>
  </div>
</div>
```

### 3. Badges de statut

```tsx
// Badge de catégorie
<Badge variant="outline" className="text-green-400 border-green-500/30">
  Addition
</Badge>

// Badge de performance
<Badge className="bg-green-500/20 text-green-400 text-xs">
  Excellent !
</Badge>

// Badge de record
<Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
  <TrendingUp className="w-3 h-3" />
  Nouveau record !
</Badge>
```

### 4. Barres de progression

Utiliser le composant `Progress` de shadcn/ui :

```tsx
import { Progress } from '@/components/ui/progress';

<Progress value={75} className="h-3" />
```

**Ne pas** créer de barres custom avec `div` et `bg-gradient-to-r`.

---

## ⚡ Animations

### Utilisation de Framer Motion

**Toujours** utiliser le hook `useAccessibleAnimation` pour respecter `prefers-reduced-motion` :

```tsx
const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

const variants = createVariants({
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
});

const transition = createTransition({ duration: 0.2 });
```

### Animations d'icônes

```tsx
<motion.div
  animate={!shouldReduceMotion ? { 
    rotate: [0, -10, 10, -10, 0],
    scale: [1, 1.1, 1]
  } : {}}
  transition={{ duration: 0.5, delay: 0.2 }}
>
  <Flame className="w-5 h-5 text-orange-400" />
</motion.div>
```

### Hover effects

```tsx
<motion.div
  whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
>
  <Card>...</Card>
</motion.div>
```

---

## ♿ Accessibilité

### Focus states

Tous les widgets interactifs doivent avoir un focus visible :

```tsx
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
```

### Skeleton loaders

Toujours fournir un skeleton pendant le chargement :

```tsx
if (isLoading) {
  return (
    <Card className="bg-card border-primary/20 animate-pulse">
      <CardHeader>
        <div className="h-6 w-32 bg-muted rounded"></div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-4 w-full bg-muted rounded"></div>
          <div className="h-4 w-3/4 bg-muted rounded"></div>
        </div>
      </CardContent>
    </Card>
  );
}
```

### ARIA attributes

Pour les widgets avec valeurs numériques :

```tsx
<div
  role="article"
  aria-label={`Série actuelle: ${currentStreak} jours`}
  tabIndex={0}
>
```

---

## 🌙 Multi-thème

### Variables CSS à utiliser

**✅ À FAIRE :**
```tsx
className="bg-card text-foreground border-primary/20"
```

**❌ À ÉVITER :**
```tsx
className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
```

### Thèmes disponibles

Le projet supporte plusieurs thèmes :
- **Spatial** (défaut) : Fond spatial avec étoiles
- **Minimaliste** : Fond uni clair
- **Océan** : Couleurs bleues/cyan
- **Neutre** : Gris neutres

Les variables CSS s'adaptent automatiquement à chaque thème.

---

## 📊 Exemples de widgets

### StreakWidget (avec accent)

```tsx
<Card className={cn(
  'bg-card border-2',
  currentStreak > 0 ? 'border-orange-500/40 bg-orange-500/5' : 'border-primary/20'
)}>
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Flame className={cn(
        'w-5 h-5',
        currentStreak > 0 ? 'text-orange-400' : 'text-muted-foreground'
      )} />
      Série en cours
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-5xl font-bold text-orange-400">
      {currentStreak}
    </div>
  </CardContent>
</Card>
```

### ChallengesProgressWidget (avec stats boxes)

```tsx
<Card className="bg-card border-primary/20">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Trophy className="w-5 h-5 text-yellow-400" />
      Progression des défis
    </CardTitle>
  </CardHeader>
  <CardContent>
    <Progress value={33} className="h-3 mb-4" />
    
    <div className="grid grid-cols-2 gap-4">
      <div className="rounded-lg p-3 bg-green-500/10 border border-green-500/20">
        <div className="text-xs text-muted-foreground">Taux de réussite</div>
        <div className="text-lg font-bold text-green-400">44%</div>
      </div>
      
      <div className="rounded-lg p-3 bg-blue-500/10 border border-blue-500/20">
        <div className="text-xs text-muted-foreground">Temps moyen</div>
        <div className="text-lg font-bold text-blue-400">173s</div>
      </div>
    </div>
  </CardContent>
</Card>
```

### CategoryAccuracyChart (avec badges)

```tsx
<Card className="bg-card border-primary/20">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <BarChart3 className="w-5 h-5 text-primary-on-dark" />
      Précision par catégorie
    </CardTitle>
  </CardHeader>
  <CardContent>
    {categories.map(([category, data]) => (
      <div key={category} className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <Badge variant="outline" className="text-green-400 border-green-500/30">
            {category}
          </Badge>
          <span className="text-lg font-bold text-green-400">
            {data.accuracy}%
          </span>
        </div>
        <Progress value={data.accuracy} className="h-3" />
      </div>
    ))}
  </CardContent>
</Card>
```

---

## 🚨 À éviter

### ❌ Hardcoder des couleurs
```tsx
// MAUVAIS
className="bg-white dark:bg-gray-800"

// BON
className="bg-card"
```

### ❌ Créer des barres de progression custom
```tsx
// MAUVAIS
<div className="bg-gray-200 dark:bg-gray-700 rounded-full h-3">
  <div className="bg-gradient-to-r from-green-400 to-green-600 h-full rounded-full" />
</div>

// BON
<Progress value={75} className="h-3" />
```

### ❌ Oublier le reduced motion
```tsx
// MAUVAIS
animate={{ rotate: [0, 360] }}

// BON
animate={!shouldReduceMotion ? { rotate: [0, 360] } : {}}
```

### ❌ Ignorer les loading states
```tsx
// MAUVAIS
export function MyWidget({ data }: Props) {
  return <Card>{data.value}</Card>;
}

// BON
export function MyWidget({ data, isLoading }: Props) {
  if (isLoading) return <SkeletonCard />;
  return <Card>{data.value}</Card>;
}
```

---

## ✅ Checklist pour nouveau widget

- [ ] Utilise `Card` de shadcn/ui
- [ ] Classes CSS variables (`bg-card`, `text-foreground`, etc.)
- [ ] Couleurs avec opacité pour accents (`bg-green-500/20`)
- [ ] Skeleton loader pour `isLoading`
- [ ] Hook `useAccessibleAnimation` pour animations
- [ ] `whileHover` conditionné par `shouldReduceMotion`
- [ ] Focus states avec `focus-visible:ring-2`
- [ ] Traductions via `useTranslations`
- [ ] `Progress` component pour barres de progression
- [ ] `Badge` component pour labels/statuts
- [ ] Motion wrapper avec variants
- [ ] ARIA attributes si pertinent
- [ ] Testé en dark mode et light mode
- [ ] Build réussi sans erreurs TypeScript

---

## 📚 Références

- **shadcn/ui** : https://ui.shadcn.com/
- **Tailwind CSS** : https://tailwindcss.com/docs
- **Framer Motion** : https://www.framer.com/motion/
- **next-intl** : https://next-intl-docs.vercel.app/

---

**Dernière mise à jour :** 06/02/2026
