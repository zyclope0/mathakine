"use client";

import { useState } from "react";
import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";
import { useAdminOverview } from "@/hooks/useAdminOverview";
import { useAdminReports } from "@/hooks/useAdminReports";
import { PageLayout, PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Users, BookOpen, Puzzle, Target, Download, BarChart3 } from "lucide-react";
import { api } from "@/lib/api/client";
import { toast } from "sonner";

const EXPORT_TYPES = [
  { value: "users", label: "Utilisateurs" },
  { value: "exercises", label: "Exercices" },
  { value: "attempts", label: "Tentatives" },
  { value: "overview", label: "Vue d'ensemble" },
];

const EXPORT_PERIODS = [
  { value: "all", label: "Tout" },
  { value: "30d", label: "30 derniers jours" },
  { value: "7d", label: "7 derniers jours" },
];

export default function AdminPage() {
  const { user, isLoading: authLoading } = useAuth();
  const { overview, isLoading: overviewLoading, error } = useAdminOverview();
  const router = useRouter();
  const [exportType, setExportType] = useState("users");
  const [exportPeriod, setExportPeriod] = useState("all");
  const [isExporting, setIsExporting] = useState(false);
  const [reportsPeriod, setReportsPeriod] = useState<"7d" | "30d">("7d");

  const { reports, isLoading: reportsLoading } = useAdminReports(reportsPeriod);

  const isAdmin = user?.role === "archiviste";

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await api.downloadCsv(
        `/api/admin/export?type=${encodeURIComponent(exportType)}&period=${encodeURIComponent(exportPeriod)}`,
        `mathakine_export_${exportType}_${exportPeriod}.csv`
      );
      toast.success("Export téléchargé");
    } catch (err) {
      toast.error("Erreur", {
        description: err instanceof Error ? err.message : "Échec du téléchargement",
      });
    } finally {
      setIsExporting(false);
    }
  };

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
        <PageHeader title="Espace Admin" description="Vue d'ensemble de la plateforme" />

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
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Link href="/admin/users">
                  <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium">Utilisateurs</CardTitle>
                      <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{overview.total_users}</p>
                    </CardContent>
                  </Card>
                </Link>
                <Link href="/admin/content">
                  <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium">Exercices</CardTitle>
                      <BookOpen className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{overview.total_exercises}</p>
                    </CardContent>
                  </Card>
                </Link>
                <Link href="/admin/content">
                  <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium">Défis</CardTitle>
                      <Puzzle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{overview.total_challenges}</p>
                    </CardContent>
                  </Card>
                </Link>
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

              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Rapports par période
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Inscriptions, activité et taux de succès sur la période choisie.
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-3 items-end mb-4">
                    <Select
                      value={reportsPeriod}
                      onValueChange={(v) => setReportsPeriod(v as "7d" | "30d")}
                    >
                      <SelectTrigger className="w-[160px]">
                        <SelectValue placeholder="Période" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7d">7 derniers jours</SelectItem>
                        <SelectItem value="30d">30 derniers jours</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {reportsLoading ? (
                    <p className="text-sm text-muted-foreground">Chargement...</p>
                  ) : reports ? (
                    <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
                      <div className="rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground">Inscriptions</p>
                        <p className="text-xl font-bold">{reports.new_users}</p>
                      </div>
                      <div className="rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground">Utilisateurs actifs</p>
                        <p className="text-xl font-bold">{reports.active_users}</p>
                      </div>
                      <div className="rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground">
                          Tentatives (exercices + défis)
                        </p>
                        <p className="text-xl font-bold">{reports.total_attempts}</p>
                      </div>
                      <div className="rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground">Taux de succès</p>
                        <p className="text-xl font-bold">{reports.success_rate}%</p>
                      </div>
                    </div>
                  ) : null}
                </CardContent>
              </Card>

              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Export CSV
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Téléchargez les données au format CSV (max 10 000 lignes).
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-3 items-end">
                    <Select value={exportType} onValueChange={setExportType}>
                      <SelectTrigger className="w-[160px]">
                        <SelectValue placeholder="Type" />
                      </SelectTrigger>
                      <SelectContent>
                        {EXPORT_TYPES.map((t) => (
                          <SelectItem key={t.value} value={t.value}>
                            {t.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={exportPeriod} onValueChange={setExportPeriod}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Période" />
                      </SelectTrigger>
                      <SelectContent>
                        {EXPORT_PERIODS.map((p) => (
                          <SelectItem key={p.value} value={p.value}>
                            {p.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button onClick={handleExport} disabled={isExporting}>
                      {isExporting ? "Téléchargement..." : "Télécharger"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
