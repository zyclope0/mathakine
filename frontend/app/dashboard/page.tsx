'use client';

import { useCallback, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useUserStats, type TimeRange } from '@/hooks/useUserStats';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { RefreshCw, CheckCircle, Zap, Trophy } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ProgressChartLazy } from '@/components/dashboard/ProgressChartLazy';
import { DailyExercisesChartLazy } from '@/components/dashboard/DailyExercisesChartLazy';
import { PerformanceByType } from '@/components/dashboard/PerformanceByType';
import { LevelIndicator } from '@/components/dashboard/LevelIndicator';
import { Recommendations } from '@/components/dashboard/Recommendations';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { ExportButton } from '@/components/dashboard/ExportButton';
import { TimeRangeSelector } from '@/components/dashboard/TimeRangeSelector';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';
import { PageLayout, PageHeader, PageSection, EmptyState } from '@/components/layout';
import {
  StatsCardSkeleton,
  ChartSkeleton,
  PerformanceByTypeSkeleton,
  RecentActivitySkeleton,
  LevelIndicatorSkeleton,
  RecommendationsSkeleton,
} from '@/components/dashboard/DashboardSkeletons';

export default function DashboardPage() {
  const { user } = useAuth();
  const [timeRange, setTimeRange] = useState<TimeRange>('30');
  const { stats, isLoading, error, refetch } = useUserStats(timeRange);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const t = useTranslations('dashboard');
  const tToasts = useTranslations('toasts.dashboard');
  
  // Debounce du refresh pour éviter les clics multiples rapides
  const handleRefresh = useCallback(async () => {
    // Empêcher les clics multiples
    if (isRefreshing) {
      return;
    }

    setIsRefreshing(true);
    
    try {
      await refetch();
      toast.success(tToasts('statsUpdated'));
    } catch (error) {
      // En production, les erreurs sont gérées par le toast
      // Ne pas logger en console pour éviter les fuites d'information
      toast.error(t('error.title', { default: 'Erreur lors du rafraîchissement' }));
    } finally {
      // Délai minimum pour éviter les clics trop rapides
      setTimeout(() => {
        setIsRefreshing(false);
      }, 500);
    }
  }, [refetch, isRefreshing, tToasts, t]);

  if (isLoading) {
    return (
      <ProtectedRoute>
        <PageLayout>
          <PageHeader
            title={user?.username ? `${t('welcome')}, ${user.username} !` : t('title')}
            description={t('description')}
          />
          {/* Skeleton loaders pour meilleure perception de performance */}
          <PageSection className="space-y-3">
            <div className="grid gap-4 md:grid-cols-3">
              <StatsCardSkeleton />
              <StatsCardSkeleton />
              <StatsCardSkeleton />
            </div>
          </PageSection>
          <PageSection className="space-y-3">
            <div className="grid gap-6 md:grid-cols-2">
              <ChartSkeleton />
              <ChartSkeleton />
            </div>
          </PageSection>
          <PageSection className="space-y-3">
            <PerformanceByTypeSkeleton />
          </PageSection>
        </PageLayout>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <PageLayout>
          <EmptyState
            title={t('error.title')}
            action={
              <Button onClick={() => refetch()}>{t('error.retry')}</Button>
            }
          />
        </PageLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={user?.username ? `${t('welcome')}, ${user.username} !` : t('title')}
          description={t('description')}
          actions={
            <>
              <TimeRangeSelector value={timeRange} onValueChange={setTimeRange} />
              <ExportButton timeRange={timeRange} />
              <Button
                variant="outline"
                onClick={handleRefresh}
                disabled={isRefreshing || isLoading}
                className="btn-cta-primary flex items-center gap-2"
                aria-label={t('refresh')}
              >
                <RefreshCw 
                  className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} 
                  aria-hidden="true" 
                />
                {t('refresh')}
              </Button>
            </>
          }
        />

        {/* Statistiques générales */}
        {stats && (
          <>
            <PageSection className="space-y-3 animate-fade-in-up-delay-1">
              <div className="grid gap-4 md:grid-cols-3">
                <StatsCard
                  icon={CheckCircle}
                  value={stats.total_exercises || 0}
                  label={t('stats.exercisesSolved')}
                />
                <StatsCard
                  icon={Zap}
                  value={`${Math.round((stats.correct_answers / (stats.correct_answers + stats.incorrect_answers)) * 100) || 0}%`}
                  label={t('stats.successRate')}
                />
                <StatsCard
                  icon={Trophy}
                  value={stats.total_challenges || 0}
                  label={t('stats.challengesCompleted')}
                />
              </div>
              {/* Métadonnées temporelles */}
              {stats.recent_activity && stats.recent_activity.length > 0 && stats.recent_activity[0] && (
                <div className="text-xs text-muted-foreground text-center mt-2">
                  {t('lastUpdate', { 
                    time: new Date(stats.recent_activity[0].completed_at).toLocaleString('fr-FR', {
                      day: '2-digit',
                      month: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    })
                  })}
                </div>
              )}
            </PageSection>

            {/* Graphiques */}
            <PageSection className="space-y-3 animate-fade-in-up-delay-2">
              <div className="grid gap-6 md:grid-cols-2">
                {stats.progress_over_time && (
                  <ProgressChartLazy data={stats.progress_over_time} />
                )}
                {stats.exercises_by_day && (
                  <DailyExercisesChartLazy data={stats.exercises_by_day} />
                )}
              </div>
            </PageSection>

            {/* Performance par type */}
            {stats.performance_by_type && (
              <PageSection className="space-y-3 animate-fade-in-up-delay-3">
                <PerformanceByType performance={stats.performance_by_type} />
              </PageSection>
            )}

            {/* Niveau actuel */}
            {stats.level && (
              <PageSection className="space-y-3 animate-fade-in-up-delay-3">
                <LevelIndicator level={stats.level} />
              </PageSection>
            )}

            {/* Recommandations */}
            <PageSection className="space-y-3 animate-fade-in-up-delay-3">
              <Recommendations />
            </PageSection>

            {/* Activité récente */}
            {stats.recent_activity && (
              <PageSection className="space-y-3 animate-fade-in-up-delay-3">
                <RecentActivity activities={stats.recent_activity} />
              </PageSection>
            )}
          </>
        )}

        {/* État vide */}
        {!stats && (
          <EmptyState
            title={t('empty.message')}
          />
        )}
      </PageLayout>
    </ProtectedRoute>
  );
}

