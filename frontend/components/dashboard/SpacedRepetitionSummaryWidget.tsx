"use client";

import { useMemo } from "react";
import { parseISO } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { format } from "date-fns";
import { CalendarDays } from "lucide-react";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { cn } from "@/lib/utils";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";

export interface SpacedRepetitionSummaryWidgetProps {
  summary: SpacedRepetitionUserSummary;
  isLoading?: boolean;
  /** Erreur stats (ex. validation) — message localisé sans casser toute la page */
  hasError?: boolean;
}

function utcTodayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

function isStrictlyFutureReview(isoDate: string, todayUtc: string): boolean {
  return isoDate.length === 10 && isoDate > todayUtc;
}

/**
 * Résumé F04 — lecture seule, pas de session SR.
 * Charge cognitive : une carte, un message principal, détails en second plan.
 */
export function SpacedRepetitionSummaryWidget({
  summary,
  isLoading = false,
  hasError = false,
}: SpacedRepetitionSummaryWidgetProps) {
  const t = useTranslations("dashboard.spacedRepetition");
  const { locale } = useLocaleStore();
  const dateLocale = locale === "en" ? enUS : fr;
  const todayUtc = useMemo(() => utcTodayIsoDate(), []);

  const nextReviewFormatted = useMemo(() => {
    const d = summary.next_review_date;
    if (!d || !isStrictlyFutureReview(d, todayUtc)) {
      return null;
    }
    try {
      return format(parseISO(`${d}T12:00:00.000Z`), "PPP", { locale: dateLocale });
    } catch {
      return d;
    }
  }, [summary.next_review_date, todayUtc, dateLocale]);

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-48">
        <div className="space-y-2">
          <Skeleton className="h-8 w-16" aria-hidden />
          <Skeleton className="h-4 w-full max-w-md" aria-hidden />
        </div>
      </DashboardWidgetSkeleton>
    );
  }

  if (hasError) {
    return (
      <Card
        className="dashboard-card-surface border-dashed"
        role="region"
        aria-label={t("a11y.regionLabel")}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold flex items-center gap-2 text-foreground">
            <CalendarDays className="h-5 w-5 text-muted-foreground shrink-0" aria-hidden />
            {t("title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{t("loadError")}</p>
        </CardContent>
      </Card>
    );
  }

  const { f04_initialized, active_cards_count, due_today_count, overdue_count } = summary;

  const primaryTone =
    due_today_count > 0
      ? "border-primary/25 bg-primary/5"
      : overdue_count > 0 && f04_initialized
        ? "border-amber-500/30 bg-amber-500/5"
        : "border-border";

  return (
    <Card
      className={cn("dashboard-card-surface", primaryTone)}
      role="region"
      aria-label={t("a11y.regionLabel")}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold flex items-center gap-2 text-foreground">
          <CalendarDays className="h-5 w-5 text-primary shrink-0" aria-hidden />
          {t("title")}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {!f04_initialized ? (
          <p className="text-muted-foreground leading-relaxed">{t("notInitialized")}</p>
        ) : (
          <>
            {due_today_count > 0 ? (
              <p className="text-base font-semibold text-foreground" role="status">
                {t("dueToday", { count: due_today_count })}
              </p>
            ) : (
              <p className="text-foreground/90 leading-relaxed" role="status">
                {t("noneToday")}
              </p>
            )}

            {overdue_count > 0 ? (
              <p className="text-sm text-amber-800 dark:text-amber-200/90">
                {t("overdue", { count: overdue_count })}
              </p>
            ) : null}

            <p className="text-xs text-muted-foreground">
              {t("activeCards", { count: active_cards_count })}
            </p>

            {nextReviewFormatted ? (
              <p className="text-xs text-muted-foreground">
                {t("nextReview", { date: nextReviewFormatted })}
              </p>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}
