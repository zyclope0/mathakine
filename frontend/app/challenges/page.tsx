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
import {
  Filter,
  X,
  Puzzle,
  Search,
  LayoutGrid,
  List,
  Sparkles,
  CheckCircle2,
  EyeOff,
} from "lucide-react";
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

    f.order = "random"; // Ordre aléatoire par défaut
    f.hide_completed = hideCompleted;

    return f;
  }, [challengeTypeFilter, ageGroupFilter, searchQuery, currentPage, hideCompleted]);

  const { challenges, total, isLoading, error } = useChallenges(filters);

  // Calculer le nombre total de pages à partir du total réel
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE) || 1;

  const hasActiveFilters =
    challengeTypeFilter !== "all" ||
    ageGroupFilter !== "all" ||
    searchQuery.trim() !== "" ||
    hideCompleted;

  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setChallengeTypeFilter("all");
    setAgeGroupFilter("all");
    setSearchQuery("");
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
      <PageLayout>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} icon={Puzzle} />

        {/* Filtres - Section avec fond distinct */}
        <PageSection className="section-filter space-y-4 animate-fade-in-up">
          {/* En-tête des filtres */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">{t("filters.title")}</h2>
              {hasActiveFilters && (
                <Badge variant="secondary" className="ml-1">
                  {(challengeTypeFilter !== "all" ? 1 : 0) +
                    (ageGroupFilter !== "all" ? 1 : 0) +
                    (searchQuery.trim() ? 1 : 0)}
                </Badge>
              )}
            </div>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4 mr-1" />
                {t("filters.reset")}
              </Button>
            )}
          </div>

          {/* Barre de recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder={t("search.placeholder", { default: "Rechercher un défi..." })}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-10 h-11"
              aria-label={t("search.placeholder", { default: "Rechercher un défi..." })}
            />
          </div>

          {/* Filtres principaux - Layout responsive */}
          <div className="flex flex-col lg:flex-row lg:items-end gap-4">
            {/* Types de défis - Sélecteur par icônes */}
            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                {t("filters.challengeType")}
              </label>
              <TooltipProvider delayDuration={300}>
                <div className="flex flex-wrap gap-1.5">
                  {/* Bouton "Tous" */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant={challengeTypeFilter === "all" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setChallengeTypeFilter("all");
                          handleFilterChange();
                        }}
                        className={cn(
                          "h-10 w-10 p-0 transition-all",
                          challengeTypeFilter === "all"
                            ? "ring-2 ring-primary/50 ring-offset-2 ring-offset-background shadow-md"
                            : "hover:bg-accent hover:border-primary/30"
                        )}
                      >
                        <Filter className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="font-medium">
                      {t("filters.allTypes")}
                    </TooltipContent>
                  </Tooltip>

                  {/* Séparateur visuel */}
                  <div className="w-px h-10 bg-border mx-1 hidden sm:block" />

                  {/* Boutons pour chaque type */}
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
                          className={cn(
                            "h-10 w-10 p-0 transition-all",
                            challengeTypeFilter === type
                              ? "ring-2 ring-primary/50 ring-offset-2 ring-offset-background shadow-md"
                              : "hover:bg-accent hover:border-primary/30"
                          )}
                        >
                          <Icon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent side="bottom" className="font-medium">
                        {getTypeDisplay(type)}
                      </TooltipContent>
                    </Tooltip>
                  ))}
                </div>
              </TooltipProvider>
            </div>

            {/* Groupe d'âge - Compact sur la même ligne en desktop */}
            <div className="lg:w-48 space-y-2">
              <label
                htmlFor="filter-age-group"
                className="text-sm font-medium text-muted-foreground"
              >
                {t("filters.ageGroup")}
              </label>
              <Select
                value={ageGroupFilter}
                onValueChange={(value) => {
                  setAgeGroupFilter(value);
                  handleFilterChange();
                }}
              >
                <SelectTrigger id="filter-age-group" className="h-10">
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
            </div>

            {/* Masquer les réussis */}
            <div className="flex items-center gap-2">
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
                className="text-sm font-medium text-muted-foreground cursor-pointer flex items-center gap-1.5"
              >
                <EyeOff className="h-4 w-4" />
                {t("filters.hideCompleted")}
              </label>
            </div>
          </div>
        </PageSection>

        {/* Générateur IA */}
        <PageSection className="section-generator animate-fade-in-up-delay-1">
          <AIGenerator
            onChallengeGenerated={() => {
              // Invalider le cache pour recharger la liste
              queryClient.invalidateQueries({ queryKey: ["challenges"] });
              queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
            }}
          />
        </PageSection>

        {/* Liste des défis */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-3">
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
                aria-label="Vue grille"
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="h-8 w-8 p-0"
                aria-label="Vue liste"
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
                  {challenges.map((challenge, index) => {
                    const delayClass =
                      index === 0
                        ? "animate-fade-in-up-delay-1"
                        : index === 1
                          ? "animate-fade-in-up-delay-2"
                          : index === 2
                            ? "animate-fade-in-up-delay-3"
                            : "animate-fade-in-up-delay-3";
                    return (
                      <div key={challenge.id} className={delayClass}>
                        <ChallengeCard challenge={challenge} />
                      </div>
                    );
                  })}
                </PageGrid>
              ) : (
                /* Vue Liste Compacte */
                <div className="space-y-2">
                  {challenges.map((challenge) => {
                    const typeKey =
                      challenge.challenge_type?.toLowerCase() as keyof typeof CHALLENGE_TYPE_STYLES;
                    const { icon: TypeIcon } = CHALLENGE_TYPE_STYLES[typeKey] || { icon: Puzzle };
                    const typeDisplay = getTypeDisplay(challenge.challenge_type);
                    const ageDisplay = getAgeDisplay(challenge.age_group);
                    const completed = isCompleted(challenge.id);

                    return (
                      <div
                        key={challenge.id}
                        onClick={() => {
                          setSelectedChallengeId(challenge.id);
                          setIsModalOpen(true);
                        }}
                        className={cn(
                          "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                          "bg-card/80 backdrop-blur-sm border-border/60",
                          "hover:bg-accent hover:border-primary/50 hover:shadow-md",
                          completed && "bg-green-500/10 border-green-500/40"
                        )}
                      >
                        {/* Icône du type */}
                        <div
                          className={cn(
                            "flex-shrink-0 h-10 w-10 rounded-lg flex items-center justify-center",
                            "bg-primary/10 border border-primary/20"
                          )}
                        >
                          <TypeIcon className="h-5 w-5 text-primary" />
                        </div>

                        {/* Infos principales */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium truncate">{challenge.title}</h3>
                            {challenge.ai_generated && (
                              <Sparkles className="h-3.5 w-3.5 text-amber-500 flex-shrink-0" />
                            )}
                            {completed && (
                              <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground truncate">
                            {challenge.description || challenge.question}
                          </p>
                        </div>

                        {/* Badges */}
                        <div className="hidden sm:flex items-center gap-2 flex-shrink-0">
                          <Badge variant="outline" className="text-xs">
                            {typeDisplay}
                          </Badge>
                          {ageDisplay && (
                            <Badge variant="outline" className="text-xs">
                              {ageDisplay}
                            </Badge>
                          )}
                        </div>
                      </div>
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
          onChallengeCompleted={() => {
            queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
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
