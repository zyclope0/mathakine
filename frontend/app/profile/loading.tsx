"use client";

import { useTranslations } from "next-intl";
import { User } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader } from "@/components/layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Fallback segment /profile — header + nav latérale + sections principales (structure page profil).
 */
export default function ProfileLoading() {
  const t = useTranslations("profile");

  return (
    <ProtectedRoute>
      <PageLayout maxWidth="lg">
        <PageHeader title={t("title")} description={t("description")} icon={User} />

        <div className="mx-auto flex max-w-6xl flex-col gap-8 md:grid md:grid-cols-12 md:gap-12">
          <aside className="space-y-2 md:col-span-3" aria-hidden>
            <Skeleton className="h-10 w-full md:hidden" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="hidden h-10 w-full rounded-lg md:block" />
            ))}
          </aside>

          <div className="space-y-8 md:col-span-9">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-56" />
              </CardHeader>
              <CardContent className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-10 w-full max-w-sm" />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Skeleton className="h-24 w-full rounded-lg" />
                  <Skeleton className="h-24 w-full rounded-lg" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}
