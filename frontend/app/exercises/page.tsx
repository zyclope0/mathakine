"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useExercises } from "@/hooks/useExercises";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ExerciseCard } from "@/components/exercises/ExerciseCard";
import { ExerciseGenerator } from "@/components/exercises/ExerciseGenerator";
import { AIGenerator } from "@/components/exercises/AIGenerator";
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
import { EXERCISE_TYPE_STYLES, EXERCISE_TYPES, AGE_GROUPS } from "@/lib/constants/exercises";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { Filter, X, Search, LayoutGrid, List, Sparkles, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
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
import { useLocaleStore } from "@/lib/stores/localeStore";
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
  const { locale } = useLocaleStore();
  const [exerciseTypeFilter, setExerciseTypeFilter] = useState<string>("all");
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
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

    return f;
  }, [exerciseTypeFilter, ageGroupFilter, searchQuery, currentPage]);

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
    exerciseTypeFilter !== "all" || ageGroupFilter !== "all" || searchQuery.trim() !== "";

  const clearFilters = () => {
    setExerciseTypeFilter("all");
    setAgeGroupFilter("all");
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll vers le haut de la liste
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <ProtectedRoute>
      <PageLayout>
        {/* En-tête */}
        <PageHeader title={t("title")} description={t("pageDescription")} />

        {/* Filtres - Section avec fond distinct */}
        <PageSection className="section-filter space-y-4 animate-fade-in-up">
          {/* En-tête des filtres */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">{t("filters.title")}</h2>
              {hasActiveFilters && (
                <Badge variant="secondary" className="ml-1">
                  {(exerciseTypeFilter !== "all" ? 1 : 0) +
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
              placeholder={t("search.placeholder")}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-10 h-11"
              aria-label={t("search.placeholder")}
            />
          </div>

          {/* Filtres principaux - Layout responsive */}
          <div className="flex flex-col lg:flex-row lg:items-end gap-4">
            {/* Types d'exercice */}
            <div className="flex-1 space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                {t("filters.exerciseType")}
              </label>
              <TooltipProvider delayDuration={300}>
                <div className="flex flex-wrap gap-1.5">
                  {/* Bouton "Tous" */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant={exerciseTypeFilter === "all" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setExerciseTypeFilter("all");
                          handleFilterChange();
                        }}
                        className={cn(
                          "h-10 w-10 p-0 transition-all",
                          exerciseTypeFilter === "all"
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
                          className={cn(
                            "h-10 w-10 p-0 transition-all",
                            exerciseTypeFilter === type
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
          </div>
        </PageSection>

        {/* Générateurs - Horizontal avec fond accentué */}
        <PageSection className="section-generator space-y-3 animate-fade-in-up-delay-1">
          <div className="grid gap-3 md:grid-cols-2">
            <ExerciseGenerator />
            <AIGenerator />
          </div>
        </PageSection>

        {/* Liste des exercices */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-3">
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
                  {exercises.map((exercise, index) => {
                    const delayClass =
                      index === 0
                        ? "animate-fade-in-up-delay-1"
                        : index === 1
                          ? "animate-fade-in-up-delay-2"
                          : index === 2
                            ? "animate-fade-in-up-delay-3"
                            : "animate-fade-in-up-delay-3";
                    return (
                      <div key={exercise.id} className={delayClass}>
                        <ExerciseCard exercise={exercise} />
                      </div>
                    );
                  })}
                </PageGrid>
              ) : (
                /* Vue Liste Compacte */
                <div className="space-y-2">
                  {exercises.map((exercise) => {
                    const typeKey =
                      exercise.exercise_type?.toLowerCase() as keyof typeof EXERCISE_TYPE_STYLES;
                    const { icon: TypeIcon } =
                      EXERCISE_TYPE_STYLES[typeKey] || EXERCISE_TYPE_STYLES.divers;
                    const typeDisplay = getTypeDisplay(exercise.exercise_type);
                    const ageDisplay = getAgeDisplay(exercise.age_group);
                    const completed = isCompleted(exercise.id);

                    return (
                      <div
                        key={exercise.id}
                        onClick={() => {
                          setSelectedExerciseId(exercise.id);
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
                            <h3 className="font-medium truncate">{exercise.title}</h3>
                            {exercise.ai_generated && (
                              <Sparkles className="h-3.5 w-3.5 text-amber-500 flex-shrink-0" />
                            )}
                            {completed && (
                              <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground truncate">
                            {exercise.question}
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
