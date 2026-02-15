"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";
import { useAdminOverview } from "@/hooks/useAdminOverview";
import { PageLayout, PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, BookOpen, Puzzle, Target } from "lucide-react";

export default function AdminPage() {
  const { user, isLoading: authLoading } = useAuth();
  const { overview, isLoading: overviewLoading, error } = useAdminOverview();
  const router = useRouter();

  const isAdmin = user?.role === "archiviste";

  useEffect(() => {
    if (!authLoading && user && !isAdmin) {
      router.push("/dashboard");
    }
  }, [authLoading, user, isAdmin, router]);

  if (!user && !authLoading) return null;
  if (!isAdmin && user) return null; // Redirection en cours

  return (
    <ProtectedRoute>
      <PageLayout>
        <PageHeader
          title="Espace Admin"
          description="Vue d'ensemble de la plateforme"
        />

        <PageSection>
          {error ? (
            <Card>
              <CardContent className="py-12">
                <p className="text-center text-destructive">
                  Erreur de chargement. Droits insuffisants ou API indisponible.
                </p>
              </CardContent>
            </Card>
          ) : overviewLoading ? (
            <LoadingState message="Chargement..." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Utilisateurs</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{overview.total_users}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Exercices</CardTitle>
                  <BookOpen className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{overview.total_exercises}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Défis</CardTitle>
                  <Puzzle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{overview.total_challenges}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">Tentatives</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{overview.total_attempts}</p>
                </CardContent>
              </Card>
            </div>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
