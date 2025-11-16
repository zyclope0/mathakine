# 📚 Guide des Composants - Frontend Mathakine

**Date** : 9 Novembre 2025  
**Version** : 0.1.0

---

## 📋 **Table des Matières**

- [Composants UI (shadcn/ui)](#composants-ui-shadcnui)
- [Composants Exercices](#composants-exercices)
- [Composants Défis Logiques](#composants-défis-logiques)
- [Composants Badges](#composants-badges)
- [Composants Dashboard](#composants-dashboard)
- [Composants Layout](#composants-layout)
- [Composants Accessibilité](#composants-accessibilité)
- [Composants Thèmes](#composants-thèmes)
- [Composants i18n](#composants-i18n)

---

## 🎨 **Composants UI (shadcn/ui)**

Tous les composants UI sont basés sur **Radix UI** et **shadcn/ui**, garantissant l'accessibilité WCAG AAA.

### **Button**

**Fichier** : `components/ui/button.tsx`

**Variants disponibles** :
- `default` : Bouton principal (bg-primary)
- `outline` : Bouton avec bordure
- `ghost` : Bouton transparent
- `destructive` : Bouton de suppression (rouge)
- `secondary` : Bouton secondaire
- `link` : Style lien

**Exemple** :

```typescript
import { Button } from '@/components/ui/button';

<Button variant="default" size="default">
  Cliquer
</Button>

<Button variant="outline" size="sm">
  Petit bouton
</Button>
```

**Props** :
- `variant` : Variant du bouton
- `size` : `default` | `sm` | `lg` | `icon` | `icon-sm` | `icon-lg`
- `asChild` : Utiliser Slot pour composition
- Toutes les props HTML button standard

---

### **Card**

**Fichier** : `components/ui/card.tsx`

**Composants** :
- `Card` : Conteneur principal
- `CardHeader` : En-tête
- `CardTitle` : Titre
- `CardDescription` : Description
- `CardContent` : Contenu
- `CardFooter` : Pied de page

**Exemple** :

```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Titre</CardTitle>
  </CardHeader>
  <CardContent>
    Contenu de la carte
  </CardContent>
</Card>
```

---

### **Dialog**

**Fichier** : `components/ui/dialog.tsx`

**Composants** :
- `Dialog` : Conteneur principal
- `DialogTrigger` : Élément déclencheur
- `DialogContent` : Contenu de la modale
- `DialogHeader` : En-tête
- `DialogTitle` : Titre
- `DialogDescription` : Description
- `DialogFooter` : Pied de page

**Exemple** :

```typescript
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger>Ouvrir</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Titre</DialogTitle>
    </DialogHeader>
    Contenu de la modale
  </DialogContent>
</Dialog>
```

---

### **Input**

**Fichier** : `components/ui/input.tsx`

**Exemple** :

```typescript
import { Input } from '@/components/ui/input';

<Input 
  type="text" 
  placeholder="Saisir..."
  aria-label="Champ de saisie"
/>
```

**Accessibilité** :
- Support ARIA natif
- Focus visible
- Validation avec `aria-invalid`

---

### **Select**

**Fichier** : `components/ui/select.tsx`

**Composants** :
- `Select` : Conteneur principal
- `SelectTrigger` : Élément déclencheur
- `SelectValue` : Valeur sélectionnée
- `SelectContent` : Liste déroulante
- `SelectItem` : Élément de la liste

**Exemple** :

```typescript
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Choisir..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

---

## 🧮 **Composants Exercices**

### **ExerciseCard**

**Fichier** : `components/exercises/ExerciseCard.tsx`

**Description** : Carte affichant un exercice dans la liste.

**Props** :

```typescript
interface ExerciseCardProps {
  exercise: Exercise;
}
```

**Fonctionnalités** :
- Affichage titre, type, difficulté
- Animation Framer Motion (avec garde-fous)
- Lien vers page de résolution
- Badges visuels (type, difficulté)

**Exemple** :

```typescript
import { ExerciseCard } from '@/components/exercises/ExerciseCard';

<ExerciseCard exercise={exercise} />
```

---

### **ExerciseSolver**

**Fichier** : `components/exercises/ExerciseSolver.tsx`

**Description** : Composant pour résoudre un exercice.

**Props** :

```typescript
interface ExerciseSolverProps {
  exerciseId: number;
}
```

**Fonctionnalités** :
- Affichage question et choix multiples
- Validation réponse
- Feedback immédiat
- Explication après validation
- Enregistrement tentative

**Exemple** :

```typescript
import { ExerciseSolver } from '@/components/exercises/ExerciseSolver';

<ExerciseSolver exerciseId={123} />
```

---

### **ExerciseModal**

**Fichier** : `components/exercises/ExerciseModal.tsx`

**Description** : Modale pour résoudre un exercice rapidement.

**Props** :

```typescript
interface ExerciseModalProps {
  exerciseId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExerciseCompleted?: () => void;
}
```

**Fonctionnalités** :
- Modale avec Dialog
- Résolution rapide sans navigation
- Callback après complétion

**Exemple** :

```typescript
import { ExerciseModal } from '@/components/exercises/ExerciseModal';

<ExerciseModal 
  exerciseId={123}
  open={isOpen}
  onOpenChange={setIsOpen}
  onExerciseCompleted={() => console.log('Complété!')}
/>
```

---

### **ExerciseGenerator**

**Fichier** : `components/exercises/ExerciseGenerator.tsx`

**Description** : Générateur d'exercices standard (sans IA).

**Fonctionnalités** :
- Sélection type et difficulté
- Génération via API
- Feedback succès/erreur

---

### **AIGenerator**

**Fichier** : `components/exercises/AIGenerator.tsx`

**Description** : Générateur d'exercices avec IA (streaming SSE).

**Fonctionnalités** :
- Prompt utilisateur
- Streaming en temps réel
- Affichage progressif
- Génération intelligente

---

## 🧩 **Composants Défis Logiques**

### **ChallengeCard**

**Fichier** : `components/challenges/ChallengeCard.tsx`

**Description** : Carte affichant un défi logique dans la liste.

**Props** :

```typescript
interface ChallengeCardProps {
  challenge: Challenge;
}
```

**Fonctionnalités** :
- Affichage titre, description, type, âge
- Badges visuels (groupe d'âge, type)
- Statistiques (temps estimé, taux de réussite)
- Animation Framer Motion

---

### **ChallengeSolver**

**Fichier** : `components/challenges/ChallengeSolver.tsx`

**Description** : Composant pour résoudre un défi logique.

**Props** :

```typescript
interface ChallengeSolverProps {
  challengeId: number;
  onChallengeCompleted?: () => void;
}
```

**Fonctionnalités** :
- Affichage question et données visuelles
- Choix multiples ou saisie libre
- Système d'indices progressifs
- Validation et feedback
- Explication solution

---

### **LogicGrid**

**Fichier** : `components/challenges/LogicGrid.tsx`

**Description** : Grille interactive avec drag & drop pour défis logiques.

**Fonctionnalités** :
- Drag & drop avec @dnd-kit
- Navigation clavier alternative
- Accessibilité complète
- Respect reduced motion

---

### **PatternSolver**

**Fichier** : `components/challenges/PatternSolver.tsx`

**Description** : Résolveur de séquences et patterns.

**Props** :

```typescript
interface PatternSolverProps {
  challenge: PatternChallenge;
  onSolve: (value: number) => void;
  disabled?: boolean;
  showFeedback?: boolean;
}
```

**Fonctionnalités** :
- Affichage séquence
- Sélection valeur manquante
- Validation pattern
- Feedback visuel

---

## 🏆 **Composants Badges**

### **BadgeCard**

**Fichier** : `components/badges/BadgeCard.tsx`

**Description** : Carte affichant un badge.

**Props** :

```typescript
interface BadgeCardProps {
  badge: Badge;
  userBadge?: UserBadge;
  isEarned: boolean;
  index?: number;
}
```

**Fonctionnalités** :
- Affichage nom, description, titre Star Wars
- Badge difficulté (bronze, silver, gold)
- Animation shimmer si obtenu
- Points récompense
- Date d'obtention

---

### **BadgeGrid**

**Fichier** : `components/badges/BadgeGrid.tsx`

**Description** : Grille de badges avec tri et filtres.

**Fonctionnalités** :
- Affichage grille responsive
- Tri par catégorie, difficulté
- Filtres badges obtenus/disponibles
- Animation Framer Motion

---

## 📊 **Composants Dashboard**

### **StatsCard**

**Fichier** : `components/dashboard/StatsCard.tsx`

**Description** : Carte de statistique avec icône et valeur.

**Props** :

```typescript
interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}
```

---

### **ProgressChart**

**Fichier** : `components/dashboard/ProgressChart.tsx`

**Description** : Graphique de progression avec Recharts.

**Fonctionnalités** :
- Graphique ligne avec Recharts
- Lazy loading pour performance
- Responsive
- Accessibilité (ARIA labels)

---

### **Recommendations**

**Fichier** : `components/dashboard/Recommendations.tsx`

**Description** : Liste de recommandations personnalisées.

**Fonctionnalités** :
- Recommandations basées sur performance
- Liens vers exercices/défis
- Animation d'apparition

---

## 🏗️ **Composants Layout**

### **Header**

**Fichier** : `components/layout/Header.tsx`

**Description** : En-tête avec navigation et sélecteurs.

**Fonctionnalités** :
- Navigation principale
- Menu mobile responsive
- Sélecteur langue
- Sélecteur thème compact
- Bouton déconnexion

---

### **Footer**

**Fichier** : `components/layout/Footer.tsx`

**Description** : Pied de page avec informations.

**Fonctionnalités** :
- Copyright
- Liens utiles
- Informations légales

---

## ♿ **Composants Accessibilité**

### **AccessibilityToolbar**

**Fichier** : `components/accessibility/AccessibilityToolbar.tsx`

**Description** : Barre d'outils flottante pour options d'accessibilité.

**Fonctionnalités** :
- 5 boutons pour modes accessibilité
- Position fixe (bottom-right)
- Icônes Lucide React
- ARIA labels complets

**Modes** :
- Contraste élevé (Alt+C)
- Texte agrandi (Alt+T)
- Réduction animations (Alt+M)
- Mode dyslexie (Alt+D)
- Mode Focus TSA/TDAH

---

### **WCAGAudit**

**Fichier** : `components/accessibility/WCAGAudit.tsx`

**Description** : Audit automatique WCAG avec @axe-core/react.

**Fonctionnalités** :
- Audit au chargement
- Rapport d'erreurs
- Affichage console

---

## 🎨 **Composants Thèmes**

### **ThemeSelector**

**Fichier** : `components/theme/ThemeSelector.tsx`

**Description** : Sélecteur de thème complet.

**Fonctionnalités** :
- 4 thèmes disponibles
- Prévisualisation
- Persistance localStorage

---

### **ThemeSelectorCompact**

**Fichier** : `components/theme/ThemeSelectorCompact.tsx`

**Description** : Sélecteur de thème compact pour Header.

**Fonctionnalités** :
- Dropdown menu
- Icônes par thème
- Intégration Header

---

## 🌐 **Composants i18n**

### **LanguageSelector**

**Fichier** : `components/locale/LanguageSelector.tsx`

**Description** : Sélecteur de langue.

**Fonctionnalités** :
- Dropdown avec drapeaux
- Changement immédiat
- Persistance localStorage
- Invalidation React Query

---

### **LocaleInitializer**

**Fichier** : `components/locale/LocaleInitializer.tsx`

**Description** : Initialiseur de locale au chargement.

**Fonctionnalités** :
- Récupération locale depuis localStorage
- Application au document
- Synchronisation avec store

---

## 📝 **Bonnes Pratiques**

### **Créer un Nouveau Composant**

1. **Définir le type** :

```typescript
interface MyComponentProps {
  title: string;
  optional?: boolean;
}
```

2. **Utiliser les hooks appropriés** :

```typescript
'use client';

import { useTranslations } from 'next-intl';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
```

3. **Respecter l'accessibilité** :

```typescript
<div role="article" aria-labelledby="title">
  <h2 id="title">{title}</h2>
</div>
```

4. **Utiliser les animations accessibles** :

```typescript
const { createVariants, shouldReduceMotion } = useAccessibleAnimation();

<motion.div
  variants={createVariants({...})}
  animate={shouldReduceMotion ? {} : 'animate'}
>
```

---

## 🔗 **Ressources**

- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [next-intl Documentation](https://next-intl-docs.vercel.app/)

---

**Dernière mise à jour** : 9 Novembre 2025

