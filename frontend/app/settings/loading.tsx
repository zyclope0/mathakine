"use client";

import { useTranslations } from "next-intl";
import { Settings } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader } from "@/components/layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Fallback segment /settings — header + grille sidebar / contenu (hiérarchie page paramètres).
 */
export default function SettingsLoading() {
  const t = useTranslations("settings");

  return (
    <ProtectedRoute>
      <PageLayout maxWidth="lg">
        <PageHeader title={t("title")} description={t("description")} icon={Settings} />

        <div className="mx-auto flex max-w-6xl flex-col gap-8 md:grid md:grid-cols-12 md:gap-12">
          <aside className="space-y-2 md:col-span-3" aria-hidden>
            <Skeleton className="h-10 w-full md:hidden" />
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="hidden h-10 w-full rounded-lg md:block" />
            ))}
          </aside>

          <div className="space-y-8 md:col-span-9">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-3/4" />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          </div>
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}
