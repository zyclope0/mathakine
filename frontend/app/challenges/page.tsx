"use client";

import { useMemo, Suspense } from "react";
import { useContentListPageController } from "@/hooks/useContentListPageController";
import { useChallenges } from "@/hooks/useChallenges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ChallengeCard } from "@/components/challenges/ChallengeCard";
import { AIGenerator } from "@/components/challenges/AIGenerator";
import { useQueryClient } from "@tanstack/react-query";
import {
  CHALLENGE_TYPE_STYLES,
  AGE_GROUPS,
  type ChallengeType,
  type AgeGroup,
} from "@/lib/constants/challenges";
import { useChallengeTranslations } from "@/hooks/useChallengeTranslations";
import type { ChallengeFilters } from "@/hooks/useChallenges";
import { Puzzle } from "lucide-react";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader } from "@/components/layout";
import { ChallengesListLoadingShell } from "@/components/shared/ListLoadingShells";
import { ApiClientError } from "@/lib/api/client";
import { useCompletedChallenges } from "@/hooks/useCompletedItems";
import dynamic from "next/dynamic";
import {
  ContentListProgressiveFilterToolbar,
  type ContentListFilterToolbarLabels,
} from "@/components/shared/ContentListProgressiveFilterToolbar";
import { ContentListResultsSection } from "@/components/shared/ContentListResultsSection";
import { contentListTotalPages } from "@/lib/contentList/pageHelpers";
import { STORAGE_KEYS } from "@/lib/storage";

// Lazy load modal pour la vue liste
const ChallengeModal = dynamic(
  () =>
    import("@/components/challenges/ChallengeModal").then((mod) => ({
      default: mod.ChallengeModal,
    })),
  {
    loading: () => null,
  }
);

const ITEMS_PER_PAGE = 15;

function ChallengesPageContent() {
  const t = useTranslations("challenges");
  const { getTypeDisplay, getAgeDisplay } = useChallengeTranslations();
  const queryClient = useQueryClient();
  const {
    typeFilter: challengeTypeFilter,
    setTypeFilter: setChallengeTypeFilter,
    ageFilter: ageGroupFilter,
    setAgeFilter: setAgeGroupFilter,
    searchQuery,
    setSearchQuery,
    filtersPanelOpen,
    setFiltersPanelOpen,
    hideCompleted,
    setHideCompleted,
    selectedItemId: selectedChallengeId,
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
  } = useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefChallengeOrder });
  const { isCompleted } = useCompletedChallenges();

  // Optimiser les filtres avec useMemo
  const filters: ChallengeFilters = useMemo(() => {
    const f: ChallengeFilters = {
      limit: ITEMS_PER_PAGE,
      skip: (currentPage - 1) * ITEMS_PER_PAGE,
    };

    if (challengeTypeFilter !== "all") {
      f.challenge_type = challengeTypeFilter as ChallengeType;
    }

    if (ageGroupFilter !== "all") {
      f.age_group = ageGroupFilter as AgeGroup;
    }

    // Ajouter la recherche côté serveur si fournie
    if (searchQuery.trim()) {
      f.search = searchQuery.trim();
    }

    f.order = orderFilter;
    f.hide_completed = hideCompleted;

    return f;
  }, [challengeTypeFilter, ageGroupFilter, searchQuery, orderFilter, currentPage, hideCompleted]);

  const { challenges, total, isLoading, error } = useChallenges(filters);

  // Calculer le nombre total de pages à partir du total réel
  const totalPages = contentListTotalPages(total, ITEMS_PER_PAGE);

  const toolbarLabels: ContentListFilterToolbarLabels = useMemo(
    () => ({
      filterButton: t("filters.moreFilters"),
      filterButtonAriaExpand: t("filters.expandFilters"),
      filterButtonAriaCollapse: t("filters.collapseFilters"),
      advancedRegionLabel: t("filters.advancedFiltersRegion"),
      reset: t("filters.reset"),
      typeHeading: t("filters.challengeType"),
      allTypes: t("filters.allTypes"),
      ageGroup: t("filters.ageGroup"),
      allAgesPlaceholder: t("filters.allGroups"),
      orderLabel: t("filters.order"),
      orderAria: t("filters.order"),
      orderRandom: t("filters.orderRandom"),
      orderRecent: t("filters.orderRecent"),
      hideCompleted: t("filters.hideCompleted"),
      searchPlaceholder: t("search.placeholder", { default: "Rechercher un défi..." }),
      searchAriaLabel: t("search.placeholder", { default: "Rechercher un défi..." }),
      activeFiltersSummary: t("filters.activeFiltersSummary"),
      removeTypeChip: t("filters.removeTypeFilter"),
      removeAgeChip: t("filters.removeAgeFilter"),
    }),
    [t]
  );

  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout compact>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} icon={Puzzle} />

        <ContentListProgressiveFilterToolbar
          labels={toolbarLabels}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchPageReset={() => setCurrentPage(1)}
          panelOpen={filtersPanelOpen}
          onPanelOpenChange={setFiltersPanelOpen}
          showTypeChipsInline
          typeFilterValue={challengeTypeFilter}
          onTypeFilterChange={setChallengeTypeFilter}
          typeStyles={CHALLENGE_TYPE_STYLES}
          ageFilterValue={ageGroupFilter}
          onAgeFilterChange={setAgeGroupFilter}
          ageGroupValues={Object.values(AGE_GROUPS)}
          orderValue={orderFilter}
          onOrderChange={handleOrderChange}
          hideCompleted={hideCompleted}
          onHideCompletedChange={setHideCompleted}
          hideCompletedFieldId="hide-completed-challenges"
          getTypeDisplay={getTypeDisplay}
          getAgeDisplay={getAgeDisplay}
          onResetAll={clearFilters}
          onFilterAdjust={handleFilterChange}
          onClearTypeFilter={clearTypeFilter}
          onClearAgeFilter={clearAgeFilter}
          hasResettableState={hasActiveFilters}
          advancedActiveCount={advancedActiveCount}
        />

        {/* Générateur IA — Toolbar compacte */}
        <AIGenerator
          compact
          onChallengeGenerated={() => {
            queryClient.invalidateQueries({ queryKey: ["challenges"] });
            queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
          }}
        />

        <ContentListResultsSection
          isLoading={isLoading}
          error={error}
          errorTitle={t("list.error.title", { default: "Erreur de chargement" })}
          errorDescription={
            error instanceof ApiClientError
              ? error.message
              : t("list.error.description", { default: "Impossible de charger les défis" })
          }
          errorIcon={Puzzle}
          loadingLabel={t("list.loading")}
          listHeaderTitle={
            <>
              {total === 0
                ? t("list.empty")
                : total === 1
                  ? t("list.count", { count: total, default: "1 défi" })
                  : t("list.countPlural", { count: total, default: `${total} défis` })}
            </>
          }
          itemCount={challenges.length}
          emptyTitle={
            searchQuery.trim()
              ? t("search.noResults", {
                  query: searchQuery,
                  default: `Aucun résultat pour "${searchQuery}"`,
                })
              : t("list.empty")
          }
          emptyDescription={searchQuery.trim() ? "" : t("list.emptyHint")}
          emptyIcon={Puzzle}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          ariaLabelGrid={t("viewGrid")}
          ariaLabelList={t("viewList")}
          renderGrid={() =>
            challenges.map((challenge, index) => (
              <div key={challenge.id} className={`${getStaggerDelay(index)} w-full`}>
                <ChallengeCard challenge={challenge} completed={isCompleted(challenge.id)} />
              </div>
            ))
          }
          renderList={() => (
            /* Vue Liste Compacte */
            <div className="space-y-2">
              {challenges.map((challenge) => {
                const typeKey =
                  challenge.challenge_type?.toLowerCase() as keyof typeof CHALLENGE_TYPE_STYLES;
                const { icon: TypeIcon } = CHALLENGE_TYPE_STYLES[typeKey] || { icon: Puzzle };
                return (
                  <CompactListItem
                    key={challenge.id}
                    title={challenge.title}
                    subtitle={challenge.description || challenge.question || ""}
                    TypeIcon={TypeIcon}
                    aiGenerated={isAiGenerated(challenge)}
                    completed={isCompleted(challenge.id)}
                    typeDisplay={getTypeDisplay(challenge.challenge_type)}
                    ageDisplay={getAgeDisplay(challenge.age_group)}
                    onClick={() => openItem(challenge.id)}
                  />
                );
              })}
            </div>
          )}
          totalPages={totalPages}
          currentPage={currentPage}
          onPageChange={handlePageChange}
          itemsPerPage={ITEMS_PER_PAGE}
          totalItems={total}
        />

        {/* Modal pour la vue liste */}
        <ChallengeModal
          challengeId={selectedChallengeId}
          open={isModalOpen}
          onOpenChange={handleModalOpenChange}
        />
      </PageLayout>
    </ProtectedRoute>
  );
}

export default function ChallengesPage() {
  return (
    <Suspense
      fallback={
        <ProtectedRoute requireFullAccess>
          <PageLayout compact>
            <ChallengesListLoadingShell />
          </PageLayout>
        </ProtectedRoute>
      }
    >
      <ChallengesPageContent />
    </Suspense>
  );
}
