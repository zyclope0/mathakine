"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useChallenges } from "@/hooks/useChallenges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ChallengeCard } from "@/components/challenges/ChallengeCard";
import { AIGenerator } from "@/components/challenges/AIGenerator";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Pagination } from "@/components/ui/pagination";
import {
  CHALLENGE_TYPE_STYLES,
  AGE_GROUPS,
  type ChallengeType,
  type AgeGroup,
} from "@/lib/constants/challenges";
import { useChallengeTranslations } from "@/hooks/useChallengeTranslations";
import type { ChallengeFilters } from "@/hooks/useChallenges";
import { Puzzle, LayoutGrid, List } from "lucide-react";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, PageGrid, EmptyState } from "@/components/layout";
import { Skeleton } from "@/components/ui/skeleton";
import { ContentListSkeleton } from "@/components/shared/ContentListSkeleton";
import { ChallengesListLoadingShell } from "@/components/shared/ListLoadingShells";
import { ApiClientError } from "@/lib/api/client";
import { useCompletedChallenges } from "@/hooks/useCompletedItems";
import dynamic from "next/dynamic";
import {
  ContentListProgressiveFilterToolbar,
  type ContentListFilterToolbarLabels,
} from "@/components/shared/ContentListProgressiveFilterToolbar";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";
import { getLocalString, removeLocalKey, setLocalString, STORAGE_KEYS } from "@/lib/storage";

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

function isValidStoredContentListOrder(value: string | null): value is ContentListOrder {
  return value === CONTENT_LIST_ORDER.RANDOM || value === CONTENT_LIST_ORDER.RECENT;
}

function ChallengesPageContent() {
  const t = useTranslations("challenges");
  const { getTypeDisplay, getAgeDisplay } = useChallengeTranslations();
  const queryClient = useQueryClient();
  const [challengeTypeFilter, setChallengeTypeFilter] = useState<string>("all");
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [orderFilter, setOrderFilter] = useState<ContentListOrder>(CONTENT_LIST_ORDER.RANDOM);
  const [filtersPanelOpen, setFiltersPanelOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedChallengeId, setSelectedChallengeId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hideCompleted, setHideCompleted] = useState(false);
  const { isCompleted } = useCompletedChallenges();

  useEffect(() => {
    const raw = getLocalString(STORAGE_KEYS.prefChallengeOrder);
    if (isValidStoredContentListOrder(raw)) {
      // Restauration post-hydratation uniquement (pas de lecture storage dans l’initializer useState).
      // eslint-disable-next-line react-hooks/set-state-in-effect -- sync exigée pour appliquer la préférence au plus tôt après montage client
      setOrderFilter(raw);
    }
  }, []);

  const handleOrderChange = (value: ContentListOrder) => {
    setOrderFilter(value);
    setLocalString(STORAGE_KEYS.prefChallengeOrder, value);
  };

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
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE) || 1;

  const hasActiveFilters =
    challengeTypeFilter !== "all" ||
    ageGroupFilter !== "all" ||
    searchQuery.trim() !== "" ||
    orderFilter !== CONTENT_LIST_ORDER.RANDOM ||
    hideCompleted;

  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setChallengeTypeFilter("all");
    setAgeGroupFilter("all");
    setSearchQuery("");
    setOrderFilter(CONTENT_LIST_ORDER.RANDOM);
    setHideCompleted(false);
    setCurrentPage(1);
    removeLocalKey(STORAGE_KEYS.prefChallengeOrder);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll vers le haut de la liste
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const advancedActiveCount =
    (challengeTypeFilter !== "all" ? 1 : 0) + (ageGroupFilter !== "all" ? 1 : 0);

  const toolbarLabels: ContentListFilterToolbarLabels = useMemo(
    () => ({
      filterButton: t("filters.title"),
      filterButtonAriaExpand: t("filters.expandFilters"),
      filterButtonAriaCollapse: t("filters.collapseFilters"),
      advancedRegionLabel: t("filters.advancedFiltersRegion"),
      reset: t("filters.reset"),
      typeHeading: t("filters.challengeType"),
      allTypes: t("filters.allTypes"),
      ageGroup: t("filters.ageGroup"),
      allAgesPlaceholder: t("filters.allGroups"),
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
          onClearTypeFilter={() => {
            setChallengeTypeFilter("all");
            handleFilterChange();
          }}
          onClearAgeFilter={() => {
            setAgeGroupFilter("all");
            handleFilterChange();
          }}
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

        {/* Liste des défis */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-2 gap-3">
            {isLoading ? (
              <div className="text-lg md:text-xl font-semibold min-h-11 flex items-center">
                <h2 className="sr-only">{t("list.loading")}</h2>
                <Skeleton className="h-7 w-44 md:w-56 max-w-[min(100%,16rem)]" aria-hidden />
              </div>
            ) : (
              <h2 className="text-lg md:text-xl font-semibold">
                {total === 0
                  ? t("list.empty")
                  : total === 1
                    ? t("list.count", { count: total, default: "1 défi" })
                    : t("list.countPlural", { count: total, default: `${total} défis` })}
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
                  : t("list.error.description", { default: "Impossible de charger les défis" })
              }
              icon={Puzzle}
            />
          ) : isLoading ? (
            <ContentListSkeleton variant={viewMode} loadingLabel={t("list.loading")} />
          ) : challenges.length === 0 ? (
            <EmptyState
              title={
                searchQuery.trim()
                  ? t("search.noResults", {
                      query: searchQuery,
                      default: `Aucun résultat pour "${searchQuery}"`,
                    })
                  : t("list.empty")
              }
              description={searchQuery.trim() ? "" : t("list.emptyHint")}
              icon={Puzzle}
            />
          ) : (
            <>
              {viewMode === "grid" ? (
                <PageGrid
                  columns={{ mobile: 1, tablet: 2, desktop: 3 }}
                  gap="sm"
                  className="md:gap-4"
                >
                  {challenges.map((challenge, index) => (
                    <div key={challenge.id} className={`${getStaggerDelay(index)} h-full`}>
                      <ChallengeCard challenge={challenge} completed={isCompleted(challenge.id)} />
                    </div>
                  ))}
                </PageGrid>
              ) : (
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
                        onClick={() => {
                          setSelectedChallengeId(challenge.id);
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
                  />
                </div>
              )}
            </>
          )}
        </PageSection>

        {/* Modal pour la vue liste */}
        <ChallengeModal
          challengeId={selectedChallengeId}
          open={isModalOpen}
          onOpenChange={(open) => {
            setIsModalOpen(open);
            if (!open) setSelectedChallengeId(null);
          }}
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
