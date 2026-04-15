"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { Clock, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

interface AverageTimeWidgetProps {
  averageTimeSeconds: number;
  totalAttempts: number;
  isLoading?: boolean;
}

function formatAverageTime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)} s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return secs > 0 ? `${mins} min ${secs} s` : `${mins} min`;
}

function getPerformanceHintKey(seconds: number): string {
  if (seconds <= 30) return "hintExcellent";
  if (seconds <= 60) return "hintGood";
  if (seconds <= 120) return "hintSteady";
  return "hintSlow";
}

function getPerformanceColor(seconds: number): string {
  if (seconds <= 30) return "text-success";
  if (seconds <= 60) return "text-primary";
  if (seconds <= 120) return "text-warning";
  return "text-destructive";
}

export function AverageTimeWidget({
  averageTimeSeconds,
  totalAttempts,
  isLoading,
}: AverageTimeWidgetProps) {
  const t = useTranslations("dashboard.averageTime");

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-48">
        <Skeleton className="h-12 w-32" />
      </DashboardWidgetSkeleton>
    );
  }

  const hasData = totalAttempts > 0 && averageTimeSeconds > 0;
  const hintKey = hasData ? getPerformanceHintKey(averageTimeSeconds) : null;
  const hintColor = hasData ? getPerformanceColor(averageTimeSeconds) : "text-muted-foreground";

  return (
    <Card className="dashboard-card-surface">
      <CardContent className="p-5">
        <div className="flex items-center gap-5">
          <div className="dashboard-card-icon-chip h-14 w-14 rounded-2xl">
            <Clock className="h-7 w-7 text-primary" />
          </div>

          <div className="flex-1 min-w-0">
            <p className="heading-kicker mb-0.5">{t("title", { default: "Tempo moyen" })}</p>
            <div
              className={cn(
                "text-3xl font-black tabular-nums leading-none",
                hasData ? "text-foreground" : "text-muted-foreground"
              )}
            >
              {hasData ? formatAverageTime(averageTimeSeconds) : t("noData", { default: "—" })}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {t("description", { default: "Temps moyen par exercice" })}
            </p>
          </div>

          {hasData && hintKey && (
            <div className="flex-shrink-0 flex flex-col items-end gap-1 text-right">
              <div className="flex items-center gap-1.5">
                <TrendingUp className={cn("h-3.5 w-3.5", hintColor)} />
                <span className={cn("text-xs font-semibold", hintColor)}>
                  {t(hintKey as Parameters<typeof t>[0])}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">
                {totalAttempts.toLocaleString()} {t("exercises", { default: "exercices analysés" })}
              </span>
            </div>
          )}

          {!hasData && (
            <p className="flex-shrink-0 max-w-[140px] text-right text-sm text-muted-foreground">
              {t("emptyHint", { default: "Fais des exercices pour voir ton tempo." })}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
