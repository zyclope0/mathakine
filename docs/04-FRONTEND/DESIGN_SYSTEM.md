# SystÃ¨me de Design Frontend â€” Mathakine

> DerniÃ¨re mise Ã  jour : 05/04/2026  
> ValidÃ© contre le code source rÃ©el (post-audit industrialisation + refonte Premium EdTech)

Le systÃ¨me de design garantit cohÃ©rence UI/UX sur toutes les pages, via des composants de layout standardisÃ©s. Toute nouvelle page **doit** utiliser ces composants.

---

## Composants de layout (`components/layout/`)

### PageLayout

Wrapper de base pour toutes les pages â€” padding responsive + max-width.

```tsx
import { PageLayout } from "@/components/layout";

<PageLayout maxWidth="xl">{/* contenu */}</PageLayout>;
```

**Props** : `maxWidth?: 'sm'|'md'|'lg'|'xl'|'2xl'|'full'` (dÃ©faut: `'xl'`), `className?`

---

### PageHeader

En-tÃªte standardisÃ© avec titre, description, icÃ´ne et actions.

```tsx
import { PageHeader } from "@/components/layout";
import { Puzzle } from "lucide-react";

<PageHeader
  title="DÃ©fis Logiques"
  description="Relevez des dÃ©fis de logique mathÃ©matique"
  icon={Puzzle}
  actions={<Button variant="outline">Nouveau dÃ©fi</Button>}
/>;
```

**Props** : `title` (requis), `description?`, `icon?`, `actions?`, `className?`

---

### PageSection

Section de page avec titre et description optionnels â€” espacements cohÃ©rents.

```tsx
import { PageSection } from "@/components/layout";

<PageSection title="Filtres" description="Filtrez selon vos prÃ©fÃ©rences">
  {/* contenu */}
</PageSection>;
```

**Props** : `title?`, `description?`, `icon?`, `children` (requis), `className?`, `headerClassName?`

---

### PageGrid

Grille responsive standardisÃ©e.

```tsx
import { PageGrid } from "@/components/layout";

<PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="md">
  {items.map((item) => (
    <ItemCard key={item.id} item={item} />
  ))}
</PageGrid>;
```

**Props** : `columns?: { mobile, tablet, desktop }`, `gap?: 'sm'|'md'|'lg'`

---

### EmptyState

Ã‰tat vide standardisÃ© â€” message centrÃ© + icÃ´ne + action.

```tsx
import { EmptyState } from "@/components/layout";

<EmptyState
  title="Aucun dÃ©fi trouvÃ©"
  description="Essayez de modifier vos filtres"
  icon={Puzzle}
  action={<Button>GÃ©nÃ©rer un dÃ©fi</Button>}
/>;
```

---

### LoadingState

Spinner de chargement standardisÃ© â€” centrÃ©, accessible (`sr-only`).

```tsx
import { LoadingState } from "@/components/layout";

<LoadingState message="Chargement des exercices..." size="md" />;
```

**Props** : `message?`, `size?: 'sm'|'md'|'lg'`

---

## Primitives apprenant (`components/learner/`)

La couche apprenant est additive et volontairement plus calme que les surfaces dashboard.
Elle sert le flux `home-learner` et les surfaces de resolution.

### LearnerLayout

Wrapper mono-colonne avec largeur controlee, grands espaces blancs et zero sidebar.

```tsx
import { LearnerLayout } from "@/components/learner/LearnerLayout";

<LearnerLayout maxWidth="2xl">{/* parcours apprenant */}</LearnerLayout>;
```

### LearnerCard

Carte apprenant sans shadow decoratif, basee sur `--bg-learner` et `data-learner-context`.

```tsx
import { LearnerCard } from "@/components/learner/LearnerCard";

<LearnerCard variant="exercise">{/* solveur */}</LearnerCard>;
```

Regles :

- preferer `LearnerCard` a `Card` pour tout flux de reflexion principal
- conserver un signal visuel calme : bordure legere, pas de lift, pas de glow
- laisser `Card` classique aux surfaces dashboard/admin et aux zones non apprenantes

---

## Pattern de page standard

Structure Ã  copier pour toute nouvelle page :

```tsx
"use client";

import {
  PageLayout,
  PageHeader,
  PageSection,
  PageGrid,
  EmptyState,
  LoadingState,
} from "@/components/layout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export default function MyPage() {
  const { data, isLoading, error } = useData();

  return (
    <ProtectedRoute>
      <PageLayout>
        <PageHeader title="Titre" description="Description" />

        <PageSection title="Section">
          {error ? (
            <Card>
              <CardContent className="py-12">
                <p className="text-center text-destructive">
                  Erreur de chargement. VÃ©rifiez vos droits.
                </p>
              </CardContent>
            </Card>
          ) : isLoading ? (
            <LoadingState message="Chargement..." />
          ) : data.length === 0 ? (
            <EmptyState title="Aucun rÃ©sultat" />
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

> **Note pattern admin** : Les pages admin utilisent `PageSection` sans `PageLayout` (le layout admin fournit dÃ©jÃ  le wrapper via `admin/layout.tsx`). Le sÃ©lecteur de filtre va Ã  l'intÃ©rieur du `PageSection`.

---

## RÃ¨gles d'usage

| âŒ Interdit                                               | âœ… Standard                                    |
| --------------------------------------------------------- | ----------------------------------------------- |
| `<div className="min-h-screen p-4 md:p-8">`               | `<PageLayout>`                                  |
| `<h1 className="text-3xl font-bold">`                     | `<PageHeader title="..." />`                    |
| `<div>Chargement...</div>`                                | `<LoadingState />`                              |
| `<div>Aucun rÃ©sultat</div>`                              | `<EmptyState title="..." />`                    |
| `<div className="grid grid-cols-1 md:grid-cols-3 gap-4">` | `<PageGrid>`                                    |
| `<input className="...">` raw                             | `<Input>` (shadcn/ui)                           |
| `<textarea className="...">` raw                          | `<Textarea>` (shadcn/ui)                        |
| `import { cn } from "@/lib/utils/cn"`                     | `import { cn } from "@/lib/utils"`              |
| Couleur hardcodÃ©e ex: `stroke="#7c3aed"`                 | `stroke="var(--color-chart-1)"`                 |
| Dupliquer `hasAiTag` inline                               | `import { hasAiTag } from "@/lib/utils/format"` |

---

## Design Tokens (via CSS variables)

Les tokens de design sont dÃ©finis comme variables CSS dans `app/globals.css` (pas via un fichier TypeScript). Ils suivent les conventions shadcn/ui :

```css
/* Couleurs sÃ©mantiques (shadcn/ui) */
--background, --foreground
--primary, --primary-foreground
--secondary, --muted, --accent
--destructive, --border, --ring
--card, --card-foreground, --popover, --popover-foreground

/* Tokens sÃ©mantiques additionnels (Ã  utiliser Ã  la place des couleurs Tailwind hardcodÃ©es) */
--warning, --warning-foreground   /* Ex : alertes, messages d'avertissement */
--success, --success-foreground   /* Ex : feedback positif */
--info, --info-foreground         /* Ex : messages informatifs */

/* Tokens charts â€” 8 thÃ¨mes Ã— light/dark */
--chart-1 Ã  --chart-5            /* Lignes/barres/sÃ©ries dans Recharts */

/* Tokens sidebar */
--sidebar-background, --sidebar-foreground, --sidebar-primary, etc.

/* UtilisÃ©s par Tailwind via @theme inline */
bg-primary, text-foreground, bg-warning, text-chart-1...
```

> **RÃ¨gle** : Ne jamais utiliser `dark:text-yellow-*`, `bg-blue-600` hardcodÃ©s dans les composants applicatifs. Utiliser `bg-warning`, `bg-primary`, `text-muted-foreground`, etc.

---

## Pattern Â« Focus Board Â» (Premium EdTech Glassmorphism)

Introduit en v2.5.0. Standard pour les pages de rÃ©solution full-page (exercice, dÃ©fi). Remplace les `<Card>` flottantes sur fond spatial.

### DÃ©finition

```tsx
// DÃ©clarÃ© AU NIVEAU MODULE (jamais inline dans une fonction composant â€” cf. rÃ¨gle DnD ci-dessous)
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
        className,
      )}
    >
      {children}
    </div>
  );
}
```

**Variante Challenge** (avec Command Bar collÃ©e) :

- FocusBoard : `rounded-t-3xl` (pas `rounded-3xl`)
- Command Bar : `bg-slate-950/80 border border-white/10 border-t-0 p-6 rounded-b-3xl max-w-5xl mx-auto`

### Structure interne standard

```tsx
<FocusBoard>
  {/* 1. Bouton retour discret */}
  <Link
    href="..."
    className="text-muted-foreground hover:text-white transition-colors mb-6 inline-flex items-center gap-2"
  >
    <ArrowLeft className="h-4 w-4" /> Retour
  </Link>

  {/* 2. Titre (petite Ã©tiquette + titre star) */}
  <p className="text-sm text-muted-foreground font-mono">DÃ©fi #1234</p>
  <h1 className="text-3xl md:text-4xl font-bold text-white mt-2 mb-6">
    Titre principal
  </h1>

  {/* 3. Tags */}
  <div className="flex flex-wrap gap-2 mb-6">
    <Badge variant="outline">Tag</Badge>
  </div>

  {/* 4. Contenu principal */}
  {/* 5. BoÃ®tes internes */}
  <div className="bg-white/5 border border-white/10 rounded-xl p-4">...</div>
</FocusBoard>
```

### âš ï¸ RÃ¨gle critique â€” DnD et composants dÃ©finis inline

**Ne jamais dÃ©finir `FocusBoard` (ou tout composant wrapper) Ã  l'intÃ©rieur d'une fonction composant React** si des enfants utilisent des bibliothÃ¨ques de drag & drop (`@dnd-kit/core`, etc.).

**Pourquoi** : un composant dÃ©fini inline obtient une nouvelle rÃ©fÃ©rence Ã  chaque render. React dÃ©monte et remonte l'arbre entier, dÃ©truisant le `DndContext` et cassant le drag.

```tsx
// âŒ Interdit â€” crÃ©e un nouveau type Ã  chaque render
export function MyPage() {
  const FocusBoard = ({ children }) => <div>{children}</div>; // â† BUG dnd-kit
  return (
    <FocusBoard>
      <PuzzleRenderer />
    </FocusBoard>
  );
}

// âœ… Correct â€” type stable entre les renders
function FocusBoard({ children }) {
  return <div>{children}</div>;
}
export function MyPage() {
  return (
    <FocusBoard>
      <PuzzleRenderer />
    </FocusBoard>
  );
}
```

---

## Pattern tuiles de rÃ©ponse (Glassmorphism GamifiÃ©)

Pour les pages exercice et dÃ©fi. Styles selon l'Ã©tat :

```tsx
className={cn(
  // Base
  "rounded-2xl py-6 md:py-8 text-2xl font-medium text-white cursor-pointer transition-all text-center border-2",
  // Repos
  !hasSubmitted && !isSelected && "bg-white/10 border-white/20 hover:bg-white/20 hover:border-white/40 hover:-translate-y-1",
  // SÃ©lectionnÃ©
  !hasSubmitted && isSelected && "border-primary bg-primary/20 shadow-[0_0_20px_hsl(var(--primary)/0.3)]",
  // Correct aprÃ¨s validation
  showCorrect && "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]",
  // Incorrect aprÃ¨s validation
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
{/* Bandeau rÃ©sultat */}
<div className="rounded-xl p-4 font-semibold text-lg flex items-center gap-3
                bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">

{/* Explication â€” Fiche de savoir */}
<div className="bg-primary/5 border-l-4 border-primary rounded-r-xl p-5 mt-6">
  <Lightbulb className="text-primary" />
  <h4 className="font-semibold text-primary mb-2">Explication</h4>
  <p className="text-slate-200 text-lg">...</p>
</div>

{/* Boutons d'action â€” hiÃ©rarchie claire */}
{/* Primaire (continuer) */}
<Button className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 rounded-xl hover:-translate-y-0.5">
{/* Secondaire (retour) */}
<Button className="bg-transparent border border-white/10 text-muted-foreground hover:bg-white/5 hover:text-white rounded-xl">
```

---

## Bouton Indice (style Â« bouÃ©e de sauvetage Â»)

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

DÃ©finie dans `globals.css`. Ajoute profondeur et effet de survol (sweep + Ã©lÃ©vation) aux cartes.

```tsx
<Card className="card-spatial-depth">...</Card>
```

- Ã‰lÃ©vation `translateY(-4px)` au hover
- Sweep de lumiÃ¨re via `::before`
- Ombre `primary/30` adaptative au thÃ¨me
- Reduced-motion dÃ©jÃ  gÃ©rÃ© (dÃ©sactivÃ© si `prefers-reduced-motion`)

---

## Composants UI (shadcn/ui)

Tous dans `components/ui/`. BasÃ©s sur Radix UI â€” accessibilitÃ© WCAG incluse.

| Composant                                | Usage                                                                                  |
| ---------------------------------------- | -------------------------------------------------------------------------------------- |
| `Button`                                 | Variants: `default`, `outline`, `ghost`, `destructive`, `secondary`, `link`            |
| `Card` + `CardHeader/Content/Footer`     | Conteneurs avec sÃ©paration visuelle                                                   |
| `Dialog` + `DialogTrigger/Content/Title` | Modales accessibles                                                                    |
| `Input`                                  | **Obligatoire** pour tous les `<input type="text/email/â€¦">` â€” jamais `<input>` raw |
| `Textarea`                               | **Obligatoire** pour tous les `<textarea>` â€” jamais `<textarea>` raw                 |
| `Select` + `SelectTrigger/Content/Item`  | SÃ©lecteurs                                                                            |
| `Badge`                                  | Ã‰tiquettes visuelles                                                                  |
| `Progress`                               | Barres de progression                                                                  |
| `Skeleton`                               | Placeholder de chargement â€” intÃ©grÃ© dans `DashboardWidgetSkeleton`                 |

### DashboardWidgetSkeleton

Squelette gÃ©nÃ©rique pour les widgets du dashboard â€” Ã©vite les implÃ©mentations ad-hoc.

```tsx
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";

// Squelette par dÃ©faut (2 lignes de texte)
<DashboardWidgetSkeleton />

// Avec contenu personnalisÃ©
<DashboardWidgetSkeleton titleWidth="w-32">
  <Skeleton className="h-32 w-full" />
</DashboardWidgetSkeleton>
```

---

## Templates

Templates de page disponibles dans `frontend/docs/templates/` :

- `PAGE_LIST_TEMPLATE.md` â€” page liste avec filtres et pagination

---

## RÃ©fÃ©rences

- Composants : `frontend/components/layout/`
- Templates : `frontend/docs/templates/`
- [AccessibilitÃ©](ACCESSIBILITY.md) â€” WCAG AAA et raccourcis clavier
- [Architecture](ARCHITECTURE.md) â€” structure complÃ¨te du projet
