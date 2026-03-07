"use client";

import { useState, useMemo, Suspense, useEffect } from "react";
import { useChallenges } from "@/hooks/useChallenges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ChallengeCard } from "@/components/challenges/ChallengeCard";
import { AIGenerator } from "@/components/challenges/AIGenerator";
import { useQueryClient } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Pagination } from "@/components/ui/pagination";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  CHALLENGE_TYPE_STYLES,
  AGE_GROUPS,
  type ChallengeType,
  type AgeGroup,
} from "@/lib/constants/challenges";
import { useChallengeTranslations } from "@/hooks/useChallengeTranslations";
import type { ChallengeFilters } from "@/hooks/useChallenges";
import { Filter, X, Puzzle, Search, LayoutGrid, List, EyeOff } from "lucide-react";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import {
  PageLayout,
  PageHeader,
  PageSection,
  PageGrid,
  EmptyState,
  LoadingState,
} from "@/components/layout";
import { ApiClientError } from "@/lib/api/client";
import { useCompletedChallenges } from "@/hooks/useCompletedItems";
import dynamic from "next/dynamic";

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
  const pathname = usePathname();
  const [challengeTypeFilter, setChallengeTypeFilter] = useState<string>("all");
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [orderFilter, setOrderFilter] = useState<"random" | "recent">("random");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedChallengeId, setSelectedChallengeId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hideCompleted, setHideCompleted] = useState(false);
  const { isCompleted } = useCompletedChallenges();

  // Refetch les queries de progression quand on arrive sur la page
  useEffect(() => {
    if (pathname === "/challenges") {
      queryClient.refetchQueries({ queryKey: ["completed-challenges"] });
    }
  }, [pathname, queryClient]);

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
    orderFilter !== "random" ||
    hideCompleted;

  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setChallengeTypeFilter("all");
    setAgeGroupFilter("all");
    setSearchQuery("");
    setOrderFilter("random");
    setHideCompleted(false);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll vers le haut de la liste
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout compact>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} icon={Puzzle} />

        {/* Filtres — Toolbar ultra-compacte */}
        <div className="p-4 rounded-xl border border-border/50 bg-card/40 backdrop-blur-md flex flex-col md:flex-row md:items-center gap-3 animate-fade-in-up">
          <div className="flex items-center gap-2 flex-shrink-0">
            <Filter className="h-4 w-4 text-primary" aria-hidden="true" />
            <span className="text-sm font-medium">{t("filters.title")}</span>
            {hasActiveFilters && (
              <Badge variant="secondary" className="text-xs">
                {(challengeTypeFilter !== "all" ? 1 : 0) +
                  (ageGroupFilter !== "all" ? 1 : 0) +
                  (searchQuery.trim() ? 1 : 0) +
                  (orderFilter !== "random" ? 1 : 0) +
                  (hideCompleted ? 1 : 0)}
              </Badge>
            )}
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="h-8 text-muted-foreground hover:text-foreground"
              >
                <X className="h-3.5 w-3.5 mr-1" />
                {t("filters.reset")}
              </Button>
            )}
          </div>

          <div className="relative flex-1 min-w-0">
            <Search
              className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              type="text"
              placeholder={t("search.placeholder", { default: "Rechercher un défi..." })}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-9 h-9"
              aria-label={t("search.placeholder", { default: "Rechercher un défi..." })}
            />
          </div>

          <TooltipProvider delayDuration={300}>
            <div className="flex flex-wrap items-center gap-1.5 flex-shrink-0">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={challengeTypeFilter === "all" ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setChallengeTypeFilter("all");
                      handleFilterChange();
                    }}
                    className="h-9 w-9 p-0"
                  >
                    <Filter className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">{t("filters.allTypes")}</TooltipContent>
              </Tooltip>
              <div className="w-px h-9 bg-border mx-0.5 hidden sm:block" aria-hidden="true" />
              {Object.entries(CHALLENGE_TYPE_STYLES).map(([type, { icon: Icon }]) => (
                <Tooltip key={type}>
                  <TooltipTrigger asChild>
                    <Button
                      variant={challengeTypeFilter === type ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setChallengeTypeFilter(type);
                        handleFilterChange();
                      }}
                      className="h-9 w-9 p-0"
                    >
                      <Icon className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">{getTypeDisplay(type)}</TooltipContent>
                </Tooltip>
              ))}
            </div>
          </TooltipProvider>

          <Select
            value={ageGroupFilter}
            onValueChange={(value) => {
              setAgeGroupFilter(value);
              handleFilterChange();
            }}
          >
            <SelectTrigger id="filter-age-group" className="h-9 w-[100px] md:w-[110px] flex-shrink-0">
              <SelectValue placeholder={t("filters.allGroups")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("filters.allGroups")}</SelectItem>
                {Object.values(AGE_GROUPS).map((value) => (
                  <SelectItem key={value} value={value}>
                    {getAgeDisplay(value)}
                  </SelectItem>
                ))}
              </SelectContent>
          </Select>

          <Select
            value={orderFilter}
            onValueChange={(value: "random" | "recent") => {
              setOrderFilter(value);
              handleFilterChange();
            }}
          >
            <SelectTrigger id="filter-order" className="h-9 w-[100px] flex-shrink-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="random">
                  {t("filters.orderRandom", { default: "Aléatoire" })}
                </SelectItem>
                <SelectItem value="recent">
                  {t("filters.orderRecent", { default: "Plus récents" })}
                </SelectItem>
              </SelectContent>
          </Select>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Switch
              id="hide-completed-challenges"
              checked={hideCompleted}
              onCheckedChange={(checked) => {
                setHideCompleted(checked);
                handleFilterChange();
              }}
            />
            <label
              htmlFor="hide-completed-challenges"
              className="text-xs text-muted-foreground cursor-pointer flex items-center gap-1.5"
            >
              <EyeOff className="h-3.5 w-3.5" />
              {t("filters.hideCompleted")}
            </label>
          </div>
        </div>

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
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg md:text-xl font-semibold">
              {isLoading
                ? t("list.loading")
                : total === 0
                  ? t("list.empty")
                  : total === 1
                    ? t("list.count", { count: total, default: "1 défi" })
                    : t("list.countPlural", { count: total, default: `${total} défis` })}
            </h2>

            {/* Toggle Vue Grille / Liste */}
            <div className="flex items-center gap-1 border rounded-lg p-1">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="h-8 w-8 p-0"
                aria-label={t("viewGrid")}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="h-8 w-8 p-0"
                aria-label={t("viewList")}
              >
                <List className="h-4 w-4" />
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
            <LoadingState message={t("list.loading")} />
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
                      <ChallengeCard challenge={challenge} />
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
          <PageLayout>
            <LoadingState message="Chargement..." />
          </PageLayout>
        </ProtectedRoute>
      }
    >
      <ChallengesPageContent />
    </Suspense>
  );
}
