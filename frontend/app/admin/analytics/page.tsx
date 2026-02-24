"use client";

import { useState } from "react";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminEdTechAnalytics } from "@/hooks/useAdminEdTechAnalytics";
import {
  BarChart3,
  MousePointer,
  Clock,
  Zap,
  Target,
  Swords,
} from "lucide-react";
import Link from "next/link";

const EVENT_LABELS: Record<string, string> = {
  quick_start_click: "Clic Quick Start",
  first_attempt: "1er attempt",
};

const EVENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  quick_start_click: MousePointer,
  first_attempt: Target,
};

export default function AdminAnalyticsPage() {
  const [period, setPeriod] = useState<"7d" | "30d">("7d");
  const [eventFilter, setEventFilter] = useState<string>("");

  const { data, isLoading, error } = useAdminEdTechAnalytics(
    period,
    eventFilter || undefined
  );

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics EdTech"
        description="CTR Quick Start, temps vers 1er attempt, conversion exercice/défi — données du bloc parcours guidé"
      />

      <PageSection>
        <div className="flex flex-wrap gap-4 items-center mb-4">
          <Select
            value={period}
            onValueChange={(v) => setPeriod(v as "7d" | "30d")}
          >
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">7 derniers jours</SelectItem>
              <SelectItem value="30d">30 derniers jours</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={eventFilter || "all"}
            onValueChange={(v) => setEventFilter(v === "all" ? "" : v)}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Tous les événements" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les événements</SelectItem>
              <SelectItem value="quick_start_click">Clic Quick Start</SelectItem>
              <SelectItem value="first_attempt">1er attempt</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {error ? (
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-destructive">
                Erreur de chargement. Vérifiez vos droits admin.
              </p>
            </CardContent>
          </Card>
        ) : isLoading ? (
          <LoadingState message="Chargement des analytics..." />
        ) : !data ? (
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-muted-foreground">Aucune donnée.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* KPIs */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {data.ctr_summary && data.ctr_summary.total_clicks > 0 && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">
                      Clics Quick Start
                    </CardTitle>
                    <Zap className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {data.ctr_summary.total_clicks}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {data.ctr_summary.guided_clicks} guidés (
                      {data.ctr_summary.guided_rate_pct}%)
                    </p>
                  </CardContent>
                </Card>
              )}
              {data.aggregates?.first_attempt && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">
                      1ers attempts
                    </CardTitle>
                    <Target className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {data.aggregates.first_attempt.count}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {data.aggregates.first_attempt.avg_time_to_first_attempt_ms !=
                      null
                        ? `~${Math.round(
                            data.aggregates.first_attempt
                              .avg_time_to_first_attempt_ms / 1000
                          )}s en moyenne`
                        : "—"}
                    </p>
                  </CardContent>
                </Card>
              )}
              {data.aggregates?.first_attempt?.avg_time_to_first_attempt_ms !=
                null && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">
                      Temps moyen → 1er attempt
                    </CardTitle>
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {Math.round(
                        (data.aggregates.first_attempt
                          .avg_time_to_first_attempt_ms ?? 0) / 1000
                      )}
                      s
                    </p>
                    <p className="text-xs text-muted-foreground">
                      depuis la vue du dashboard
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Liste des événements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Derniers événements
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Période : {data.period} (depuis{" "}
                  {data.since
                    ? new Date(data.since).toLocaleDateString("fr-FR")
                    : "—"}
                  )
                </p>
              </CardHeader>
              <CardContent>
                {data.events.length === 0 ? (
                  <div className="rounded-md border border-dashed p-12 text-center text-muted-foreground">
                    <BarChart3 className="mx-auto mb-3 h-12 w-12 opacity-50" />
                    <p>Aucun événement pour cette période.</p>
                    <p className="mt-1 text-sm">
                      Les événements sont collectés lorsqu&apos;un utilisateur
                      clique sur Quick Start ou soumet un premier attempt.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="px-4 py-3 text-left font-medium">
                            Date
                          </th>
                          <th className="px-4 py-3 text-left font-medium">
                            Événement
                          </th>
                          <th className="px-4 py-3 text-left font-medium">
                            User ID
                          </th>
                          <th className="px-4 py-3 text-left font-medium">
                            Détails
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.events.map((item) => {
                          const Icon =
                            EVENT_ICONS[item.event] ?? BarChart3;
                          const payload = item.payload ?? {};
                          const type = payload.type as string | undefined;
                          const guided = payload.guided as boolean | undefined;
                          const targetId = payload.targetId as number | undefined;
                          const timeMs = payload.timeToFirstAttemptMs as
                            | number
                            | undefined;

                          return (
                            <tr
                              key={item.id}
                              className="border-b last:border-0 hover:bg-muted/50"
                            >
                              <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                                {item.created_at
                                  ? new Date(
                                      item.created_at
                                    ).toLocaleString("fr-FR")
                                  : "-"}
                              </td>
                              <td className="px-4 py-3">
                                <Badge
                                  variant="outline"
                                  className="flex w-fit items-center gap-1"
                                >
                                  <Icon className="h-3 w-3" />
                                  {EVENT_LABELS[item.event] ?? item.event}
                                </Badge>
                              </td>
                              <td className="px-4 py-3">
                                {item.user_id ?? (
                                  <span className="text-muted-foreground">
                                    —
                                  </span>
                                )}
                              </td>
                              <td className="px-4 py-3">
                                <div className="flex flex-wrap gap-2">
                                  {type && (
                                    <Badge variant="secondary" className="text-xs">
                                      {type === "exercise" ? (
                                        <span className="flex items-center gap-1">
                                          Exercice
                                          {targetId && (
                                            <Link
                                              href={`/exercises/${targetId}`}
                                              className="hover:underline"
                                            >
                                              #{targetId}
                                            </Link>
                                          )}
                                        </span>
                                      ) : (
                                        <span className="flex items-center gap-1">
                                          <Swords className="h-3 w-3" />
                                          Défi
                                          {targetId && (
                                            <Link
                                              href={`/challenge/${targetId}`}
                                              className="hover:underline"
                                            >
                                              #{targetId}
                                            </Link>
                                          )}
                                        </span>
                                      )}
                                    </Badge>
                                  )}
                                  {guided !== undefined && (
                                    <Badge
                                      variant={
                                        guided ? "default" : "outline"
                                      }
                                      className="text-xs"
                                    >
                                      {guided ? "Guidé" : "Libre"}
                                    </Badge>
                                  )}
                                  {timeMs != null && (
                                    <span className="text-muted-foreground text-xs">
                                      ~{Math.round(timeMs / 1000)}s
                                    </span>
                                  )}
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </PageSection>
    </div>
  );
}
