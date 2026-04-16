"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { parseISO } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { format } from "date-fns";
import { CalendarDays, Loader2 } from "lucide-react";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { cn } from "@/lib/utils";
import { useNextReview } from "@/hooks/useNextReview";
import { storeSpacedReviewNext } from "@/lib/spacedReviewSession";
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
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    fetchNextReview,
    isLoading: isReviewNavLoading,
    error: reviewNavError,
    clearError,
  } = useNextReview();
  const [neutralNoCard, setNeutralNoCard] = useState(false);
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
      /* swallowed: invalid review date, ISO string used as fallback */
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
        className="dashboard-card-surface--calm border-dashed"
        role="region"
        aria-label={t("a11y.regionLabel")}
      >
        <CardHeader className="space-y-0 px-4 pb-2 pt-4">
          <CardTitle className="text-base font-semibold flex items-center gap-2 text-foreground">
            <CalendarDays className="h-5 w-5 text-muted-foreground shrink-0" aria-hidden />
            {t("title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-sm text-muted-foreground leading-relaxed">{t("loadError")}</p>
        </CardContent>
      </Card>
    );
  }

  const { f04_initialized, active_cards_count, due_today_count, overdue_count } = summary;

  const showReviewCta = f04_initialized && (due_today_count > 0 || overdue_count > 0);

  const handleReviewNow = async () => {
    clearError();
    setNeutralNoCard(false);
    const data = await fetchNextReview();
    if (!data) {
      return;
    }
    await queryClient.invalidateQueries({ queryKey: ["user", "stats"] });
    if (data.has_due_review && data.next_review) {
      storeSpacedReviewNext(data.next_review);
      router.push(`/exercises/${data.next_review.exercise_id}?session=spaced-review`);
      return;
    }
    setNeutralNoCard(true);
  };

  const primaryTone =
    due_today_count > 0
      ? "border-primary/30 bg-primary/[0.07]"
      : overdue_count > 0 && f04_initialized
        ? "border-warning/35 bg-warning/[0.08]"
        : "";

  return (
    <Card
      className={cn("dashboard-card-surface--calm", primaryTone)}
      role="region"
      aria-label={t("a11y.regionLabel")}
    >
      <CardHeader className="space-y-0 px-4 pb-2 pt-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2 text-foreground">
          <CalendarDays className="h-5 w-5 text-primary shrink-0" aria-hidden />
          {t("title")}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 px-4 pb-4 pt-1 text-sm">
        {!f04_initialized ? (
          <p className="text-muted-foreground leading-relaxed">{t("notInitialized")}</p>
        ) : (
          <>
            <div className="space-y-2">
              {due_today_count > 0 ? (
                <p className="text-base font-semibold text-foreground leading-snug" role="status">
                  {t("dueToday", { count: due_today_count })}
                </p>
              ) : (
                <p className="text-base text-foreground leading-snug" role="status">
                  {t("noneToday")}
                </p>
              )}

              {overdue_count > 0 ? (
                <p className="text-sm font-medium text-warning leading-snug">
                  {t("overdue", { count: overdue_count })}
                </p>
              ) : null}
            </div>

            <div className="text-sm text-muted-foreground leading-snug space-y-1">
              <p>{t("activeCards", { count: active_cards_count })}</p>
              {nextReviewFormatted ? <p>{t("nextReview", { date: nextReviewFormatted })}</p> : null}
            </div>

            {showReviewCta ? (
              <section
                className="pt-3 border-t border-border space-y-2"
                aria-label={t("a11y.ctaSection")}
              >
                <Button
                  type="button"
                  onClick={() => void handleReviewNow()}
                  disabled={isReviewNavLoading}
                  className="w-full min-h-11 min-w-[44px] justify-center px-6 py-3 text-base motion-reduce:transition-none"
                  aria-busy={isReviewNavLoading}
                >
                  {isReviewNavLoading ? (
                    <>
                      <Loader2
                        className="mr-2 h-5 w-5 shrink-0 animate-spin motion-reduce:animate-none"
                        aria-hidden
                      />
                      {t("reviewNowLoading")}
                    </>
                  ) : (
                    t("reviewNow")
                  )}
                </Button>
                {reviewNavError ? (
                  <p className="text-sm text-muted-foreground" role="status">
                    {t("reviewFetchError")}
                  </p>
                ) : null}
                {neutralNoCard && !reviewNavError ? (
                  <p className="text-sm text-muted-foreground" role="status">
                    {t("noReviewAvailable")}
                  </p>
                ) : null}
              </section>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}
