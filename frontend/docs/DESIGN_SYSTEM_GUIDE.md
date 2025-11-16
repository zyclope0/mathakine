# 🎨 Guide du Système de Design - Mathakine

**Date** : 9 Novembre 2025  
**Version** : 1.0.0

---

## 📋 **Table des Matières**

- [Principe](#principe)
- [Composants de Layout](#composants-de-layout)
- [Design Tokens](#design-tokens)
- [Patterns de Page](#patterns-de-page)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## 🎯 **Principe**

Le système de design garantit :
- ✅ **Cohérence** : Même UI/UX sur toutes les pages
- ✅ **Maintenabilité** : Modifications centralisées
- ✅ **Rapidité** : Création de nouvelles pages en ~15 minutes
- ✅ **Accessibilité** : WCAG 2.1 AAA par défaut

---

## 🧩 **Composants de Layout**

### **PageLayout**

Layout de base pour toutes les pages.

```tsx
import { PageLayout } from '@/components/layout/PageLayout';

<PageLayout maxWidth="xl">
  {/* Contenu de la page */}
</PageLayout>
```

**Props** :
- `maxWidth` : `'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'` (défaut: `'xl'`)
- `className` : Classes CSS additionnelles

**Garantit** :
- Padding responsive (`p-4 md:p-6 lg:p-8`)
- Container avec max-width
- Espacements verticaux (`space-y-6`)

---

### **PageHeader**

En-tête standardisé avec titre, description et actions.

```tsx
import { PageHeader } from '@/components/layout/PageHeader';
import { Puzzle } from 'lucide-react';

<PageHeader
  title="Défis Logiques"
  description="Relevez des défis de logique mathématique"
  icon={Puzzle}
  actions={
    <Button variant="outline">Action</Button>
  }
/>
```

**Props** :
- `title` : Titre de la page (requis)
- `description` : Description optionnelle
- `icon` : Icône Lucide optionnelle
- `actions` : Actions (boutons) optionnelles alignées à droite
- `className` : Classes CSS additionnelles

**Garantit** :
- Hiérarchie typographique (`text-3xl font-bold`)
- Espacements standardisés
- Responsive (flex-col sur mobile, flex-row sur desktop)

---

### **PageSection**

Section de page avec titre et description optionnels.

```tsx
import { PageSection } from '@/components/layout/PageSection';

<PageSection
  title="Filtres"
  description="Filtrez les résultats selon vos préférences"
>
  {/* Contenu de la section */}
</PageSection>
```

**Props** :
- `title` : Titre de la section (optionnel)
- `description` : Description optionnelle
- `children` : Contenu de la section
- `className` : Classes CSS additionnelles
- `headerClassName` : Classes CSS pour l'en-tête

**Garantit** :
- Espacements cohérents (`space-y-4`)
- Hiérarchie visuelle claire

---

### **PageGrid**

Grille responsive standardisée.

```tsx
import { PageGrid } from '@/components/layout/PageGrid';

<PageGrid
  columns={{ mobile: 1, tablet: 2, desktop: 3 }}
  gap="md"
>
  {items.map((item) => (
    <ItemCard key={item.id} item={item} />
  ))}
</PageGrid>
```

**Props** :
- `columns` : Nombre de colonnes par breakpoint
  - `mobile` : Colonnes sur mobile (défaut: `1`)
  - `tablet` : Colonnes sur tablet (défaut: `2`)
  - `desktop` : Colonnes sur desktop (défaut: `3`)
- `gap` : Espacement entre les items (`'sm' | 'md' | 'lg'`, défaut: `'md'`)
- `className` : Classes CSS additionnelles

**Garantit** :
- Breakpoints cohérents (`md:`, `lg:`)
- Espacements standardisés

---

### **EmptyState**

État vide standardisé.

```tsx
import { EmptyState } from '@/components/layout/EmptyState';
import { Puzzle } from 'lucide-react';

<EmptyState
  title="Aucun défi trouvé"
  description="Essayez de modifier vos filtres pour voir plus de résultats"
  icon={Puzzle}
  action={<Button>Générer un défi</Button>}
/>
```

**Props** :
- `title` : Titre du message (requis)
- `description` : Description optionnelle
- `icon` : Icône Lucide optionnelle
- `action` : Action (bouton) optionnelle
- `className` : Classes CSS additionnelles

**Garantit** :
- Message clair et centré
- Espacements cohérents (`py-12`, `min-h-[12rem]`)

---

### **LoadingState**

État de chargement standardisé.

```tsx
import { LoadingState } from '@/components/layout/LoadingState';

<LoadingState message="Chargement des exercices..." size="md" />
```

**Props** :
- `message` : Message optionnel
- `size` : Taille du spinner (`'sm' | 'md' | 'lg'`, défaut: `'md'`)
- `className` : Classes CSS additionnelles

**Garantit** :
- Spinner centré
- Espacements cohérents (`py-12`, `min-h-[12rem]`)
- Accessibilité (`sr-only`)

---

## 🎨 **Design Tokens**

### **Espacements**

```typescript
import { spacing } from '@/lib/design-tokens';

spacing.xs   // 8px
spacing.sm   // 12px
spacing.md   // 16px
spacing.lg   // 24px
spacing.xl   // 32px
```

### **Typographie**

```typescript
import { typography } from '@/lib/design-tokens';

typography.sizes.xs      // 12px
typography.sizes.base    // 16px
typography.sizes['2xl']  // 24px
```

### **Breakpoints**

```typescript
import { breakpoints } from '@/lib/design-tokens';

breakpoints.sm   // 640px
breakpoints.md   // 768px
breakpoints.lg   // 1024px
```

---

## 📄 **Patterns de Page**

### **Structure Standard**

```tsx
'use client';

import { PageLayout } from '@/components/layout/PageLayout';
import { PageHeader } from '@/components/layout/PageHeader';
import { PageSection } from '@/components/layout/PageSection';
import { PageGrid } from '@/components/layout/PageGrid';
import { EmptyState } from '@/components/layout/EmptyState';
import { LoadingState } from '@/components/layout/LoadingState';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function MyPage() {
  const { data, isLoading } = useData();

  return (
    <ProtectedRoute>
      <PageLayout>
        <PageHeader
          title="Titre de la Page"
          description="Description de la page"
        />

        <PageSection title="Section">
          {isLoading ? (
            <LoadingState />
          ) : data.length === 0 ? (
            <EmptyState
              title="Aucun résultat"
              description="Description de l'état vide"
            />
          ) : (
            <PageGrid>
              {data.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </PageGrid>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
```

---

## 📝 **Templates**

### **Template Page Liste**

Voir `frontend/docs/templates/PAGE_LIST_TEMPLATE.md`

### **Template Page Détail**

Voir `frontend/docs/templates/PAGE_DETAIL_TEMPLATE.md`

---

## ✅ **Best Practices**

### **1. Toujours Utiliser les Composants Standardisés**

❌ **Mauvais** :
```tsx
<div className="min-h-screen p-4 md:p-8">
  <div className="max-w-7xl mx-auto">
    <h1 className="text-3xl font-bold">Titre</h1>
  </div>
</div>
```

✅ **Bon** :
```tsx
<PageLayout>
  <PageHeader title="Titre" />
</PageLayout>
```

### **2. Utiliser les Design Tokens**

❌ **Mauvais** :
```tsx
<div className="p-4 md:p-6 lg:p-8">
```

✅ **Bon** :
```tsx
<PageLayout> {/* Utilise les tokens automatiquement */}
```

### **3. États Standardisés**

❌ **Mauvais** :
```tsx
{isLoading && <div>Chargement...</div>}
{data.length === 0 && <div>Aucun résultat</div>}
```

✅ **Bon** :
```tsx
{isLoading && <LoadingState />}
{data.length === 0 && <EmptyState title="Aucun résultat" />}
```

### **4. Grilles Responsive**

❌ **Mauvais** :
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

✅ **Bon** :
```tsx
<PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="md">
```

---

## 🚀 **Créer une Nouvelle Page**

1. **Copier le template** depuis `frontend/docs/templates/`
2. **Remplacer** les placeholders
3. **Utiliser** les composants standardisés
4. **Tester** sur mobile, tablet et desktop

**Temps estimé** : ~15 minutes

---

## 📚 **Ressources**

- **Design Tokens** : `frontend/lib/design-tokens.ts`
- **Composants Layout** : `frontend/components/layout/`
- **Templates** : `frontend/docs/templates/`

---

**Dernière mise à jour** : 9 Novembre 2025

