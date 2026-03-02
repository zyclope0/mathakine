# Système de Design Frontend — Mathakine

> Dernière mise à jour : 22/02/2026  
> Validé contre le code source réel

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

---

## Design Tokens (via CSS variables)

Les tokens de design sont définis comme variables CSS dans `app/globals.css` (pas via un fichier TypeScript). Ils suivent les conventions shadcn/ui :

```css
/* Couleurs sémantiques */
--background, --foreground
--primary, --primary-foreground
--secondary, --muted, --accent
--destructive, --border, --ring

/* Utilisés par Tailwind via le système de variables */
bg-primary, text-foreground, border-border, ring-ring...
```

---

## Composants UI (shadcn/ui)

Tous dans `components/ui/`. Basés sur Radix UI — accessibilité WCAG incluse.

| Composant | Usage |
|---|---|
| `Button` | Variants: `default`, `outline`, `ghost`, `destructive`, `secondary`, `link` |
| `Card` + `CardHeader/Content/Footer` | Conteneurs avec séparation visuelle |
| `Dialog` + `DialogTrigger/Content/Title` | Modales accessibles |
| `Input` | Champs de saisie (ARIA natif) |
| `Select` + `SelectTrigger/Content/Item` | Sélecteurs |
| `Badge` | Étiquettes visuelles |
| `Progress` | Barres de progression |

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
