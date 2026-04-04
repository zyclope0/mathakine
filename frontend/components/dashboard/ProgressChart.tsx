"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { formatShortDate } from "@/lib/utils/format";
import { RECHARTS_TOOLTIP_STYLE } from "@/lib/utils/chart";

interface ProgressChartRow {
  name: string;
  value: number;
}

const PROGRESS_VALUE_KEY: keyof ProgressChartRow = "value";
const DEFAULT_PROGRESS_SERIES_LABEL = "Exercices resolus";

interface ProgressChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
    }>;
  };
}

export function ProgressChart({ data }: ProgressChartProps) {
  const t = useTranslations("dashboard.charts.progressByType");
  const { shouldReduceMotion } = useAccessibleAnimation({ respectFocusMode: false });
  const seriesLabel = data.datasets[0]?.label || DEFAULT_PROGRESS_SERIES_LABEL;

  // Memoization de la transformation des donnees pour eviter les recalculs
  const chartData = useMemo<ProgressChartRow[]>(() => {
    return data.labels.map((label, index) => ({
      name: label,
      value: data.datasets[0]?.data[index] || 0,
    }));
  }, [data.labels, data.datasets]);

  // Memoization de la description textuelle pour l'accessibilite
  const chartDescription = useMemo(() => {
    return data.labels
      .map((label, index) => `${label}: ${data.datasets[0]?.data[index] || 0} ${seriesLabel}`)
      .join(", ");
  }, [data.labels, data.datasets, seriesLabel]);

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t("title", { default: "Progression par type d'exercice" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div id="progress-chart-description" className="sr-only">
          {chartDescription}
        </div>
        <div
          className="h-[300px] w-full"
          role="img"
          aria-label={t("ariaLabel", {
            default: "Graphique de progression montrant le nombre d'exercices resolus par type",
          })}
          aria-describedby="progress-chart-description"
        >
          {/* aria-hidden : l'accessibilite est portee par le div[role="img"] parent */}
          <div aria-hidden="true" className="h-full w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="progressGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-chart-1)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--color-chart-1)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--color-border)"
                  strokeOpacity={0.4}
                />
                <XAxis
                  dataKey="name"
                  stroke="var(--color-muted-foreground)"
                  style={{ fontSize: "11px" }}
                  tickFormatter={formatShortDate}
                  minTickGap={28}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke="var(--color-muted-foreground)"
                  style={{ fontSize: "12px" }}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={RECHARTS_TOOLTIP_STYLE}
                  formatter={(value) => [
                    typeof value === "number" ? Math.round(value) : value,
                    seriesLabel,
                  ]}
                />
                <Legend wrapperStyle={{ color: "var(--color-muted-foreground)" }} />
                <Area
                  type="monotone"
                  dataKey={PROGRESS_VALUE_KEY}
                  name={seriesLabel}
                  stroke="var(--color-chart-1)"
                  strokeWidth={2}
                  fill="url(#progressGradient)"
                  dot={{ fill: "var(--color-chart-1)", r: 4 }}
                  activeDot={{ r: 6, fill: "var(--color-chart-1)" }}
                  isAnimationActive={!shouldReduceMotion}
                  animationDuration={800}
                  animationEasing="ease-out"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
