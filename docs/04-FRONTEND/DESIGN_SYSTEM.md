# Système de Design Frontend — Mathakine

> Dernière mise à jour : 03/03/2026  
> Validé contre le code source réel (post-audit industrialisation)

Le système de design garantit cohérence UI/UX sur toutes les pages, via des composants de layout standardisés. Toute nouvelle page **doit** utiliser ces composants.

---

## Composants de layout (`components/layout/`)

### PageLayout

Wrapper de base pour toutes les pages — padding responsive + max-width.

```tsx
import { PageLayout } from "@/components/layout";

<PageLayout maxWidth="xl">{/* contenu */}</PageLayout>
```

**Props** : `maxWidth?: 'sm'|'md'|'lg'|'xl'|'2xl'|'full'` (défaut: `'xl'`), `className?`

---

### PageHeader

En-tête standardisé avec titre, description, icône et actions.

```tsx
import { PageHeader } from "@/components/layout";
import { Puzzle } from "lucide-react";

<PageHeader
  title="Défis Logiques"
  description="Relevez des défis de logique mathématique"
  icon={Puzzle}
  actions={<Button variant="outline">Nouveau défi</Button>}
/>
```

**Props** : `title` (requis), `description?`, `icon?`, `actions?`, `className?`

---

### PageSection

Section de page avec titre et description optionnels — espacements cohérents.

```tsx
import { PageSection } from "@/components/layout";

<PageSection title="Filtres" description="Filtrez selon vos préférences">
  {/* contenu */}
</PageSection>
```

**Props** : `title?`, `description?`, `icon?`, `children` (requis), `className?`, `headerClassName?`

---

### PageGrid

Grille responsive standardisée.

```tsx
import { PageGrid } from "@/components/layout";

<PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="md">
  {items.map((item) => <ItemCard key={item.id} item={item} />)}
</PageGrid>
```

**Props** : `columns?: { mobile, tablet, desktop }`, `gap?: 'sm'|'md'|'lg'`

---

### EmptyState

État vide standardisé — message centré + icône + action.

```tsx
import { EmptyState } from "@/components/layout";

<EmptyState
  title="Aucun défi trouvé"
  description="Essayez de modifier vos filtres"
  icon={Puzzle}
  action={<Button>Générer un défi</Button>}
/>
```

---

### LoadingState

Spinner de chargement standardisé — centré, accessible (`sr-only`).

```tsx
import { LoadingState } from "@/components/layout";

<LoadingState message="Chargement des exercices..." size="md" />
```

**Props** : `message?`, `size?: 'sm'|'md'|'lg'`

---

## Pattern de page standard

Structure à copier pour toute nouvelle page :

```tsx
"use client";

import { PageLayout, PageHeader, PageSection, PageGrid, EmptyState, LoadingState } from "@/components/layout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export default function MyPage() {
  const { data, isLoading, error } = useData();

  return (
    <ProtectedRoute>
      <PageLayout>
        <PageHeader title="Titre" description="Description" />

        <PageSection title="Section">
          {error ? (
            <Card><CardContent className="py-12">
              <p className="text-center text-destructive">
                Erreur de chargement. Vérifiez vos droits.
              </p>
            </CardContent></Card>
          ) : isLoading ? (
            <LoadingState message="Chargement..." />
          ) : data.length === 0 ? (
            <EmptyState title="Aucun résultat" />
          ) : (
            <PageGrid>
              {data.map((item) => <ItemCard key={item.id} item={item} />)}
            </PageGrid>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
```

> **Note pattern admin** : Les pages admin utilisent `PageSection` sans `PageLayout` (le layout admin fournit déjà le wrapper via `admin/layout.tsx`). Le sélecteur de filtre va à l'intérieur du `PageSection`.

---

## Règles d'usage

| ❌ Interdit | ✅ Standard |
|---|---|
| `<div className="min-h-screen p-4 md:p-8">` | `<PageLayout>` |
| `<h1 className="text-3xl font-bold">` | `<PageHeader title="..." />` |
| `<div>Chargement...</div>` | `<LoadingState />` |
| `<div>Aucun résultat</div>` | `<EmptyState title="..." />` |
| `<div className="grid grid-cols-1 md:grid-cols-3 gap-4">` | `<PageGrid>` |
| `<input className="...">` raw | `<Input>` (shadcn/ui) |
| `<textarea className="...">` raw | `<Textarea>` (shadcn/ui) |
| `import { cn } from "@/lib/utils/cn"` | `import { cn } from "@/lib/utils"` |
| Couleur hardcodée ex: `stroke="#7c3aed"` | `stroke="var(--color-chart-1)"` |
| Dupliquer `hasAiTag` inline | `import { hasAiTag } from "@/lib/utils/format"` |

---

## Design Tokens (via CSS variables)

Les tokens de design sont définis comme variables CSS dans `app/globals.css` (pas via un fichier TypeScript). Ils suivent les conventions shadcn/ui :

```css
/* Couleurs sémantiques (shadcn/ui) */
--background, --foreground
--primary, --primary-foreground
--secondary, --muted, --accent
--destructive, --border, --ring
--card, --card-foreground, --popover, --popover-foreground

/* Tokens sémantiques additionnels (à utiliser à la place des couleurs Tailwind hardcodées) */
--warning, --warning-foreground   /* Ex : alertes, messages d'avertissement */
--success, --success-foreground   /* Ex : feedback positif */
--info, --info-foreground         /* Ex : messages informatifs */

/* Tokens charts — 7 thèmes × light/dark */
--chart-1 à --chart-5            /* Lignes/barres/séries dans Recharts */

/* Tokens sidebar */
--sidebar-background, --sidebar-foreground, --sidebar-primary, etc.

/* Utilisés par Tailwind via @theme inline */
bg-primary, text-foreground, bg-warning, text-chart-1...
```

> **Règle** : Ne jamais utiliser `dark:text-yellow-*`, `bg-blue-600` hardcodés dans les composants applicatifs. Utiliser `bg-warning`, `bg-primary`, `text-muted-foreground`, etc.

---

## Classe utilitaire `card-spatial-depth`

Définie dans `globals.css`. Ajoute profondeur et effet de survol (sweep + élévation) aux cartes.

```tsx
<Card className="card-spatial-depth">...</Card>
```

- Élévation `translateY(-4px)` au hover
- Sweep de lumière via `::before`
- Ombre `primary/30` adaptative au thème
- Reduced-motion déjà géré (désactivé si `prefers-reduced-motion`)

---

## Composants UI (shadcn/ui)

Tous dans `components/ui/`. Basés sur Radix UI — accessibilité WCAG incluse.

| Composant | Usage |
|---|---|
| `Button` | Variants: `default`, `outline`, `ghost`, `destructive`, `secondary`, `link` |
| `Card` + `CardHeader/Content/Footer` | Conteneurs avec séparation visuelle |
| `Dialog` + `DialogTrigger/Content/Title` | Modales accessibles |
| `Input` | **Obligatoire** pour tous les `<input type="text/email/…">` — jamais `<input>` raw |
| `Textarea` | **Obligatoire** pour tous les `<textarea>` — jamais `<textarea>` raw |
| `Select` + `SelectTrigger/Content/Item` | Sélecteurs |
| `Badge` | Étiquettes visuelles |
| `Progress` | Barres de progression |
| `Skeleton` | Placeholder de chargement — intégré dans `DashboardWidgetSkeleton` |

### DashboardWidgetSkeleton

Squelette générique pour les widgets du dashboard — évite les implémentations ad-hoc.

```tsx
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";

// Squelette par défaut (2 lignes de texte)
<DashboardWidgetSkeleton />

// Avec contenu personnalisé
<DashboardWidgetSkeleton titleWidth="w-32">
  <Skeleton className="h-32 w-full" />
</DashboardWidgetSkeleton>
```

---

## Templates

Templates de page disponibles dans `frontend/docs/templates/` :
- `PAGE_LIST_TEMPLATE.md` — page liste avec filtres et pagination

---

## Références

- Composants : `frontend/components/layout/`
- Templates : `frontend/docs/templates/`
- [Accessibilité](ACCESSIBILITY.md) — WCAG AAA et raccourcis clavier
- [Architecture](ARCHITECTURE.md) — structure complète du projet
