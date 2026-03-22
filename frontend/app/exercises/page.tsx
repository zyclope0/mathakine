"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useExercises } from "@/hooks/useExercises";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ExerciseCard } from "@/components/exercises/ExerciseCard";
import { UnifiedExerciseGenerator } from "@/components/exercises/UnifiedExerciseGenerator";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
import { Button } from "@/components/ui/button";
import { Pagination } from "@/components/ui/pagination";
import { EXERCISE_TYPE_STYLES, AGE_GROUPS } from "@/lib/constants/exercises";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { LayoutGrid, List } from "lucide-react";
import {
  ContentListProgressiveFilterToolbar,
  type ContentListFilterToolbarLabels,
} from "@/components/shared/ContentListProgressiveFilterToolbar";
import { useCompletedExercises } from "@/hooks/useCompletedItems";
import dynamic from "next/dynamic";

// Lazy load modal pour la vue liste
const ExerciseModal = dynamic(
  () =>
    import("@/components/exercises/ExerciseModal").then((mod) => ({ default: mod.ExerciseModal })),
  {
    loading: () => null,
  }
);
import type { ExerciseFilters } from "@/hooks/useExercises";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, PageGrid, EmptyState } from "@/components/layout";
import { Skeleton } from "@/components/ui/skeleton";
import { ContentListSkeleton } from "@/components/shared/ContentListSkeleton";
import { ExercisesListLoadingShell } from "@/components/shared/ListLoadingShells";
import { ApiClientError } from "@/lib/api/client";
import { debugLog } from "@/lib/utils/debug";

const ITEMS_PER_PAGE = 15;

function ExercisesPageContent() {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [exerciseTypeFilter, setExerciseTypeFilter] = useState<string>("all");
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hideCompleted, setHideCompleted] = useState(false);
  const [orderFilter, setOrderFilter] = useState<ContentListOrder>(CONTENT_LIST_ORDER.RANDOM);
  const [filtersPanelOpen, setFiltersPanelOpen] = useState(false);
  const { isCompleted } = useCompletedExercises();

  // Réinitialiser à la page 1 quand les filtres changent
  const filters: ExerciseFilters = useMemo(() => {
    const f: ExerciseFilters = {
      limit: ITEMS_PER_PAGE,
      skip: (currentPage - 1) * ITEMS_PER_PAGE,
    };

    if (exerciseTypeFilter !== "all") {
      f.exercise_type = exerciseTypeFilter;
    }

    if (ageGroupFilter !== "all") {
      f.age_group = ageGroupFilter;
    }

    // Ajouter la recherche côté serveur si fournie
    if (searchQuery.trim()) {
      f.search = searchQuery.trim();
    }

    f.order = orderFilter;
    f.hide_completed = hideCompleted;

    return f;
  }, [exerciseTypeFilter, ageGroupFilter, searchQuery, orderFilter, currentPage, hideCompleted]);

  // Détecter le paramètre generated=true et rafraîchir la liste
  useEffect(() => {
    const generated = searchParams.get("generated");
    if (generated === "true") {
      // Invalider les queries pour forcer le refetch avec les bons filtres
      queryClient.invalidateQueries({ queryKey: ["exercises"] });
      // Retirer le paramètre de l'URL sans recharger la page
      const newSearchParams = new URLSearchParams(searchParams.toString());
      newSearchParams.delete("generated");
      const newUrl = newSearchParams.toString()
        ? `${window.location.pathname}?${newSearchParams.toString()}`
        : window.location.pathname;
      router.replace(newUrl, { scroll: false });
    }
  }, [searchParams, queryClient, router]);

  const { exercises, total, hasMore, isLoading, isFetching, error } = useExercises(filters);

  // Log pour déboguer (uniquement en développement)
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      debugLog("[ExercisesPage] State:", {
        exercisesCount: exercises?.length || 0,
        total,
        hasMore,
        isLoading,
        error: error instanceof ApiClientError ? error.message : error ? String(error) : null,
        filters,
        currentPage,
      });
    }
  }, [exercises, total, hasMore, isLoading, error, filters, currentPage]);

  // Calculer le nombre total de pages à partir du total réel
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE) || 1;

  // Réinitialiser à la page 1 quand les filtres changent
  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const hasActiveFilters =
    exerciseTypeFilter !== "all" ||
    ageGroupFilter !== "all" ||
    searchQuery.trim() !== "" ||
    orderFilter !== CONTENT_LIST_ORDER.RANDOM ||
    hideCompleted;

  const clearFilters = () => {
    setExerciseTypeFilter("all");
    setAgeGroupFilter("all");
    setSearchQuery("");
    setOrderFilter(CONTENT_LIST_ORDER.RANDOM);
    setHideCompleted(false);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll vers le haut de la liste
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const advancedActiveCount =
    (exerciseTypeFilter !== "all" ? 1 : 0) + (ageGroupFilter !== "all" ? 1 : 0);

  const toolbarLabels: ContentListFilterToolbarLabels = useMemo(
    () => ({
      filterButton: t("filters.title"),
      filterButtonAriaExpand: t("filters.expandFilters"),
      filterButtonAriaCollapse: t("filters.collapseFilters"),
      advancedRegionLabel: t("filters.advancedFiltersRegion"),
      reset: t("filters.reset"),
      typeHeading: t("filters.exerciseType"),
      allTypes: t("filters.allTypes"),
      ageGroup: t("filters.ageGroup"),
      allAgesPlaceholder: t("filters.allAgeGroups"),
      orderAria: t("filters.order"),
      orderRandom: t("filters.orderRandom"),
      orderRecent: t("filters.orderRecent"),
      hideCompleted: t("filters.hideCompleted"),
      searchPlaceholder: t("search.placeholder"),
      searchAriaLabel: t("search.placeholder"),
      activeFiltersSummary: t("filters.activeFiltersSummary"),
      removeTypeChip: t("filters.removeTypeFilter"),
      removeAgeChip: t("filters.removeAgeFilter"),
    }),
    [t]
  );

  return (
    <ProtectedRoute>
      <PageLayout compact>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} />

        <ContentListProgressiveFilterToolbar
          labels={toolbarLabels}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchPageReset={() => setCurrentPage(1)}
          panelOpen={filtersPanelOpen}
          onPanelOpenChange={setFiltersPanelOpen}
          typeFilterValue={exerciseTypeFilter}
          onTypeFilterChange={setExerciseTypeFilter}
          typeStyles={EXERCISE_TYPE_STYLES}
          ageFilterValue={ageGroupFilter}
          onAgeFilterChange={setAgeGroupFilter}
          ageGroupValues={Object.values(AGE_GROUPS)}
          orderValue={orderFilter}
          onOrderChange={setOrderFilter}
          hideCompleted={hideCompleted}
          onHideCompletedChange={setHideCompleted}
          hideCompletedFieldId="hide-completed"
          getTypeDisplay={getTypeDisplay}
          getAgeDisplay={getAgeDisplay}
          onResetAll={clearFilters}
          onFilterAdjust={handleFilterChange}
          onClearTypeFilter={() => {
            setExerciseTypeFilter("all");
            handleFilterChange();
          }}
          onClearAgeFilter={() => {
            setAgeGroupFilter("all");
            handleFilterChange();
          }}
          hasResettableState={hasActiveFilters}
          advancedActiveCount={advancedActiveCount}
        />

        {/* Générateur unifié — Toolbar compacte */}
        <UnifiedExerciseGenerator
          onExerciseGenerated={() => {
            queryClient.invalidateQueries({ queryKey: ["exercises"] });
            queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
          }}
        />

        {/* Liste des exercices */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-2 gap-3">
            {isLoading ? (
              <div className="text-lg md:text-xl font-semibold min-h-11 flex items-center">
                <h2 className="sr-only">{t("list.loading")}</h2>
                <Skeleton className="h-7 w-44 md:w-56 max-w-[min(100%,16rem)]" aria-hidden />
              </div>
            ) : (
              <h2 className="text-lg md:text-xl font-semibold">
                {total === 1
                  ? t("list.count", { count: total })
                  : t("list.countPlural", { count: total })}
                {isFetching && (
                  <span className="ml-2 text-sm text-muted-foreground animate-pulse">
                    ({t("list.loading", { default: "chargement..." })})
                  </span>
                )}
              </h2>
            )}

            {/* Toggle Vue Grille / Liste — cibles tactiles 44px */}
            <div className="flex items-center gap-1 border rounded-lg p-1 shrink-0">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="h-11 w-11 min-h-[44px] min-w-[44px] p-0"
                aria-label={t("viewGrid")}
                aria-pressed={viewMode === "grid"}
              >
                <LayoutGrid className="h-4 w-4" aria-hidden="true" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="h-11 w-11 min-h-[44px] min-w-[44px] p-0"
                aria-label={t("viewList")}
                aria-pressed={viewMode === "list"}
              >
                <List className="h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>

          {error ? (
            <EmptyState
              title={t("list.error.title", { default: "Erreur de chargement" })}
              description={
                error instanceof ApiClientError
                  ? error.message
                  : t("list.error.description", { default: "Impossible de charger les exercices" })
              }
            />
          ) : isLoading ? (
            <ContentListSkeleton variant={viewMode} loadingLabel={t("list.loading")} />
          ) : exercises.length === 0 ? (
            <EmptyState
              title={
                searchQuery.trim() ? t("search.noResults", { query: searchQuery }) : t("list.empty")
              }
              description={searchQuery.trim() ? "" : t("list.emptyHint")}
            />
          ) : (
            <>
              {viewMode === "grid" ? (
                <PageGrid
                  columns={{ mobile: 1, tablet: 2, desktop: 3 }}
                  gap="sm"
                  className="md:gap-4"
                >
                  {exercises.map((exercise, index) => (
                    <div key={exercise.id} className={`${getStaggerDelay(index)} h-full`}>
                      <ExerciseCard exercise={exercise} completed={isCompleted(exercise.id)} />
                    </div>
                  ))}
                </PageGrid>
              ) : (
                /* Vue Liste Compacte */
                <div className="space-y-2">
                  {exercises.map((exercise) => {
                    const typeKey =
                      exercise.exercise_type?.toLowerCase() as keyof typeof EXERCISE_TYPE_STYLES;
                    const { icon: TypeIcon } =
                      EXERCISE_TYPE_STYLES[typeKey] || EXERCISE_TYPE_STYLES.divers;
                    return (
                      <CompactListItem
                        key={exercise.id}
                        title={exercise.title}
                        subtitle={exercise.question}
                        TypeIcon={TypeIcon}
                        aiGenerated={isAiGenerated(exercise)}
                        completed={isCompleted(exercise.id)}
                        typeDisplay={getTypeDisplay(exercise.exercise_type)}
                        ageDisplay={getAgeDisplay(exercise.age_group)}
                        onClick={() => {
                          setSelectedExerciseId(exercise.id);
                          setIsModalOpen(true);
                        }}
                      />
                    );
                  })}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-4 pt-4 border-t border-border/50">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                    itemsPerPage={ITEMS_PER_PAGE}
                    totalItems={total}
                    showInfo={true}
                  />
                </div>
              )}
            </>
          )}
        </PageSection>

        {/* Modal pour la vue liste */}
        <ExerciseModal
          exerciseId={selectedExerciseId}
          open={isModalOpen}
          onOpenChange={(open) => {
            setIsModalOpen(open);
            if (!open) setSelectedExerciseId(null);
          }}
          onExerciseCompleted={() => {
            queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
          }}
        />
      </PageLayout>
    </ProtectedRoute>
  );
}

export default function ExercisesPage() {
  return (
    <Suspense
      fallback={
        <ProtectedRoute>
          <PageLayout compact>
            <ExercisesListLoadingShell />
          </PageLayout>
        </ProtectedRoute>
      }
    >
      <ExercisesPageContent />
    </Suspense>
  );
}
