"use client";

import { useTranslations } from "next-intl";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ChartSkeleton, StatsCardSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { PageLayout, PageHeader, PageSection } from "@/components/layout";
import { DASHBOARD_ROUTE_ACCESS } from "@/lib/auth/routeAccess";

const protectedRouteProps = {
  requireFullAccess: DASHBOARD_ROUTE_ACCESS.requireFullAccess,
  requireOnboardingCompleted: DASHBOARD_ROUTE_ACCESS.requireOnboardingCompleted,
  allowedRoles: DASHBOARD_ROUTE_ACCESS.allowedRoles,
};

/**
 * Fallback segment /dashboard — aligné sur le shell de chargement données de la page (stats + graphiques).
 */
export default function DashboardLoading() {
  const t = useTranslations("dashboard");

  return (
    <ProtectedRoute {...protectedRouteProps}>
      <PageLayout>
        <PageHeader title={t("title")} description={t("description")} />
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
