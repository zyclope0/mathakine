"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useProgressTimeline, type TimelinePeriod } from "@/hooks/useProgressTimeline";
import { formatShortDate } from "@/lib/utils/format";
import { RECHARTS_TOOLTIP_STYLE } from "@/lib/utils/chart";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle } from "lucide-react";
import { useLocaleStore } from "@/lib/stores/localeStore";

export function ProgressTimelineWidget() {
  const [period, setPeriod] = useState<TimelinePeriod>("7d");
  const { data, isLoading, error } = useProgressTimeline(period);
  const t = useTranslations("dashboard.charts.timeline");
  const { shouldReduceMotion } = useAccessibleAnimation();
  const { locale } = useLocaleStore();
  const dateLocale = locale === "en" ? "en-US" : "fr-FR";

  const chartData = useMemo(() => {
    const points = data?.points ?? [];
    return points.map((p) => ({
      name: p.date,
      attempts: p.attempts,
      successRate: p.success_rate_pct,
    }));
  }, [data?.points]);

  const chartDescription = useMemo(() => {
    return chartData
      .map(
        (d) =>
          `${formatShortDate(d.name, dateLocale)}: ${d.attempts} ${t("attemptsLabel")}, ${d.successRate}% ${t("successRateLabel")}`
      )
      .join(", ");
  }, [chartData, dateLocale, t]);

  if (isLoading) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px] w-full space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
            <Skeleton className="h-4 w-3/6" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground"
            role="alert"
          >
            <AlertCircle className="h-10 w-10" aria-hidden="true" />
            <p className="text-sm">{t("error", { default: "Unable to load data." })}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isEmpty = !data?.summary || data.summary.total_attempts === 0;

  if (isEmpty) {
    return (
      <Card className="border-border/50 bg-card/40 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <p className="text-sm">{t("empty", { default: "No attempts in this period." })}</p>
            <p className="text-xs mt-1">
              {t("emptyHint", { default: "Practice to see your evolution." })}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl text-foreground">{t("title")}</CardTitle>
        <Tabs
          value={period}
          onValueChange={(v) => setPeriod(v as TimelinePeriod)}
          className="w-auto"
        >
          <TabsList className="h-8">
            <TabsTrigger value="7d" className="text-xs px-3">
              {t("period7d", { default: "7d" })}
            </TabsTrigger>
            <TabsTrigger value="30d" className="text-xs px-3">
              {t("period30d", { default: "30d" })}
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        <div
          className="h-[280px] w-full"
          role="img"
          aria-label={t("ariaLabel", {
            default: "Timeline chart showing success rate and attempt volume by day",
          })}
          aria-describedby="timeline-chart-description"
        >
          <div id="timeline-chart-description" className="sr-only">
            {chartDescription}
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ bottom: period === "30d" ? 4 : 8, left: 4, right: 4, top: 4 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                strokeOpacity={0.4}
              />
              <XAxis
                dataKey="name"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "11px" }}
                angle={0}
                textAnchor="middle"
                height={period === "30d" ? 72 : 48}
                tickFormatter={(value) =>
                  typeof value === "string" ? formatShortDate(value, dateLocale) : String(value)
                }
                minTickGap={period === "30d" ? 36 : 24}
                interval={period === "30d" ? 2 : 0}
              />
              <YAxis
                yAxisId="left"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
                allowDecimals={false}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                contentStyle={RECHARTS_TOOLTIP_STYLE}
                labelFormatter={(label) => {
                  if (typeof label !== "string") return String(label);
                  try {
                    const d = new Date(label);
                    if (isNaN(d.getTime())) return label;
                    return d.toLocaleDateString(dateLocale, {
                      weekday: "short",
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    });
                  } catch {
                    return label;
                  }
                }}
                formatter={(value, name) => {
                  if (name === "attempts") {
                    return [value, t("attemptsLabel", { default: "Attempts" })];
                  }
                  if (name === "successRate") {
                    return [
                      `${typeof value === "number" ? Math.round(value) : value}%`,
                      t("successRateLabel", { default: "Success rate" }),
                    ];
                  }
                  return [value, String(name)];
                }}
              />
              <Legend
                wrapperStyle={{ color: "var(--color-muted-foreground)" }}
                formatter={(value: string) =>
                  value === "attempts"
                    ? t("attemptsLabel", { default: "Attempts" })
                    : t("successRateLabel", { default: "Success rate" })
                }
              />
              <Bar
                yAxisId="left"
                dataKey="attempts"
                fill="var(--color-chart-2)"
                stroke="var(--color-chart-2)"
                strokeWidth={1}
                strokeOpacity={0.6}
                radius={[4, 4, 0, 0]}
                isAnimationActive={!shouldReduceMotion}
                animationDuration={600}
                animationEasing="ease-out"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="successRate"
                stroke="var(--color-chart-1)"
                strokeWidth={2}
                dot={{ fill: "var(--color-chart-1)", r: 4 }}
                activeDot={{ r: 6, fill: "var(--color-chart-1)" }}
                isAnimationActive={!shouldReduceMotion}
                animationDuration={800}
                animationEasing="ease-out"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
