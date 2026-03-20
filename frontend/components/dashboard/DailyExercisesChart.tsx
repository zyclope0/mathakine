"use client";

import { useId, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
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

export interface DailyExercisesChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
  }>;
}

interface DailyExercisesChartBodyProps {
  data: DailyExercisesChartData;
  /** Human-readable period for aria-label (already translated). */
  accessibilityPeriodSummary: string;
}

/** Chart region only (no Card) — for embedding with an external header / period selector. */
export function DailyExercisesChartBody({
  data,
  accessibilityPeriodSummary,
}: DailyExercisesChartBodyProps) {
  const t = useTranslations("dashboard.charts.dailyExercises");
  const { shouldReduceMotion } = useAccessibleAnimation();
  const descriptionId = useId();

  const chartData = useMemo(() => {
    return data.labels.map((label, index) => ({
      name: label,
      [data.datasets[0]?.label || "Exercices par jour"]: data.datasets[0]?.data[index] || 0,
    }));
  }, [data.labels, data.datasets]);

  const barColor = "var(--color-chart-2)";
  const borderColor = "var(--color-chart-2)";

  const chartDescription = useMemo(() => {
    return data.labels
      .map(
        (label, index) =>
          `${label}: ${data.datasets[0]?.data[index] || 0} ${data.datasets[0]?.label || "exercices"}`
      )
      .join(", ");
  }, [data.labels, data.datasets]);

  const ariaLabel = `${t("titleShort")} — ${accessibilityPeriodSummary}`;

  return (
    <div
      className="h-[300px] w-full"
      role="img"
      aria-label={ariaLabel}
      aria-describedby={descriptionId}
    >
      <div id={descriptionId} className="sr-only">
        {chartDescription}
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" strokeOpacity={0.4} />
          <XAxis
            dataKey="name"
            stroke="var(--color-muted-foreground)"
            style={{ fontSize: "11px" }}
            angle={-35}
            textAnchor="end"
            height={56}
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
            labelFormatter={(label) => (typeof label === "string" ? formatShortDate(label) : label)}
            formatter={(value) => [typeof value === "number" ? Math.round(value) : value, ""]}
          />
          <Legend wrapperStyle={{ color: "var(--color-muted-foreground)" }} />
          <Bar
            dataKey={data.datasets[0]?.label || "Exercices par jour"}
            fill={barColor}
            stroke={borderColor}
            strokeWidth={1}
            strokeOpacity={0.6}
            radius={[4, 4, 0, 0]}
            isAnimationActive={!shouldReduceMotion}
            animationDuration={600}
            animationEasing="ease-out"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

interface DailyExercisesChartProps {
  data: DailyExercisesChartData;
}

/** Card + default title (legacy standalone chart). */
export function DailyExercisesChart({ data }: DailyExercisesChartProps) {
  const t = useTranslations("dashboard.charts.dailyExercises");
  const defaultPeriod = t("defaultPeriodAria", {
    default: "période sélectionnée dans les statistiques",
  });

  return (
    <Card className="border-border/50 bg-card/40 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t("title", { default: "Exercices par jour (30 derniers jours)" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <DailyExercisesChartBody data={data} accessibilityPeriodSummary={defaultPeriod} />
      </CardContent>
    </Card>
  );
}
