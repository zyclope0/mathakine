'use client';

import { useState, useMemo, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { useExercises } from '@/hooks/useExercises';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ExerciseCard } from '@/components/exercises/ExerciseCard';
import { ExerciseGenerator } from '@/components/exercises/ExerciseGenerator';
import { AIGenerator } from '@/components/exercises/AIGenerator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Pagination } from '@/components/ui/pagination';
import { EXERCISE_TYPE_DISPLAY, DIFFICULTY_DISPLAY } from '@/lib/constants/exercises';
import { Filter, X, Search } from 'lucide-react';
import type { ExerciseFilters } from '@/hooks/useExercises';
import { useTranslations } from 'next-intl';
import { PageLayout, PageHeader, PageSection, PageGrid, EmptyState, LoadingState } from '@/components/layout';
import { useLocaleStore } from '@/lib/stores/localeStore';
import { ApiClientError } from '@/lib/api/client';
import { debugLog } from '@/lib/utils/debug';

const ITEMS_PER_PAGE = 20;

function ExercisesPageContent() {
  const t = useTranslations('exercises');
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const { locale } = useLocaleStore();
  const [exerciseTypeFilter, setExerciseTypeFilter] = useState<string>('all');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);

  // Refetch les queries de progression quand on arrive sur la page
  useEffect(() => {
    if (pathname === '/exercises') {
      queryClient.refetchQueries({ queryKey: ['completed-exercises'] });
    }
  }, [pathname, queryClient]);
  
  // Réinitialiser à la page 1 quand les filtres changent
  const filters: ExerciseFilters = useMemo(() => {
    const f: ExerciseFilters = {
      limit: ITEMS_PER_PAGE,
      skip: (currentPage - 1) * ITEMS_PER_PAGE,
    };
    
    if (exerciseTypeFilter !== 'all') {
      f.exercise_type = exerciseTypeFilter;
    }
    
    if (difficultyFilter !== 'all') {
      f.difficulty = difficultyFilter;
    }
    
    // Ajouter la recherche côté serveur si fournie
    if (searchQuery.trim()) {
      f.search = searchQuery.trim();
    }
    
    return f;
  }, [exerciseTypeFilter, difficultyFilter, searchQuery, currentPage]);
  
  // Détecter le paramètre generated=true et rafraîchir la liste
  useEffect(() => {
    const generated = searchParams.get('generated');
    if (generated === 'true') {
      // Invalider les queries pour forcer le refetch avec les bons filtres
      queryClient.invalidateQueries({ queryKey: ['exercises'] });
      // Retirer le paramètre de l'URL sans recharger la page
      const newSearchParams = new URLSearchParams(searchParams.toString());
      newSearchParams.delete('generated');
      const newUrl = newSearchParams.toString() 
        ? `${window.location.pathname}?${newSearchParams.toString()}`
        : window.location.pathname;
      router.replace(newUrl, { scroll: false });
    }
  }, [searchParams, queryClient, router]);
  
  const { exercises, total, hasMore, isLoading, error } = useExercises(filters);
  
  // Log pour déboguer (uniquement en développement)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      debugLog('[ExercisesPage] State:', {
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

  const hasActiveFilters = exerciseTypeFilter !== 'all' || difficultyFilter !== 'all' || searchQuery.trim() !== '';

  const clearFilters = () => {
    setExerciseTypeFilter('all');
    setDifficultyFilter('all');
    setSearchQuery('');
    setCurrentPage(1);
  };
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll vers le haut de la liste
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <ProtectedRoute>
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={t('title')}
          description={t('pageDescription')}
        />

        {/* Filtres - Section avec fond distinct */}
        <PageSection className="section-filter space-y-3 animate-fade-in-up">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="h-5 w-5 text-primary" />
            <h2 className="text-lg md:text-xl font-semibold">{t('filters.title')}</h2>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="ml-auto"
              >
                <X className="h-4 w-4 mr-1" />
                {t('filters.reset')}
              </Button>
            )}
          </div>

          {/* Barre de recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder={t('search.placeholder')}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-9"
              aria-label={t('search.placeholder')}
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="filter-exercise-type" className="text-sm font-medium">
                {t('filters.exerciseType')}
              </label>
              <Select 
                value={exerciseTypeFilter} 
                onValueChange={(value) => {
                  setExerciseTypeFilter(value);
                  handleFilterChange();
                }}
              >
                <SelectTrigger id="filter-exercise-type">
                  <SelectValue placeholder={t('filters.allTypes')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allTypes')}</SelectItem>
                  {Object.entries(EXERCISE_TYPE_DISPLAY).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="filter-difficulty" className="text-sm font-medium">
                {t('filters.difficulty')}
              </label>
              <Select 
                value={difficultyFilter} 
                onValueChange={(value) => {
                  setDifficultyFilter(value);
                  handleFilterChange();
                }}
              >
                <SelectTrigger id="filter-difficulty">
                  <SelectValue placeholder={t('filters.allLevels')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allLevels')}</SelectItem>
                  {Object.entries(DIFFICULTY_DISPLAY).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
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
                ? t('list.loading')
                : exercises.length === 1
                  ? t('list.count', { count: exercises.length })
                  : t('list.countPlural', { count: exercises.length })
              }
            </h2>
          </div>

          {error ? (
            <EmptyState
              title={t('list.error.title', { default: 'Erreur de chargement' })}
              description={error instanceof ApiClientError ? error.message : t('list.error.description', { default: 'Impossible de charger les exercices' })}
            />
          ) : isLoading ? (
            <LoadingState message={t('list.loading')} />
          ) : exercises.length === 0 ? (
            <EmptyState
              title={searchQuery.trim() ? t('search.noResults', { query: searchQuery }) : t('list.empty')}
              description={searchQuery.trim() ? '' : t('list.emptyHint')}
            />
          ) : (
            <>
              <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="sm" className="md:gap-4">
                {exercises.map((exercise, index) => {
                  const delayClass = index === 0 ? 'animate-fade-in-up-delay-1' 
                    : index === 1 ? 'animate-fade-in-up-delay-2' 
                    : index === 2 ? 'animate-fade-in-up-delay-3'
                    : 'animate-fade-in-up-delay-3';
                  return (
                    <div key={exercise.id} className={delayClass}>
                      <ExerciseCard exercise={exercise} />
                    </div>
                  );
                })}
              </PageGrid>
              
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
      </PageLayout>
    </ProtectedRoute>
  );
}

export default function ExercisesPage() {
  return (
    <Suspense fallback={
      <ProtectedRoute>
        <PageLayout>
          <LoadingState message="Chargement..." />
        </PageLayout>
      </ProtectedRoute>
    }>
      <ExercisesPageContent />
    </Suspense>
  );
}

