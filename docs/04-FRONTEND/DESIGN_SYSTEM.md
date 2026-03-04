# Système de Design Frontend — Mathakine

> Dernière mise à jour : 04/03/2026  
> Validé contre le code source réel (post-audit industrialisation + refonte Premium EdTech)

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

## Pattern « Focus Board » (Premium EdTech Glassmorphism)

Introduit en v2.5.0. Standard pour les pages de résolution full-page (exercice, défi). Remplace les `<Card>` flottantes sur fond spatial.

### Définition

```tsx
// Déclaré AU NIVEAU MODULE (jamais inline dans une fonction composant — cf. règle DnD ci-dessous)
function FocusBoard({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-slate-900/60 backdrop-blur-xl border border-white/20 shadow-2xl rounded-3xl p-8 md:p-12 w-full max-w-4xl mx-auto mt-8 md:mt-12",
        className
      )}
    >
      {children}
    </div>
  );
}
```

**Variante Challenge** (avec Command Bar collée) :
- FocusBoard : `rounded-t-3xl` (pas `rounded-3xl`)
- Command Bar : `bg-slate-950/80 border border-white/10 border-t-0 p-6 rounded-b-3xl max-w-5xl mx-auto`

### Structure interne standard

```tsx
<FocusBoard>
  {/* 1. Bouton retour discret */}
  <Link href="..." className="text-muted-foreground hover:text-white transition-colors mb-6 inline-flex items-center gap-2">
    <ArrowLeft className="h-4 w-4" /> Retour
  </Link>

  {/* 2. Titre (petite étiquette + titre star) */}
  <p className="text-sm text-muted-foreground font-mono">Défi #1234</p>
  <h1 className="text-3xl md:text-4xl font-bold text-white mt-2 mb-6">Titre principal</h1>

  {/* 3. Tags */}
  <div className="flex flex-wrap gap-2 mb-6">
    <Badge variant="outline">Tag</Badge>
  </div>

  {/* 4. Contenu principal */}
  {/* 5. Boîtes internes */}
  <div className="bg-white/5 border border-white/10 rounded-xl p-4">...</div>
</FocusBoard>
```

### ⚠️ Règle critique — DnD et composants définis inline

**Ne jamais définir `FocusBoard` (ou tout composant wrapper) à l'intérieur d'une fonction composant React** si des enfants utilisent des bibliothèques de drag & drop (`@dnd-kit/core`, etc.).

**Pourquoi** : un composant défini inline obtient une nouvelle référence à chaque render. React démonte et remonte l'arbre entier, détruisant le `DndContext` et cassant le drag.

```tsx
// ❌ Interdit — crée un nouveau type à chaque render
export function MyPage() {
  const FocusBoard = ({ children }) => <div>{children}</div>; // ← BUG dnd-kit
  return <FocusBoard><PuzzleRenderer /></FocusBoard>;
}

// ✅ Correct — type stable entre les renders
function FocusBoard({ children }) { return <div>{children}</div>; }
export function MyPage() {
  return <FocusBoard><PuzzleRenderer /></FocusBoard>;
}
```

---

## Pattern tuiles de réponse (Glassmorphism Gamifié)

Pour les pages exercice et défi. Styles selon l'état :

```tsx
className={cn(
  // Base
  "rounded-2xl py-6 md:py-8 text-2xl font-medium text-white cursor-pointer transition-all text-center border-2",
  // Repos
  !hasSubmitted && !isSelected && "bg-white/10 border-white/20 hover:bg-white/20 hover:border-white/40 hover:-translate-y-1",
  // Sélectionné
  !hasSubmitted && isSelected && "border-primary bg-primary/20 shadow-[0_0_20px_hsl(var(--primary)/0.3)]",
  // Correct après validation
  showCorrect && "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]",
  // Incorrect après validation
  showIncorrect && "bg-red-500/20 border-red-500 text-red-400",
)}
```

---

## Pattern Bouton Valider dynamique

```tsx
className={cn(
  "w-full transition-all",
  !hasAnswer && "opacity-50 cursor-not-allowed bg-slate-800 text-slate-400 border border-white/5",
  hasAnswer  && "bg-primary text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.35)] hover:shadow-[0_0_20px_hsl(var(--primary)/0.5)]"
)}
```

---

## Pattern Success State (Juicy Design)

```tsx
{/* Bandeau résultat */}
<div className="rounded-xl p-4 font-semibold text-lg flex items-center gap-3
                bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">

{/* Explication — Fiche de savoir */}
<div className="bg-primary/5 border-l-4 border-primary rounded-r-xl p-5 mt-6">
  <Lightbulb className="text-primary" />
  <h4 className="font-semibold text-primary mb-2">Explication</h4>
  <p className="text-slate-200 text-lg">...</p>
</div>

{/* Boutons d'action — hiérarchie claire */}
{/* Primaire (continuer) */}
<Button className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 rounded-xl hover:-translate-y-0.5">
{/* Secondaire (retour) */}
<Button className="bg-transparent border border-white/10 text-muted-foreground hover:bg-white/5 hover:text-white rounded-xl">
```

---

## Bouton Indice (style « bouée de sauvetage »)

```tsx
<Button
  variant="outline"
  className="border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 transition-colors px-6 py-3 rounded-xl"
>
  <Lightbulb className="mr-2 h-4 w-4" />
  Indice
</Button>
```

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
