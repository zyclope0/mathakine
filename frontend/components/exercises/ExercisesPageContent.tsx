"use client";

import { useMemo, useEffect } from "react";
import { useContentListPageController } from "@/hooks/useContentListPageController";
import { useSearchParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useExercises } from "@/hooks/useExercises";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UnifiedExerciseGenerator } from "@/components/exercises/UnifiedExerciseGenerator";
import { EXERCISE_TYPE_STYLES, AGE_GROUPS } from "@/lib/constants/exercises";
import { contentListTotalPages } from "@/lib/contentList/pageHelpers";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { ContentListProgressiveFilterToolbar } from "@/components/shared/ContentListProgressiveFilterToolbar";
import { useCompletedExercises } from "@/hooks/useCompletedItems";
import dynamic from "next/dynamic";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader } from "@/components/layout";
import { ApiClientError } from "@/lib/api/client";
import { debugLog } from "@/lib/utils/debug";
import { STORAGE_KEYS } from "@/lib/storage";
import { buildExercisePageFilters } from "@/lib/exercises/buildExercisePageFilters";
import { buildExercisePageToolbarLabels } from "@/lib/exercises/exercisePageToolbarLabels";
import { EXERCISES_PAGE_ITEMS_PER_PAGE } from "@/lib/exercises/exercisesPageConstants";
import { ExercisesResultsView } from "@/components/exercises/ExercisesResultsView";

const ExerciseModal = dynamic(
  () =>
    import("@/components/exercises/ExerciseModal").then((mod) => ({ default: mod.ExerciseModal })),
  {
    loading: () => null,
  }
);

export function ExercisesPageContent() {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    typeFilter: exerciseTypeFilter,
    setTypeFilter: setExerciseTypeFilter,
    ageFilter: ageGroupFilter,
    setAgeFilter: setAgeGroupFilter,
    searchQuery,
    setSearchQuery,
    filtersPanelOpen,
    setFiltersPanelOpen,
    hideCompleted,
    setHideCompleted,
    selectedItemId: selectedExerciseId,
    isModalOpen,
    currentPage,
    setCurrentPage,
    viewMode,
    setViewMode,
    handleFilterChange,
    handlePageChange,
    orderFilter,
    handleOrderChange,
    hasActiveFilters,
    advancedActiveCount,
    clearFilters,
    clearTypeFilter,
    clearAgeFilter,
    openItem,
    handleModalOpenChange,
  } = useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder });
  const { isCompleted } = useCompletedExercises();

  const filters = useMemo(
    () =>
      buildExercisePageFilters({
        itemsPerPage: EXERCISES_PAGE_ITEMS_PER_PAGE,
        currentPage,
        exerciseTypeFilter,
        ageGroupFilter,
        searchQuery,
        orderFilter,
        hideCompleted,
      }),
    [exerciseTypeFilter, ageGroupFilter, searchQuery, orderFilter, currentPage, hideCompleted]
  );

  useEffect(() => {
    const generated = searchParams.get("generated");
    if (generated === "true") {
      void queryClient.invalidateQueries({ queryKey: ["exercises"] });
      const newSearchParams = new URLSearchParams(searchParams.toString());
      newSearchParams.delete("generated");
      const newUrl = newSearchParams.toString()
        ? `${window.location.pathname}?${newSearchParams.toString()}`
        : window.location.pathname;
      router.replace(newUrl, { scroll: false });
    }
  }, [searchParams, queryClient, router]);

  const { exercises, total, hasMore, isLoading, isFetching, error } = useExercises(filters);

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

  const totalPages = contentListTotalPages(total, EXERCISES_PAGE_ITEMS_PER_PAGE);

  const toolbarLabels = useMemo(() => buildExercisePageToolbarLabels(t), [t]);

  const listHeaderTitle = useMemo(
    () => (
      <>
        {total === 1 ? t("list.count", { count: total }) : t("list.countPlural", { count: total })}
        {isFetching && (
          <span className="ml-2 text-sm text-muted-foreground animate-pulse">
            ({t("list.loading", { default: "chargement..." })})
          </span>
        )}
      </>
    ),
    [total, isFetching, t]
  );

  return (
    <ProtectedRoute>
      <PageLayout compact>
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
          onOrderChange={handleOrderChange}
          hideCompleted={hideCompleted}
          onHideCompletedChange={setHideCompleted}
          hideCompletedFieldId="hide-completed"
          getTypeDisplay={getTypeDisplay}
          getAgeDisplay={getAgeDisplay}
          onResetAll={clearFilters}
          onFilterAdjust={handleFilterChange}
          onClearTypeFilter={clearTypeFilter}
          onClearAgeFilter={clearAgeFilter}
          hasResettableState={hasActiveFilters}
          advancedActiveCount={advancedActiveCount}
          showTypeChipsInline
        />

        <UnifiedExerciseGenerator
          onExerciseGenerated={() => {
            void queryClient.invalidateQueries({ queryKey: ["exercises"] });
            void queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
          }}
        />

        <ExercisesResultsView
          t={t}
          listHeaderTitle={listHeaderTitle}
          isLoading={isLoading}
          error={error}
          exercises={exercises}
          searchQuery={searchQuery}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          totalPages={totalPages}
          currentPage={currentPage}
          onPageChange={handlePageChange}
          itemsPerPage={EXERCISES_PAGE_ITEMS_PER_PAGE}
          totalItems={total}
          isCompleted={isCompleted}
          openItem={openItem}
          getTypeDisplay={getTypeDisplay}
          getAgeDisplay={getAgeDisplay}
        />

        <ExerciseModal
          exerciseId={selectedExerciseId}
          open={isModalOpen}
          onOpenChange={handleModalOpenChange}
          onExerciseCompleted={() => {
            void queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
          }}
        />
      </PageLayout>
    </ProtectedRoute>
  );
}
