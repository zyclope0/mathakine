'use client';

import { useState, useMemo, Suspense, useEffect } from 'react';
import { useChallenges } from '@/hooks/useChallenges';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ChallengeCard } from '@/components/challenges/ChallengeCard';
import { AIGenerator } from '@/components/challenges/AIGenerator';
import { useQueryClient } from '@tanstack/react-query';
import { usePathname } from 'next/navigation';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Pagination } from '@/components/ui/pagination';
import { CHALLENGE_TYPES, CHALLENGE_TYPE_DISPLAY, AGE_GROUPS, AGE_GROUP_DISPLAY, type ChallengeType, type AgeGroup } from '@/lib/constants/challenges';
import type { ChallengeFilters } from '@/hooks/useChallenges';
import { Filter, X, Puzzle, Search } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { PageLayout, PageHeader, PageSection, PageGrid, EmptyState, LoadingState } from '@/components/layout';
import { ApiClientError } from '@/lib/api/client';
import type { Challenge } from '@/types/api';

const ITEMS_PER_PAGE = 20;

function ChallengesPageContent() {
  const t = useTranslations('challenges');
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const [challengeTypeFilter, setChallengeTypeFilter] = useState<string>('all');
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);

  // Refetch les queries de progression quand on arrive sur la page
  useEffect(() => {
    if (pathname === '/challenges') {
      queryClient.refetchQueries({ queryKey: ['completed-challenges'] });
    }
  }, [pathname, queryClient]);
  
  // Optimiser les filtres avec useMemo
  const filters: ChallengeFilters = useMemo(() => {
    const f: ChallengeFilters = {
      limit: ITEMS_PER_PAGE,
      skip: (currentPage - 1) * ITEMS_PER_PAGE,
    };
    
    if (challengeTypeFilter !== 'all') {
      f.challenge_type = challengeTypeFilter as ChallengeType;
    }
    
    if (ageGroupFilter !== 'all') {
      f.age_group = ageGroupFilter as AgeGroup;
    }
    
    // Ajouter la recherche côté serveur si fournie
    if (searchQuery.trim()) {
      f.search = searchQuery.trim();
    }
    
    return f;
  }, [challengeTypeFilter, ageGroupFilter, searchQuery, currentPage]);

  const { challenges, total, hasMore, isLoading, error } = useChallenges(filters);

  // Calculer le nombre total de pages à partir du total réel
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE) || 1;

  const hasActiveFilters = challengeTypeFilter !== 'all' || ageGroupFilter !== 'all' || searchQuery.trim() !== '';

  const clearFilters = () => {
    setChallengeTypeFilter('all');
    setAgeGroupFilter('all');
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
          icon={Puzzle}
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
          <div className="space-y-1.5">
            <label htmlFor="search-challenges" className="text-sm font-medium">{t('search.label', { default: 'Rechercher' })}</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                id="search-challenges"
                placeholder={t('search.placeholder', { default: 'Rechercher un défi...' })}
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                className="pl-9"
                aria-label={t('search.placeholder', { default: 'Rechercher un défi...' })}
              />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="filter-challenge-type" className="text-sm font-medium">{t('filters.challengeType')}</label>
              <Select value={challengeTypeFilter} onValueChange={(value) => {
                setChallengeTypeFilter(value);
                setCurrentPage(1);
              }}>
                <SelectTrigger id="filter-challenge-type" className="h-9">
                  <SelectValue placeholder={t('filters.allTypes')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allTypes')}</SelectItem>
                  {Object.entries(CHALLENGE_TYPE_DISPLAY).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="filter-age-group" className="text-sm font-medium">{t('filters.ageGroup')}</label>
              <Select value={ageGroupFilter} onValueChange={(value) => {
                setAgeGroupFilter(value);
                setCurrentPage(1);
              }}>
                <SelectTrigger id="filter-age-group" className="h-9">
                  <SelectValue placeholder={t('filters.allGroups')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.allGroups')}</SelectItem>
                  {Object.entries(AGE_GROUP_DISPLAY).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </PageSection>

        {/* Générateur IA */}
        <PageSection className="section-generator animate-fade-in-up-delay-1">
          <AIGenerator 
            onChallengeGenerated={(challenge: Challenge) => {
              // Invalider le cache pour recharger la liste
              queryClient.invalidateQueries({ queryKey: ['challenges'] });
              queryClient.invalidateQueries({ queryKey: ['completed-challenges'] });
            }}
          />
        </PageSection>

        {/* Liste des défis */}
        <PageSection className="space-y-3 animate-fade-in-up-delay-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg md:text-xl font-semibold">
              {isLoading 
                ? t('list.loading')
                : total === 0
                  ? t('list.empty')
                  : total === 1
                    ? t('list.count', { count: total, default: '1 défi' })
                    : t('list.countPlural', { count: total, default: `${total} défis` })
              }
            </h2>
          </div>

          {error ? (
            <EmptyState
              title="Erreur de chargement"
              description={error instanceof ApiClientError ? error.message : 'Impossible de charger les défis'}
              icon={Puzzle}
            />
          ) : isLoading ? (
            <LoadingState message={t('list.loading')} />
          ) : challenges.length === 0 ? (
            <EmptyState
              title={searchQuery.trim() ? t('search.noResults', { query: searchQuery, default: `Aucun résultat pour "${searchQuery}"` }) : t('list.empty')}
              description={searchQuery.trim() ? '' : t('list.emptyHint')}
              icon={Puzzle}
            />
          ) : (
            <>
              <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="sm" className="md:gap-4">
                {challenges.map((challenge, index) => {
                  const delayClass = index === 0 ? 'animate-fade-in-up-delay-1' 
                    : index === 1 ? 'animate-fade-in-up-delay-2' 
                    : index === 2 ? 'animate-fade-in-up-delay-3'
                    : 'animate-fade-in-up-delay-3';
                  return (
                    <div key={challenge.id} className={delayClass}>
                      <ChallengeCard challenge={challenge} />
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

export default function ChallengesPage() {
  return (
    <Suspense fallback={
      <ProtectedRoute>
        <PageLayout>
          <LoadingState message="Chargement..." />
        </PageLayout>
      </ProtectedRoute>
    }>
      <ChallengesPageContent />
    </Suspense>
  );
}

