"use client";

import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { PageGrid } from "@/components/layout/PageGrid";
import { PageSection } from "@/components/layout/PageSection";

const DEFAULT_GRID_COUNT = 9;
const DEFAULT_LIST_COUNT = 6;

/** Hit zone 44px — carrés filtres type (alignés avec les vrais boutons). */
const FILTER_ICON_BOX = "h-11 w-11 min-h-[44px] min-w-[44px] shrink-0 rounded-md";

/**
 * Barre filtres fantôme (route loading / alignement visuel avec la toolbar réelle).
 * Pas d’interaction — structure stable pour réduire le saut de mise en page.
 */
export function ListPageFiltersSkeleton({
  className,
  showOrderSelectSkeleton = false,
}: {
  className?: string;
  /** Deuxième select (ordre) comme sur la page défis. */
  showOrderSelectSkeleton?: boolean;
}) {
  return (
    <div
      className={cn(
        "p-4 rounded-xl border border-border/50 bg-card/40 backdrop-blur-md flex flex-col md:flex-row md:flex-wrap md:items-center gap-3 md:gap-4",
        className
      )}
      aria-hidden="true"
    >
      <div className="flex items-center gap-2 flex-shrink-0">
        <Skeleton className={FILTER_ICON_BOX} />
        <Skeleton className="h-4 w-24" variant="text" />
      </div>
      <Skeleton className="h-11 w-full min-h-[44px] flex-1 min-w-0 rounded-md" />
      <div className="flex flex-wrap items-center gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className={FILTER_ICON_BOX} />
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Skeleton className="h-11 min-h-[44px] w-[130px] rounded-md" />
        {showOrderSelectSkeleton ? (
          <Skeleton className="h-11 min-h-[44px] w-[100px] rounded-md" />
        ) : null}
      </div>
      <div className="flex items-center gap-2">
        <Skeleton className="h-6 w-10 rounded-full" />
        <Skeleton className="h-4 w-28" variant="text" />
      </div>
    </div>
  );
}

/** Rangée type CompactListItem (liste dense). */
function ContentListRowSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex gap-3 rounded-lg border border-border/50 bg-card/30 p-3 min-h-[44px] items-center",
        className
      )}
    >
      <Skeleton variant="circular" className="h-10 w-10 shrink-0" />
      <div className="flex-1 space-y-2 min-w-0">
        <Skeleton className="h-4 max-w-md w-full" variant="text" />
        <Skeleton className="h-3 max-w-lg w-full" variant="text" />
      </div>
    </div>
  );
}

/** Carte type grille (structure proche ExerciseCard / ChallengeCard). */
function ContentGridCardSkeleton() {
  return (
    <div
      className={cn(
        "rounded-xl border border-border/50 bg-card/40 flex flex-col h-full min-h-[220px] overflow-hidden"
      )}
      aria-hidden="true"
    >
      <div className="p-6 flex flex-col flex-1 space-y-3">
        <Skeleton className="h-5 w-[85%]" variant="text" />
        <SkeletonTextLines />
        <div className="flex flex-wrap gap-2 pt-1">
          <Skeleton className="h-6 w-16 rounded-full" />
          <Skeleton className="h-6 w-20 rounded-full" />
        </div>
        <div className="flex-1" />
        <div className="flex justify-between items-center text-sm pt-2 border-t border-border/30">
          <Skeleton className="h-4 w-20" variant="text" />
          <Skeleton className="h-8 w-24 rounded-full" />
        </div>
      </div>
    </div>
  );
}

function SkeletonTextLines() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-3 w-full" variant="text" />
      <Skeleton className="h-3 w-full" variant="text" />
      <Skeleton className="h-3 w-4/5" variant="text" />
    </div>
  );
}

export interface ContentListSkeletonProps {
  variant: "grid" | "list";
  /** Nombre de placeholders (défaut: 9 grille, 6 liste). */
  count?: number;
  /** Libellé vocalisé pour le statut de chargement. */
  loadingLabel: string;
  className?: string;
}

/**
 * Skeleton de liste pour exercices / défis — aligné sur PageGrid + cartes réelles.
 */
export function ContentListSkeleton({
  variant,
  count,
  loadingLabel,
  className,
}: ContentListSkeletonProps) {
  const n = count ?? (variant === "grid" ? DEFAULT_GRID_COUNT : DEFAULT_LIST_COUNT);

  return (
    <div role="status" aria-busy="true" aria-label={loadingLabel} className={cn(className)}>
      {variant === "grid" ? (
        <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="sm" className="md:gap-4">
          {Array.from({ length: n }).map((_, i) => (
            <div key={i} className="h-full">
              <ContentGridCardSkeleton />
            </div>
          ))}
        </PageGrid>
      ) : (
        <div className="space-y-2">
          {Array.from({ length: n }).map((_, i) => (
            <ContentListRowSkeleton key={i} />
          ))}
        </div>
      )}
    </div>
  );
}

export interface ListRouteLoadingLayoutProps {
  loadingLabel: string;
  listVariant?: "grid" | "list";
  /** Espace réservé sous la toolbar (générateur). */
  showGeneratorSlot?: boolean;
  showOrderSelectSkeleton?: boolean;
}

/**
 * Coquille de chargement route (Suspense / loading.tsx) : header réel + structure liste.
 */
export function ListRouteLoadingLayout({
  loadingLabel,
  listVariant = "grid",
  showGeneratorSlot = true,
  showOrderSelectSkeleton = false,
}: ListRouteLoadingLayoutProps) {
  return (
    <>
      <ListPageFiltersSkeleton className="mb-4" showOrderSelectSkeleton={showOrderSelectSkeleton} />
      {showGeneratorSlot && (
        <div
          className="mb-4 h-14 md:h-16 rounded-xl border border-border/50 bg-muted/25"
          aria-hidden="true"
        />
      )}
      <PageSection className="space-y-3">
        <div className="flex items-center justify-between mb-2">
          <Skeleton className="h-7 w-48 md:w-64" variant="text" />
          <div className="flex gap-1 rounded-lg border border-border/50 p-1">
            <Skeleton className="h-11 w-11 min-h-[44px] min-w-[44px] rounded-md" />
            <Skeleton className="h-11 w-11 min-h-[44px] min-w-[44px] rounded-md" />
          </div>
        </div>
        <ContentListSkeleton variant={listVariant} loadingLabel={loadingLabel} />
      </PageSection>
    </>
  );
}
