"use client";

import { useCallback, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useUserStats, type TimeRange } from "@/hooks/useUserStats";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useChallengesProgress } from "@/hooks/useChallengesProgress";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Button } from "@/components/ui/button";
import {
  RefreshCw,
  CheckCircle,
  Zap,
  Trophy,
  LayoutDashboard,
  TrendingUp,
  BarChart3,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { ProgressChartLazy } from "@/components/dashboard/ProgressChartLazy";
import { DailyExercisesChartLazy } from "@/components/dashboard/DailyExercisesChartLazy";
import { AverageTimeWidget } from "@/components/dashboard/AverageTimeWidget";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { Recommendations } from "@/components/dashboard/Recommendations";
import { QuickStartActions } from "@/components/dashboard/QuickStartActions";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { DailyChallengesWidget } from "@/components/dashboard/DailyChallengesWidget";
import { LevelEstablishedWidget } from "@/components/dashboard/LevelEstablishedWidget";
import { ChallengesProgressWidget } from "@/components/dashboard/ChallengesProgressWidget";
import { CategoryAccuracyChart } from "@/components/dashboard/CategoryAccuracyChart";
import { ProgressTimelineWidget } from "@/components/dashboard/ProgressTimelineWidget";
import { ExportButton } from "@/components/dashboard/ExportButton";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, EmptyState } from "@/components/layout";
import { StatsCardSkeleton, ChartSkeleton } from "@/components/dashboard/DashboardSkeletons";

function DashboardLastUpdate({ time, locale }: { time: string; locale?: string }) {
  const t = useTranslations("dashboard");
  let displayTime: string;
  try {
    const date = new Date(time);
    const dateLocale = locale === "en" ? enUS : fr;
    displayTime = formatDistanceToNow(date, { addSuffix: true, locale: dateLocale });
  } catch {
    displayTime = time;
  }
  return <p className="text-xs text-muted-foreground">{t("lastUpdate", { time: displayTime })}</p>;
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { locale } = useLocaleStore();
  const [timeRange, setTimeRange] = useState<TimeRange>("30");
  const { stats, isLoading, error, refetch } = useUserStats(timeRange);
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { data: challengesProgress, isLoading: isLoadingChallenges } = useChallengesProgress();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const t = useTranslations("dashboard");
  const tToasts = useTranslations("toasts.dashboard");

  // Debounce du refresh pour éviter les clics multiples rapides
  const handleRefresh = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    try {
      await refetch();
      // Invalider progress, challenges et défis quotidiens pour un rafraîchissement complet
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["user", "progress"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "progress", "timeline"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "challenges", "progress"] }),
        queryClient.invalidateQueries({ queryKey: ["leaderboard"] }),
        queryClient.invalidateQueries({ queryKey: ["daily-challenges"] }),
      ]);
      toast.success(tToasts("statsUpdated"));
    } catch {
      toast.error(t("error.title", { default: "Erreur lors du rafraîchissement" }));
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  }, [refetch, isRefreshing, queryClient, tToasts, t]);

  if (isLoading) {
    return (
      <ProtectedRoute requireFullAccess requireOnboardingCompleted>
        <PageLayout>
          <PageHeader
            title={user?.username ? `${t("welcome")}, ${user.username} !` : t("title")}
            description={t("description")}
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
            <ChartSkeleton />
          </PageSection>
        </PageLayout>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute requireFullAccess requireOnboardingCompleted>
        <PageLayout>
          <EmptyState
            title={t("error.title")}
            action={<Button onClick={() => refetch()}>{t("error.retry")}</Button>}
          />
        </PageLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute requireFullAccess requireOnboardingCompleted>
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={user?.username ? `${t("welcome")}, ${user.username} !` : t("title")}
          description={t("description")}
          actions={
            <>
              <TimeRangeSelector value={timeRange} onValueChange={setTimeRange} />
              <ExportButton timeRange={timeRange} />
              <Button
                variant="ghost"
                onClick={handleRefresh}
                disabled={isRefreshing || isLoading}
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
                aria-label={t("refresh")}
              >
                <RefreshCw
                  className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
                  aria-hidden="true"
                />
                {t("refresh")}
              </Button>
            </>
          }
        />

        {/* Contenu organisé par onglets pour réduire la densité */}
        {stats && (
          <Tabs defaultValue="overview" className="space-y-4 animate-fade-in-up-delay-1">
            <TabsList
              className="grid w-full max-w-3xl grid-cols-2 sm:grid-cols-4"
              aria-label={t("tabs.tabsLabel", { default: "Sections du tableau de bord" })}
            >
              <TabsTrigger value="overview" className="flex items-center gap-2 py-2.5 text-sm">
                <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">
                  {t("tabs.overview", { default: "Vue d'ensemble" })}
                </span>
                <span className="sm:hidden">{t("tabs.overviewShort", { default: "Vue" })}</span>
              </TabsTrigger>
              <TabsTrigger
                value="recommendations"
                className="flex items-center gap-2 py-2.5 text-sm"
              >
                <Zap className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">
                  {t("tabs.recommendations", { default: "Recommandations" })}
                </span>
                <span className="sm:hidden">
                  {t("tabs.recommendationsShort", { default: "Recommandés" })}
                </span>
              </TabsTrigger>
              <TabsTrigger value="progress" className="flex items-center gap-2 py-2.5 text-sm">
                <TrendingUp className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">
                  {t("tabs.progress", { default: "Progression" })}
                </span>
                <span className="sm:hidden">{t("tabs.progressShort", { default: "Stats" })}</span>
              </TabsTrigger>
              <TabsTrigger value="profile" className="flex items-center gap-2 py-2.5 text-sm">
                <BarChart3 className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">
                  {t("tabs.profile", { default: "Mon Profil" })}
                </span>
                <span className="sm:hidden">{t("tabs.profileShort", { default: "Profil" })}</span>
              </TabsTrigger>
            </TabsList>

            {/* Onglet Vue d'ensemble — Parcours guidé + Défis du jour + Série en cours */}
            <TabsContent value="overview" className="space-y-6">
              <PageSection>
                <div className="space-y-3">
                  <QuickStartActions />
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-stretch">
                    <div className="md:col-span-8 flex flex-col min-h-0">
                      <DailyChallengesWidget />
                    </div>
                    <div className="md:col-span-4 flex flex-col min-h-0">
                      <StreakWidget
                        currentStreak={progressStats?.current_streak || 0}
                        highestStreak={progressStats?.highest_streak || 0}
                        isLoading={isLoadingProgress}
                      />
                    </div>
                  </div>
                </div>
              </PageSection>
            </TabsContent>

            {/* Onglet Recommandations — conseils du Maître Jedi */}
            <TabsContent value="recommendations" className="space-y-6">
              <PageSection>
                <Recommendations />
              </PageSection>
            </TabsContent>

            {/* Onglet Progression — graphiques uniquement */}
            <TabsContent value="progress" className="space-y-6">
              <PageSection>
                <ProgressTimelineWidget />
              </PageSection>
              <PageSection>
                <div className="grid gap-6 md:grid-cols-2 items-stretch">
                  <ChallengesProgressWidget
                    completedChallenges={challengesProgress?.completed_challenges || 0}
                    totalChallenges={challengesProgress?.total_challenges || 0}
                    successRate={challengesProgress?.success_rate || 0}
                    averageTime={challengesProgress?.average_time || 0}
                    isLoading={isLoadingChallenges}
                  />
                  <CategoryAccuracyChart
                    categoryData={progressStats?.by_category || {}}
                    isLoading={isLoadingProgress}
                  />
                </div>
              </PageSection>

              {stats.progress_over_time && stats.exercises_by_day ? (
                <PageSection>
                  <div className="grid gap-6 md:grid-cols-2">
                    <ProgressChartLazy data={stats.progress_over_time} />
                    <DailyExercisesChartLazy data={stats.exercises_by_day} />
                  </div>
                </PageSection>
              ) : (
                <PageSection>
                  <p className="text-muted-foreground text-center py-8">
                    {t("empty.charts", {
                      default:
                        "Continuez à vous entraîner pour voir vos graphiques de progression.",
                    })}
                  </p>
                </PageSection>
              )}
            </TabsContent>

            {/* Onglet Mon Profil — Niveau, badges, stats, tempo, journal */}
            <TabsContent value="profile" className="space-y-6">
              {stats.level && (
                <PageSection>
                  <LevelIndicator level={stats.level} />
                </PageSection>
              )}
              <PageSection>
                <LevelEstablishedWidget />
              </PageSection>
              <PageSection className="space-y-2">
                {stats.recent_activity?.[0]?.time && (
                  <div className="flex justify-end">
                    <DashboardLastUpdate time={stats.recent_activity[0].time} locale={locale} />
                  </div>
                )}
                <div className="grid gap-4 md:grid-cols-3">
                  <StatsCard
                    icon={CheckCircle}
                    value={stats.total_exercises || 0}
                    label={t("stats.exercisesSolved")}
                  />
                  <StatsCard
                    icon={Zap}
                    value={`${Math.round(stats.success_rate || 0)}%`}
                    label={t("stats.successRate")}
                  />
                  <StatsCard
                    icon={Trophy}
                    value={stats.total_challenges || 0}
                    label={t("stats.challengesCompleted")}
                  />
                </div>
              </PageSection>
              <PageSection>
                <AverageTimeWidget
                  averageTimeSeconds={progressStats?.average_time ?? 0}
                  totalAttempts={progressStats?.total_attempts ?? 0}
                  isLoading={isLoadingProgress}
                />
              </PageSection>
              {stats.recent_activity && stats.recent_activity.length > 0 && (
                <PageSection>
                  <RecentActivity activities={stats.recent_activity} />
                </PageSection>
              )}
            </TabsContent>
          </Tabs>
        )}

        {/* État vide */}
        {!stats && <EmptyState title={t("empty.message")} />}
      </PageLayout>
    </ProtectedRoute>
  );
}
