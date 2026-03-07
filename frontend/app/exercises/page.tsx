"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useExercises } from "@/hooks/useExercises";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ExerciseCard } from "@/components/exercises/ExerciseCard";
import { UnifiedExerciseGenerator } from "@/components/exercises/UnifiedExerciseGenerator";
import { CompactListItem } from "@/components/shared/CompactListItem";
import { getStaggerDelay } from "@/lib/utils/animation";
import { isAiGenerated } from "@/lib/utils/format";
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
import { EXERCISE_TYPE_STYLES, AGE_GROUPS } from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { Filter, X, Search, LayoutGrid, List, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
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
import {
  PageLayout,
  PageHeader,
  PageSection,
  PageGrid,
  EmptyState,
  LoadingState,
} from "@/components/layout";
import { ApiClientError } from "@/lib/api/client";
import { debugLog } from "@/lib/utils/debug";

const ITEMS_PER_PAGE = 15;

function ExercisesPageContent() {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const [exerciseTypeFilter, setExerciseTypeFilter] = useState<string>("all");
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hideCompleted, setHideCompleted] = useState(false);
  const { isCompleted } = useCompletedExercises();

  // Refetch les queries de progression quand on arrive sur la page
  useEffect(() => {
    if (pathname === "/exercises") {
      queryClient.refetchQueries({ queryKey: ["completed-exercises"] });
    }
  }, [pathname, queryClient]);

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

    f.order = "random"; // Ordre aléatoire par défaut
    f.hide_completed = hideCompleted;

    return f;
  }, [exerciseTypeFilter, ageGroupFilter, searchQuery, currentPage, hideCompleted]);

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
    hideCompleted;

  const clearFilters = () => {
    setExerciseTypeFilter("all");
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
    <ProtectedRoute>
      <PageLayout compact>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} />

        {/* Filtres — Toolbar compacte */}
        <div
          className={cn(
            "p-4 rounded-xl border border-border/50 bg-card/40 backdrop-blur-md flex flex-col md:flex-row md:items-center gap-4 animate-fade-in-up"
          )}
        >
          <div className="flex items-center gap-2 flex-shrink-0">
            <Filter className="h-4 w-4 text-primary" aria-hidden="true" />
            <span className="text-sm font-medium">{t("filters.title")}</span>
            {hasActiveFilters && (
              <Badge variant="secondary" className="text-xs">
                {(exerciseTypeFilter !== "all" ? 1 : 0) +
                  (ageGroupFilter !== "all" ? 1 : 0) +
                  (searchQuery.trim() ? 1 : 0) +
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
              placeholder={t("search.placeholder")}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-9 h-9"
              aria-label={t("search.placeholder")}
            />
          </div>

          <TooltipProvider delayDuration={300}>
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-muted-foreground mr-1 hidden sm:inline">
                {t("filters.exerciseType")}:
              </span>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={exerciseTypeFilter === "all" ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setExerciseTypeFilter("all");
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
              {Object.entries(EXERCISE_TYPE_STYLES).map(([type, { icon: Icon }]) => (
                <Tooltip key={type}>
                  <TooltipTrigger asChild>
                    <Button
                      variant={exerciseTypeFilter === type ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setExerciseTypeFilter(type);
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

          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-xs text-muted-foreground mr-1 hidden md:inline">
              {t("filters.ageGroup")}:
            </span>
            <Select
              value={ageGroupFilter}
              onValueChange={(value) => {
                setAgeGroupFilter(value);
                handleFilterChange();
              }}
            >
              <SelectTrigger id="filter-age-group" className="h-9 w-[120px] md:w-[130px]">
                <SelectValue placeholder={t("filters.allAgeGroups")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("filters.allAgeGroups")}</SelectItem>
                {Object.values(AGE_GROUPS).map((value) => (
                  <SelectItem key={value} value={value}>
                    {getAgeDisplay(value)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Switch
              id="hide-completed"
              checked={hideCompleted}
              onCheckedChange={(checked) => {
                setHideCompleted(checked);
                handleFilterChange();
              }}
            />
            <label
              htmlFor="hide-completed"
              className="text-xs text-muted-foreground cursor-pointer flex items-center gap-1.5"
            >
              <EyeOff className="h-3.5 w-3.5" />
              {t("filters.hideCompleted")}
            </label>
          </div>
        </div>

        {/* Générateur unifié — Toolbar compacte */}
        <UnifiedExerciseGenerator
            onExerciseGenerated={() => {
              queryClient.invalidateQueries({ queryKey: ["exercises"] });
              queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
            }}
          />

        {/* Liste des exercices */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg md:text-xl font-semibold">
              {isLoading
                ? t("list.loading")
                : total === 1
                  ? t("list.count", { count: total })
                  : t("list.countPlural", { count: total })}
              {isFetching && !isLoading && (
                <span className="ml-2 text-sm text-muted-foreground animate-pulse">
                  ({t("list.loading", { default: "chargement..." })})
                </span>
              )}
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
                  : t("list.error.description", { default: "Impossible de charger les exercices" })
              }
            />
          ) : isLoading ? (
            <LoadingState message={t("list.loading")} />
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
                      <ExerciseCard exercise={exercise} />
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
          <PageLayout>
            <LoadingState message="Chargement..." />
          </PageLayout>
        </ProtectedRoute>
      }
    >
      <ExercisesPageContent />
    </Suspense>
  );
}
