"use client";

import { useTranslations } from "next-intl";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader, PageSection } from "@/components/layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ADMIN_ROUTE_ACCESS } from "@/lib/auth/routeAccess";

/**
 * Fallback segment /admin (page overview) — cartes KPI + blocs stats, cohérent avec admin/page.tsx.
 * Le layout admin fournit déjà la colonne de navigation ; ce shell remplit la zone principale comme la page.
 */
export default function AdminLoading() {
  const t = useTranslations("adminPages.overview");

  return (
    <ProtectedRoute allowedRoles={ADMIN_ROUTE_ACCESS.allowedRoles}>
      <PageLayout>
        <PageHeader title={t("title")} description={t("description")} />

        <PageSection>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-4 rounded" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-9 w-16" />
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="mt-6">
            <CardHeader>
              <Skeleton className="h-5 w-48" />
              <Skeleton className="mt-2 h-4 w-full max-w-md" />
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-20 w-full rounded-lg" />
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="mt-6">
            <CardHeader>
              <Skeleton className="h-5 w-40" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-32 w-full" />
            </CardContent>
          </Card>
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
