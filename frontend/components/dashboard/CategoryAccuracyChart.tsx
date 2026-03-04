"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Activity } from "lucide-react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { RECHARTS_TOOLTIP_STYLE } from "@/lib/utils/chart";

interface CategoryData {
  completed: number;
  accuracy: number;
}

interface CategoryAccuracyChartProps {
  categoryData: Record<string, CategoryData>;
  isLoading?: boolean;
}

export function CategoryAccuracyChart({ categoryData, isLoading }: CategoryAccuracyChartProps) {
  const t = useTranslations("dashboard.categoryAccuracy");
  const tExercises = useTranslations("exercises");
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  const radarData = useMemo(
    () =>
      Object.entries(categoryData).map(([category, data]) => {
        const categoryKey = category.toLowerCase().replace("exercises.types.", "");
        return {
          category: tExercises(`types.${categoryKey}`, { defaultValue: categoryKey }),
          accuracy: Math.round(data.accuracy * 100),
          completed: data.completed,
        };
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [categoryData]
  );

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-48">
        <div className="h-[260px] flex items-center justify-center">
          <Skeleton className="h-48 w-48 rounded-full" />
        </div>
      </DashboardWidgetSkeleton>
    );
  }

  const categories = Object.entries(categoryData);

  if (categories.length === 0) {
    return (
      <Card className="border-white/10 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <Activity className="w-5 h-5 text-primary-on-dark" />
            {t("title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow flex items-center justify-center">
          <div className="text-sm text-muted-foreground text-center">{t("noData")}</div>
        </CardContent>
      </Card>
    );
  }

  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="border-white/10 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <Activity className="w-5 h-5 text-primary-on-dark" />
            {t("title")}
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-grow">
          <div className="h-[260px] w-full" role="img" aria-label={t("title")}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                <PolarGrid stroke="var(--color-border)" strokeOpacity={0.5} />
                <PolarAngleAxis
                  dataKey="category"
                  tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
                />
                <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  dataKey="accuracy"
                  stroke="var(--color-chart-1)"
                  strokeOpacity={0.8}
                  fill="var(--color-chart-1)"
                  fillOpacity={0.3}
                  strokeWidth={2}
                  isAnimationActive={!shouldReduceMotion}
                  animationDuration={800}
                  animationEasing="ease-out"
                />
                <Tooltip
                  contentStyle={RECHARTS_TOOLTIP_STYLE}
                  formatter={(value) => [
                    `${typeof value === "number" ? Math.round(value) : value}%`,
                    t("title"),
                  ]}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
