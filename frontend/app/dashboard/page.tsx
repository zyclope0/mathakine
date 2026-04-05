"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useUserStats, type TimeRange } from "@/hooks/useUserStats";
import { useProgressStats } from "@/hooks/useProgressStats";
import type { TimelinePeriod } from "@/hooks/useProgressTimeline";
import { useChallengesProgress } from "@/hooks/useChallengesProgress";
import { useDailyChallenges } from "@/hooks/useDailyChallenges";
import { buildDashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import { DASHBOARD_ROUTE_ACCESS } from "@/lib/auth/routeAccess";
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
import { Card, CardContent } from "@/components/ui/card";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { VolumeByTypeChartLazy } from "@/components/dashboard/VolumeByTypeChartLazy";
import { PracticeConsistencyWidget } from "@/components/dashboard/PracticeConsistencyWidget";
import { AverageTimeWidget } from "@/components/dashboard/AverageTimeWidget";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { Recommendations } from "@/components/dashboard/Recommendations";
import { QuickStartActions } from "@/components/dashboard/QuickStartActions";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { DailyChallengesWidget } from "@/components/dashboard/DailyChallengesWidget";
import { LevelEstablishedWidget } from "@/components/dashboard/LevelEstablishedWidget";
import { ChallengesProgressWidget } from "@/components/dashboard/ChallengesProgressWidget";
import { CategoryAccuracyChart } from "@/components/dashboard/CategoryAccuracyChart";
import { ProgressTimelineWidget } from "@/components/dashboard/ProgressTimelineWidget";
import { ExportButton } from "@/components/dashboard/ExportButton";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { shouldShowHeaderTimeRange } from "@/lib/dashboard/headerTimeRangeScope";
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
  return <p className="text-sm text-muted-foreground">{t("lastUpdate", { time: displayTime })}</p>;
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { locale } = useLocaleStore();
  const [timeRange, setTimeRange] = useState<TimeRange>("30");
  const { stats, isLoading, error, refetch } = useUserStats(timeRange);
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { data: challengesProgress, isLoading: isLoadingChallenges } = useChallengesProgress();
  const { challenges: dailyChallenges } = useDailyChallenges();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [timelinePeriod, setTimelinePeriod] = useState<TimelinePeriod>("7d");

  const t = useTranslations("dashboard");
  const tToasts = useTranslations("toasts.dashboard");

  const timeRangeLabel = useMemo(() => {
    const key =
      timeRange === "7"
        ? "7days"
        : timeRange === "30"
          ? "30days"
          : timeRange === "90"
            ? "90days"
            : "all";
    return t(`timeRange.${key}`);
  }, [timeRange, t]);

  const exportSnapshot = useMemo(() => {
    if (!stats || !user) {
      return null;
    }
    return buildDashboardExportSnapshot(
      {
        username: user.username,
        timeRange,
        timeRangeLabel,
        stats,
        gamificationLevel: user.gamification_level ?? null,
        accountTotalPoints: typeof user.total_points === "number" ? user.total_points : null,
        progressStats: progressStats ?? null,
        challengesProgress: challengesProgress ?? null,
        dailyChallenges,
      },
      new Date()
    );
  }, [stats, user, timeRange, timeRangeLabel, progressStats, challengesProgress, dailyChallenges]);

  // Debounce du refresh pour éviter les clics multiples rapides
  const handleRefresh = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    try {
      await refetch();
      // Invalider progress, challenges et défis quotidiens pour un rafraîchissement complet
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["auth", "me"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "stats"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "progress"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "progress", "timeline"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "challenges", "progress"] }),
        queryClient.invalidateQueries({ queryKey: ["user", "challenges", "detailed-progress"] }),
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

  /** Atténuation du décor spatial : attribut document, ciblé par globals.css (route dashboard uniquement). */
  useEffect(() => {
    document.documentElement.setAttribute("data-mathakine-dashboard", "");
    return () => {
      document.documentElement.removeAttribute("data-mathakine-dashboard");
    };
  }, []);

  if (isLoading) {
    return (
      <ProtectedRoute
        requireFullAccess={DASHBOARD_ROUTE_ACCESS.requireFullAccess}
        requireOnboardingCompleted={DASHBOARD_ROUTE_ACCESS.requireOnboardingCompleted}
        allowedRoles={DASHBOARD_ROUTE_ACCESS.allowedRoles}
      >
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
      <ProtectedRoute
        requireFullAccess={DASHBOARD_ROUTE_ACCESS.requireFullAccess}
        requireOnboardingCompleted={DASHBOARD_ROUTE_ACCESS.requireOnboardingCompleted}
        allowedRoles={DASHBOARD_ROUTE_ACCESS.allowedRoles}
      >
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
    <ProtectedRoute
      requireFullAccess={DASHBOARD_ROUTE_ACCESS.requireFullAccess}
      requireOnboardingCompleted={DASHBOARD_ROUTE_ACCESS.requireOnboardingCompleted}
      allowedRoles={DASHBOARD_ROUTE_ACCESS.allowedRoles}
    >
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={user?.username ? `${t("welcome")}, ${user.username} !` : t("title")}
          description={t("description")}
          actions={
            <>
              {shouldShowHeaderTimeRange(activeTab) ? (
                <TimeRangeSelector value={timeRange} onValueChange={setTimeRange} />
              ) : null}
              <ExportButton snapshot={exportSnapshot} />
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
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            {/* Wrapper scrollable : évite l'overflow sur mobile (<640px) sans casser le layout desktop */}
            <div className="w-full overflow-x-auto pb-1 -mb-1 no-scrollbar">
              <TabsList
                className="inline-flex h-11 w-max min-w-full sm:w-full sm:max-w-3xl"
                aria-label={t("tabs.tabsLabel", { default: "Sections du tableau de bord" })}
              >
                <TabsTrigger value="overview" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
                  <LayoutDashboard className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="hidden sm:inline">{t("tabs.overview", { default: "Vue d'ensemble" })}</span>
                  <span className="sm:hidden">{t("tabs.overviewShort", { default: "Vue" })}</span>
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
                  <Zap className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="hidden sm:inline">{t("tabs.recommendations", { default: "Recommandations" })}</span>
                  <span className="sm:hidden">{t("tabs.recommendationsShort", { default: "Recos" })}</span>
                </TabsTrigger>
                <TabsTrigger value="progress" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
                  <TrendingUp className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="hidden sm:inline">{t("tabs.progress", { default: "Progression" })}</span>
                  <span className="sm:hidden">{t("tabs.progressShort")}</span>
                </TabsTrigger>
                <TabsTrigger value="profile" className="flex flex-1 items-center gap-1.5 px-3 text-sm">
                  <BarChart3 className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="hidden sm:inline">{t("tabs.profile", { default: "Mon Profil" })}</span>
                  <span className="sm:hidden">{t("tabs.profileShort", { default: "Profil" })}</span>
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Onglet Vue d'ensemble — Parcours guidé + Défis du jour + Série en cours */}
            <TabsContent value="overview" className="space-y-6">
              <PageSection>
                <div className="space-y-3">
                  <QuickStartActions />
                  <SpacedRepetitionSummaryWidget summary={stats.spaced_repetition} />
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

            {/* Onglet Recommandations */}
            <TabsContent value="recommendations" className="space-y-6">
              <PageSection>
                <Recommendations />
              </PageSection>
            </TabsContent>

            {/* Onglet Progression — graphiques uniquement */}
            <TabsContent value="progress" className="space-y-6">
              <PageSection>
                <ProgressTimelineWidget
                  period={timelinePeriod}
                  onPeriodChange={setTimelinePeriod}
                />
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

              <PageSection>
                <div className="grid gap-6 md:grid-cols-2 items-stretch">
                  <VolumeByTypeChartLazy categoryData={progressStats?.by_category ?? {}} />
                  <PracticeConsistencyWidget period={timelinePeriod} />
                </div>
              </PageSection>
            </TabsContent>

            {/* Onglet Mon Profil — Niveau, badges, stats, tempo, journal */}
            <TabsContent value="profile" className="space-y-6">
              <PageSection>
                {user?.gamification_level ? (
                  <LevelIndicator level={user.gamification_level} />
                ) : (
                  <Card className="dashboard-card-surface border-dashed">
                    <CardContent className="p-6 sm:p-8">
                      <p className="text-sm font-semibold text-foreground">
                        {t("profile.levelUnavailableTitle")}
                      </p>
                      <p className="mt-2 text-sm text-muted-foreground">
                        {t("profile.levelUnavailableDescription")}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </PageSection>
              <PageSection>
                <LevelEstablishedWidget />
              </PageSection>
              <PageSection className="space-y-2">
                <p className="text-xs text-muted-foreground">
                  {t("profile.statsPeriodHint", { period: timeRangeLabel })}
                </p>
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
                    {...(challengesProgress && challengesProgress.average_time > 0
                      ? {
                          footnote: t("stats.challengesAvgFootnote", {
                            seconds: Math.round(challengesProgress.average_time),
                          }),
                        }
                      : {})}
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

        {/* État vide — commun aux deux vues */}
        {!stats && <EmptyState title={t("empty.message")} />}
      </PageLayout>
    </ProtectedRoute>
  );
}
