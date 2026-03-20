"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { RECHARTS_TOOLTIP_STYLE } from "@/lib/utils/chart";
import type { ProgressByCategory } from "@/hooks/useProgressStats";
import { DashboardDataScopeBadge } from "@/components/dashboard/DashboardDataScopeBadge";

interface VolumeByTypeChartProps {
  categoryData: Record<string, ProgressByCategory>;
}

export function VolumeByTypeChart({ categoryData }: VolumeByTypeChartProps) {
  const t = useTranslations("dashboard.charts.volumeByType");
  const tExercises = useTranslations("exercises");
  const { shouldReduceMotion } = useAccessibleAnimation();

  const chartData = useMemo(() => {
    return Object.entries(categoryData)
      .map(([key, data]) => {
        const categoryKey = key.toLowerCase().replace("exercises.types.", "");
        const attempts = data.attempts ?? data.completed ?? 0;
        return {
          name: tExercises(`types.${categoryKey}`, { defaultValue: categoryKey }),
          typeKey: key,
          attempts,
          correct:
            data.correct ??
            Math.round((data.accuracy ?? 0) * (data.attempts ?? data.completed ?? 0)),
          accuracy: data.accuracy ?? 0,
        };
      })
      .filter((d) => d.attempts > 0)
      .sort((a, b) => b.attempts - a.attempts);
  }, [categoryData, tExercises]);

  const chartDescription = useMemo(() => {
    return chartData.map((d) => `${d.name}: ${d.attempts} ${t("attemptsLabel")}`).join(", ");
  }, [chartData, t]);

  if (chartData.length === 0) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md">
        <CardHeader className="flex flex-col gap-2 space-y-0 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
          <DashboardDataScopeBadge />
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12 text-muted-foreground text-sm">
            {t("noData")}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-md">
      <CardHeader className="flex flex-col gap-2 space-y-0 sm:flex-row sm:items-center sm:justify-between">
        <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        <DashboardDataScopeBadge />
      </CardHeader>
      <CardContent>
        <div
          className="h-[300px] w-full"
          role="img"
          aria-label={t("ariaLabel")}
          aria-describedby="volume-by-type-chart-description"
        >
          <div id="volume-by-type-chart-description" className="sr-only">
            {chartDescription}
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ left: 8, right: 0, top: 4, bottom: 4 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                strokeOpacity={0.4}
                horizontal={false}
              />
              <XAxis
                type="number"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "11px" }}
                allowDecimals={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
                width={80}
                tickLine={false}
              />
              <Tooltip
                contentStyle={RECHARTS_TOOLTIP_STYLE}
                formatter={(value, _name, item) => {
                  const payload =
                    (
                      item as {
                        payload?: {
                          attempts?: number;
                          correct?: number;
                          accuracy?: number;
                        };
                      }
                    )?.payload ?? {};
                  const numericValue = typeof value === "number" ? value : Number(value ?? 0);
                  const attempts = payload.attempts ?? numericValue;
                  const correct = payload.correct ?? 0;
                  const accuracy = payload.accuracy ?? 0;
                  const pct = attempts > 0 ? Math.round(accuracy * 100) : 0;

                  return [
                    `${numericValue} ${t("attemptsLabel")}${
                      attempts > 0 ? ` - ${correct}/${attempts} (${pct}%)` : ""
                    }`,
                    "",
                  ];
                }}
                labelFormatter={(label) => label}
              />
              <Bar
                dataKey="attempts"
                fill="var(--color-chart-2)"
                stroke="var(--color-chart-2)"
                strokeWidth={1}
                strokeOpacity={0.6}
                radius={[0, 4, 4, 0]}
                isAnimationActive={!shouldReduceMotion}
                animationDuration={600}
                animationEasing="ease-out"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
