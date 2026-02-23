"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils/cn";

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

export function AverageTimeWidget({
  averageTimeSeconds,
  totalAttempts,
  isLoading,
}: AverageTimeWidgetProps) {
  const t = useTranslations("dashboard.averageTime");

  if (isLoading) {
    return (
      <Card className="bg-card border-primary/20 animate-pulse h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="h-6 w-48 bg-muted rounded" />
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="h-12 w-32 bg-muted rounded" />
        </CardContent>
      </Card>
    );
  }

  const hasData = totalAttempts > 0 && averageTimeSeconds > 0;

  return (
    <Card className="bg-card border-primary/20 h-full flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <Clock className="w-5 h-5 text-primary-on-dark" />
          {t("title", { default: "Tempo moyen" })}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="space-y-2">
          <div
            className={cn(
              "text-2xl font-bold",
              hasData ? "text-primary" : "text-muted-foreground"
            )}
          >
            {hasData
              ? formatAverageTime(averageTimeSeconds)
              : t("noData", { default: "—" })}
          </div>
          <p className="text-sm text-muted-foreground">
            {hasData
              ? t("description", {
                  default: "Temps moyen par exercice",
                })
              : t("emptyHint", {
                  default: "Fais des exercices pour voir ton tempo.",
                })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
