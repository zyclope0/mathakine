"use client";

import { useMemo } from "react";
import { AlertCircle, CalendarCheck } from "lucide-react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useProgressTimeline, type TimelinePeriod } from "@/hooks/useProgressTimeline";
import {
  buildDailyPresenceFlags,
  computePracticeConsistency,
} from "@/lib/dashboard/practiceConsistency";
import { formatShortDate } from "@/lib/utils/format";
import { useLocaleStore } from "@/lib/stores/localeStore";

interface PracticeConsistencyWidgetProps {
  /** Same period as `ProgressTimelineWidget` — shared React Query cache. */
  period: TimelinePeriod;
}

function PresenceStrip({ flags, label }: { flags: boolean[]; label: string }) {
  return (
    <div className="flex flex-wrap gap-1 pt-1" role="img" aria-label={label}>
      {flags.map((active, i) => (
        <span
          key={i}
          className={`h-2 w-2 shrink-0 rounded-sm ${active ? "bg-primary" : "bg-muted"}`}
          aria-hidden
        />
      ))}
    </div>
  );
}

export function PracticeConsistencyWidget({ period }: PracticeConsistencyWidgetProps) {
  const { data, isLoading, error } = useProgressTimeline(period);
  const t = useTranslations("dashboard.charts.practiceConsistency");
  const { locale } = useLocaleStore();
  const dateLocale = locale === "en" ? "en-US" : "fr-FR";

  const metrics = useMemo(() => {
    if (!data?.points || !data.from || !data.to) return null;
    return computePracticeConsistency(
      data.from,
      data.to,
      data.points,
      data.summary?.total_attempts ?? 0
    );
  }, [data]);

  const presenceFlags = useMemo(() => {
    if (!data?.points || !data.from || !data.to) return [];
    return buildDailyPresenceFlags(data.from, data.to, data.points);
  }, [data]);

  const stripAriaLabel = useMemo(() => {
    if (!metrics) return "";
    return t("presenceAria", {
      active: metrics.activeDays,
      total: metrics.totalDaysInPeriod,
    });
  }, [metrics, t]);

  if (isLoading) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-6 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-2 py-8 text-muted-foreground" role="alert">
            <AlertCircle className="h-8 w-8" aria-hidden />
            <p className="text-sm text-center">{t("error")}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isEmpty = !data?.summary || data.summary.total_attempts === 0;

  if (isEmpty || !metrics) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl text-foreground flex items-center gap-2">
            <CalendarCheck className="h-5 w-5 shrink-0 text-primary" aria-hidden />
            {t("title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">{t("empty")}</p>
        </CardContent>
      </Card>
    );
  }

  const mostActiveLabel = metrics.mostActiveDay
    ? `${formatShortDate(metrics.mostActiveDay.date, dateLocale)} · ${t("attemptsUnit", { count: metrics.mostActiveDay.attempts })}`
    : "—";

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-md h-full flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl text-foreground flex items-center gap-2">
          <CalendarCheck className="h-5 w-5 shrink-0 text-primary" aria-hidden />
          {t("title")}
        </CardTitle>
        <p className="text-xs text-muted-foreground pt-1">{t("subtitle")}</p>
      </CardHeader>
      <CardContent className="space-y-4 flex-1 flex flex-col">
        {presenceFlags.length > 0 ? (
          <PresenceStrip flags={presenceFlags} label={stripAriaLabel} />
        ) : null}

        <dl className="grid grid-cols-2 gap-3 text-sm flex-1">
          <div className="rounded-md border border-border/60 bg-muted/20 px-3 py-2">
            <dt className="text-muted-foreground text-xs">{t("activeDays")}</dt>
            <dd className="text-lg font-semibold tabular-nums text-foreground">
              {metrics.activeDays}
              <span className="text-muted-foreground font-normal text-sm">
                {" "}
                / {metrics.totalDaysInPeriod}
              </span>
            </dd>
          </div>
          <div className="rounded-md border border-border/60 bg-muted/20 px-3 py-2">
            <dt className="text-muted-foreground text-xs">{t("regularityPercent")}</dt>
            <dd className="text-lg font-semibold tabular-nums text-foreground">
              {metrics.regularityPercent}%
            </dd>
          </div>
          <div className="rounded-md border border-border/60 bg-muted/20 px-3 py-2">
            <dt className="text-muted-foreground text-xs">{t("avgPerActiveDay")}</dt>
            <dd className="text-lg font-semibold tabular-nums text-foreground">
              {metrics.activeDays > 0 ? metrics.avgAttemptsPerActiveDay : "—"}
            </dd>
          </div>
          <div className="col-span-2 rounded-md border border-border/60 bg-muted/20 px-3 py-2">
            <dt className="text-muted-foreground text-xs">{t("mostActiveDay")}</dt>
            <dd className="text-sm font-medium text-foreground leading-snug break-words">
              {mostActiveLabel}
            </dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
