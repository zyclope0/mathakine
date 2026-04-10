"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
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
import { BarChart3, MousePointer, Clock, Zap, Target, Swords, Users } from "lucide-react";
import Link from "next/link";
import { AdminReadHeavyPageShell } from "@/components/admin/AdminReadHeavyPageShell";

const EVENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  quick_start_click: MousePointer,
  first_attempt: Target,
};

function localeTag(locale: string): string {
  return locale === "en" ? "en-US" : "fr-FR";
}

export default function AdminAnalyticsPage() {
  const t = useTranslations("adminPages.analytics");
  const locale = useLocale();
  const dateLocale = localeTag(locale);

  const [period, setPeriod] = useState<"7d" | "30d">("7d");
  const [eventFilter, setEventFilter] = useState<string>("");

  const { data, isLoading, error } = useAdminEdTechAnalytics(period, eventFilter || undefined);

  const eventLabels = useMemo(
    () => ({
      quick_start_click: t("eventQuickStart"),
      first_attempt: t("eventFirstAttempt"),
    }),
    [t]
  );

  const toolbar = (
    <>
      <Select value={period} onValueChange={(v) => setPeriod(v as "7d" | "30d")}>
        <SelectTrigger className="w-[140px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="7d">{t("period7d")}</SelectItem>
          <SelectItem value="30d">{t("period30d")}</SelectItem>
        </SelectContent>
      </Select>
      <Select
        value={eventFilter || "all"}
        onValueChange={(v) => setEventFilter(v === "all" ? "" : v)}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder={t("eventsPlaceholder")} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">{t("eventsAll")}</SelectItem>
          <SelectItem value="quick_start_click">{t("eventQuickStart")}</SelectItem>
          <SelectItem value="first_attempt">{t("eventFirstAttempt")}</SelectItem>
        </SelectContent>
      </Select>
    </>
  );

  return (
    <AdminReadHeavyPageShell
      title={t("title")}
      description={t("description")}
      toolbar={toolbar}
      hasError={!!error}
      errorMessage={t("errorLoading")}
      isLoading={isLoading}
      loadingMessage={t("loading")}
      isEmpty={!error && !isLoading && !data}
      emptyMessage={t("empty")}
    >
      {data ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("kpi.uniqueUsers")}</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{data.unique_users ?? 0}</p>
                <p className="text-xs text-muted-foreground">{t("kpi.periodHint")}</p>
              </CardContent>
            </Card>
            {data.ctr_summary && data.ctr_summary.total_clicks > 0 && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">{t("kpi.quickStartClicks")}</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{data.ctr_summary.total_clicks}</p>
                  <p className="text-xs text-muted-foreground">
                    {t("ctrGuidedDetail", {
                      guided: data.ctr_summary.guided_clicks,
                      pct: data.ctr_summary.guided_rate_pct,
                    })}
                  </p>
                  {data.ctr_summary.by_type &&
                    (data.ctr_summary.by_type.exercise > 0 ||
                      data.ctr_summary.by_type.challenge > 0) && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("exChallengesRow", {
                          ex: data.ctr_summary.by_type.exercise,
                          ch: data.ctr_summary.by_type.challenge,
                        })}
                      </p>
                    )}
                </CardContent>
              </Card>
            )}
            {data.aggregates?.first_attempt && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">{t("kpi.firstAttempts")}</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{data.aggregates.first_attempt.count}</p>
                  <p className="text-xs text-muted-foreground">
                    {data.aggregates.first_attempt.avg_time_to_first_attempt_ms != null &&
                    data.aggregates.first_attempt.avg_time_to_first_attempt_ms >= 0
                      ? t("avgTimeApprox", {
                          seconds: Math.round(
                            data.aggregates.first_attempt.avg_time_to_first_attempt_ms / 1000
                          ),
                        })
                      : t("dash")}
                  </p>
                  {data.aggregates.first_attempt.by_type &&
                    (data.aggregates.first_attempt.by_type.exercise > 0 ||
                      data.aggregates.first_attempt.by_type.challenge > 0) && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("exChallengesRow", {
                          ex: data.aggregates.first_attempt.by_type.exercise,
                          ch: data.aggregates.first_attempt.by_type.challenge,
                        })}
                      </p>
                    )}
                </CardContent>
              </Card>
            )}
            {data.aggregates?.first_attempt?.avg_time_to_first_attempt_ms != null && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">{t("kpi.avgTimeTitle")}</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">
                    {Math.round(
                      (data.aggregates.first_attempt.avg_time_to_first_attempt_ms ?? 0) / 1000
                    )}
                    {t("kpi.secondsSuffix")}
                  </p>
                  <p className="text-xs text-muted-foreground">{t("kpi.fromQuickStart")}</p>
                </CardContent>
              </Card>
            )}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                {t("eventsListTitle")}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {t("periodLine", {
                  period: data.period,
                  since: data.since
                    ? new Date(data.since).toLocaleDateString(dateLocale)
                    : t("dash"),
                })}
              </p>
            </CardHeader>
            <CardContent>
              {data.events.length === 0 ? (
                <div className="rounded-md border border-dashed p-12 text-center text-muted-foreground">
                  <BarChart3 className="mx-auto mb-3 h-12 w-12 opacity-50" />
                  <p>{t("emptyEventsTitle")}</p>
                  <p className="mt-1 text-sm">{t("emptyEventsHint")}</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("colDate")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colEvent")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colUserId")}</th>
                        <th className="px-4 py-3 text-left font-medium">{t("colDetails")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.events.map((item) => {
                        const Icon = EVENT_ICONS[item.event] ?? BarChart3;
                        const payload = item.payload ?? {};
                        const type = payload.type as string | undefined;
                        const guided = payload.guided as boolean | undefined;
                        const targetId = payload.targetId as number | undefined;
                        const timeMs = payload.timeToFirstAttemptMs as number | undefined;

                        return (
                          <tr key={item.id} className="border-b last:border-0 hover:bg-muted/50">
                            <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                              {item.created_at
                                ? new Date(item.created_at).toLocaleString(dateLocale)
                                : "-"}
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant="outline" className="flex w-fit items-center gap-1">
                                <Icon className="h-3 w-3" />
                                {eventLabels[item.event as keyof typeof eventLabels] ?? item.event}
                              </Badge>
                            </td>
                            <td className="px-4 py-3">
                              {item.user_id ?? (
                                <span className="text-muted-foreground">{t("dash")}</span>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex flex-wrap gap-2">
                                {type && (
                                  <Badge variant="secondary" className="text-xs">
                                    {type === "exercise" ? (
                                      <span className="flex items-center gap-1">
                                        {t("typeExercise")}
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
                                        {t("typeChallenge")}
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
                                    variant={guided ? "default" : "outline"}
                                    className="text-xs"
                                  >
                                    {guided ? t("guided") : t("free")}
                                  </Badge>
                                )}
                                {timeMs != null && timeMs >= 0 && (
                                  <span className="text-muted-foreground text-xs">
                                    {t("timeApprox", { seconds: Math.round(timeMs / 1000) })}
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
      ) : null}
    </AdminReadHeavyPageShell>
  );
}
