"use client";

import { useTranslations } from "next-intl";
import { RefreshCw } from "lucide-react";
import { DashboardOverviewSection } from "@/components/dashboard/DashboardOverviewSection";
import { DashboardProfileSection } from "@/components/dashboard/DashboardProfileSection";
import { DashboardProgressSection } from "@/components/dashboard/DashboardProgressSection";
import { DashboardRecommendationsSection } from "@/components/dashboard/DashboardRecommendationsSection";
import { DashboardTabsNav } from "@/components/dashboard/DashboardTabsNav";
import { ExportButton } from "@/components/dashboard/ExportButton";
import { StatsCardSkeleton, ChartSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { PageLayout, PageHeader, PageSection, EmptyState } from "@/components/layout";
import { useDashboardPageController } from "@/hooks/useDashboardPageController";
import { DASHBOARD_ROUTE_ACCESS } from "@/lib/auth/routeAccess";
import { shouldShowHeaderTimeRange } from "@/lib/dashboard/headerTimeRangeScope";

const protectedRouteProps = {
  requireFullAccess: DASHBOARD_ROUTE_ACCESS.requireFullAccess,
  requireOnboardingCompleted: DASHBOARD_ROUTE_ACCESS.requireOnboardingCompleted,
  allowedRoles: DASHBOARD_ROUTE_ACCESS.allowedRoles,
};

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const tToasts = useTranslations("toasts.dashboard");
  const betaHelp = {
    title: t("betaHelp.title"),
    description: t("betaHelp.description"),
    cta: t("betaHelp.cta"),
  };
  const {
    activeTab,
    challengesProgress,
    error,
    exportSnapshot,
    handleRefresh,
    isLoading,
    isLoadingChallenges,
    isLoadingProgress,
    isRefreshing,
    locale,
    progressStats,
    refetch,
    setActiveTab,
    setTimeRange,
    setTimelinePeriod,
    stats,
    timeRange,
    timeRangeLabel,
    timelinePeriod,
    user,
  } = useDashboardPageController({
    tDashboard: t,
    tDashboardToasts: tToasts,
  });

  if (isLoading) {
    return (
      <ProtectedRoute {...protectedRouteProps}>
        <PageLayout>
          <PageHeader
            title={user?.username ? `${t("welcome")}, ${user.username} !` : t("title")}
            description={t("description")}
          />
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
      <ProtectedRoute {...protectedRouteProps}>
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
    <ProtectedRoute {...protectedRouteProps}>
      <PageLayout>
        <PageHeader
          title={user?.username ? `${t("welcome")}, ${user.username} !` : t("title")}
          description={t("description")}
          actions={
            <>
              <div
                className={
                  shouldShowHeaderTimeRange(activeTab) ? undefined : "invisible pointer-events-none"
                }
                aria-hidden={!shouldShowHeaderTimeRange(activeTab)}
              >
                <TimeRangeSelector value={timeRange} onValueChange={setTimeRange} />
              </div>
              <ExportButton snapshot={exportSnapshot} />
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRefresh}
                disabled={isRefreshing || isLoading}
                className="text-muted-foreground hover:text-foreground"
                aria-label={t("refresh")}
                title={t("refresh")}
              >
                <RefreshCw
                  className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
                  aria-hidden="true"
                />
              </Button>
            </>
          }
        />

        {stats ? (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <DashboardTabsNav />
            <TabsContent value="overview" className="space-y-6">
              <DashboardOverviewSection
                betaHelp={betaHelp}
                isLoadingProgress={isLoadingProgress}
                progressStats={progressStats}
                stats={stats}
              />
            </TabsContent>
            <TabsContent value="recommendations" className="space-y-6">
              <DashboardRecommendationsSection />
            </TabsContent>
            <TabsContent value="progress" className="space-y-6">
              <DashboardProgressSection
                challengesProgress={challengesProgress}
                isLoadingChallenges={isLoadingChallenges}
                isLoadingProgress={isLoadingProgress}
                progressStats={progressStats}
                timelinePeriod={timelinePeriod}
                onTimelinePeriodChange={setTimelinePeriod}
              />
            </TabsContent>
            <TabsContent value="profile" className="space-y-6">
              <DashboardProfileSection
                challengesProgress={challengesProgress}
                isLoadingProgress={isLoadingProgress}
                locale={locale}
                progressStats={progressStats}
                stats={stats}
                timeRangeLabel={timeRangeLabel}
                user={user}
              />
            </TabsContent>
          </Tabs>
        ) : (
          <EmptyState title={t("empty.message")} />
        )}
      </PageLayout>
    </ProtectedRoute>
  );
}
