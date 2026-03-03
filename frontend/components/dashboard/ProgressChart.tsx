"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
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
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Memoization de la transformation des données pour éviter les recalculs
  const chartData = useMemo(() => {
    return data.labels.map((label, index) => ({
      name: label,
      [data.datasets[0]?.label || "Exercices résolus"]: data.datasets[0]?.data[index] || 0,
    }));
  }, [data.labels, data.datasets]);

  // Memoization de la description textuelle pour l'accessibilité
  const chartDescription = useMemo(() => {
    return data.labels
      .map(
        (label, index) =>
          `${label}: ${data.datasets[0]?.data[index] || 0} ${data.datasets[0]?.label || "exercices"}`
      )
      .join(", ");
  }, [data.labels, data.datasets]);

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t("title", { default: "Progression par type d'exercice" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className="h-[300px] w-full"
          role="img"
          aria-label={t("ariaLabel", {
            default: "Graphique de progression montrant le nombre d'exercices résolus par type",
          })}
          aria-describedby="progress-chart-description"
        >
          <div id="progress-chart-description" className="sr-only">
            {chartDescription}
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                strokeOpacity={0.5}
              />
              <XAxis
                dataKey="name"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
              />
              <YAxis
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
                allowDecimals={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-popover)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "8px",
                  color: "var(--color-popover-foreground)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={data.datasets[0]?.label || "Exercices résolus"}
                stroke="var(--color-chart-1)"
                strokeWidth={2}
                fill="var(--color-chart-1)"
                fillOpacity={0.15}
                dot={{ fill: "var(--color-chart-1)", r: 4 }}
                activeDot={{ r: 6, fill: "var(--color-chart-1)" }}
                isAnimationActive={!shouldReduceMotion}
                animationDuration={800}
                animationEasing="ease-out"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
