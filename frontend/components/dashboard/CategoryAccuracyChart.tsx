"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity } from "lucide-react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { DashboardDataScopeBadge } from "@/components/dashboard/DashboardDataScopeBadge";
import {
  DashboardCategoryRadarPlot,
  DashboardRadarSubsectionSkeleton,
  type DashboardRadarCategoryRow,
} from "@/components/dashboard/DashboardCategoryRadarChart";
import { useChallengesDetailedProgress } from "@/hooks/useChallengesProgress";
import { getChallengeTypeDisplay } from "@/lib/constants/challenges";

interface CategoryData {
  completed: number;
  accuracy: number;
}

interface CategoryAccuracyChartProps {
  categoryData: Record<string, CategoryData>;
  isLoading?: boolean;
}

/**
 * Widget unique « Précision par catégorie » : radar exercices + radar défis logiques (même carte).
 */
export function CategoryAccuracyChart({ categoryData, isLoading }: CategoryAccuracyChartProps) {
  const t = useTranslations("dashboard.categoryAccuracy");
  const tExercises = useTranslations("exercises");
  const tChTypes = useTranslations("dashboard.challengesProgress");
  const { createVariants, createTransition } = useAccessibleAnimation();
  const {
    data: detailed,
    isLoading: isLoadingChallenges,
    isError: challengesError,
  } = useChallengesDetailedProgress();

  const exerciseRows: DashboardRadarCategoryRow[] = useMemo(
    () =>
      Object.entries(categoryData).map(([category, data]) => {
        const categoryKey = category.toLowerCase().replace("exercises.types.", "");
        return {
          category: tExercises(`types.${categoryKey}`, { defaultValue: categoryKey }),
          accuracy: Math.round(data.accuracy * 100),
          completed: data.completed,
        };
      }),
    [categoryData, tExercises]
  );

  const items = detailed?.items;
  const challengeRows: DashboardRadarCategoryRow[] = useMemo(() => {
    if (!items?.length) return [];
    return [...items]
      .filter((row) => row.total_attempts > 0)
      .sort((a, b) => a.challenge_type.localeCompare(b.challenge_type))
      .map((row) => {
        const key = row.challenge_type.toLowerCase().replace(/[^a-z0-9_]/g, "_");
        const label = tChTypes(`types.${key}`, {
          defaultValue: getChallengeTypeDisplay(row.challenge_type),
        });
        return {
          category: label,
          accuracy: Math.round(row.completion_rate),
          completed: row.correct_attempts,
          attempts: row.total_attempts,
        };
      });
  }, [items, tChTypes]);

  const effectiveChallengeRows = challengesError ? [] : challengeRows;

  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  const exercisesLoading = isLoading === true;
  const challengesLoading = isLoadingChallenges === true;

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg h-full"
    >
      <Card className="dashboard-card-surface-interactive h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex flex-wrap items-center justify-between gap-2 text-foreground">
            <span className="flex items-center gap-2 min-w-0">
              <Activity className="w-5 h-5 shrink-0 text-primary" />
              <span className="min-w-0">{t("title")}</span>
            </span>
            <DashboardDataScopeBadge />
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-grow space-y-6">
          {/* Exercices */}
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
              {t("exercisesSubtitle")}
            </p>
            {exercisesLoading ? (
              <DashboardRadarSubsectionSkeleton />
            ) : exerciseRows.length === 0 ? (
              <div className="h-[220px] flex items-center justify-center text-sm text-muted-foreground text-center px-2">
                {t("noData")}
              </div>
            ) : (
              <DashboardCategoryRadarPlot
                rows={exerciseRows}
                tooltipSeriesLabel={t("exercisesSubtitle")}
                ariaLabel={t("exercisesSubtitle")}
              />
            )}
          </div>

          <div className="border-t border-border pt-4">
            <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">
              {t("challengesSubtitle")}
            </p>
            {challengesLoading ? (
              <DashboardRadarSubsectionSkeleton />
            ) : effectiveChallengeRows.length === 0 ? (
              <div className="h-[220px] flex items-center justify-center text-sm text-muted-foreground text-center px-2">
                {t("noChallengesRadar")}
              </div>
            ) : (
              <DashboardCategoryRadarPlot
                rows={effectiveChallengeRows}
                tooltipSeriesLabel={t("challengesSubtitle")}
                ariaLabel={t("challengesSubtitle")}
              />
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
