"use client";

import { useMemo } from "react";
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

interface DailyExercisesChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
    }>;
  };
}

export function DailyExercisesChart({ data }: DailyExercisesChartProps) {
  const t = useTranslations("dashboard.charts.dailyExercises");

  // Memoization de la transformation des données pour éviter les recalculs
  const chartData = useMemo(() => {
    return data.labels.map((label, index) => ({
      name: label,
      [data.datasets[0]?.label || "Exercices par jour"]: data.datasets[0]?.data[index] || 0,
    }));
  }, [data.labels, data.datasets]);

  // Memoization des couleurs pour éviter les recalculs
  const barColor = useMemo(
    () => data.datasets[0]?.backgroundColor || "rgba(255, 206, 86, 0.8)",
    [data.datasets]
  );

  const borderColor = useMemo(
    () => data.datasets[0]?.borderColor || "rgba(255, 206, 86, 1)",
    [data.datasets]
  );

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
          {t("title", { default: "Exercices par jour (30 derniers jours)" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className="h-[300px] w-full"
          role="img"
          aria-label={t("ariaLabel", {
            default:
              "Graphique en barres montrant le nombre d'exercices résolus chaque jour sur les 30 derniers jours",
          })}
          aria-describedby="daily-exercises-chart-description"
        >
          <div id="daily-exercises-chart-description" className="sr-only">
            {chartDescription}
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis
                dataKey="name"
                stroke="#a0a0a0"
                style={{ fontSize: "11px" }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis stroke="#a0a0a0" style={{ fontSize: "12px" }} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(18, 18, 26, 0.95)",
                  border: "1px solid rgba(124, 58, 237, 0.3)",
                  borderRadius: "8px",
                  color: "#ffffff",
                }}
              />
              <Legend />
              <Bar
                dataKey={data.datasets[0]?.label || "Exercices par jour"}
                fill={barColor}
                stroke={borderColor}
                strokeWidth={1}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
