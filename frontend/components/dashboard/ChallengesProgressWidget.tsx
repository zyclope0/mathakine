"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { Progress } from "@/components/ui/progress";
import { Trophy, Target, Clock } from "lucide-react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { DashboardDataScopeBadge } from "@/components/dashboard/DashboardDataScopeBadge";
import { useChallengesDetailedProgress } from "@/hooks/useChallengesProgress";
import { getChallengeTypeDisplay } from "@/lib/constants/challenges";

interface ChallengesProgressWidgetProps {
  completedChallenges: number;
  totalChallenges: number;
  successRate: number;
  averageTime: number;
  isLoading?: boolean;
}

export function ChallengesProgressWidget({
  completedChallenges,
  totalChallenges,
  successRate,
  averageTime,
  isLoading,
}: ChallengesProgressWidgetProps) {
  const t = useTranslations("dashboard.challengesProgress");
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();
  const {
    data: detailed,
    isLoading: detailedLoading,
    isError: detailedError,
  } = useChallengesDetailedProgress();

  const sortedItems = useMemo(() => {
    const items = detailed?.items ?? [];
    return [...items].sort((a, b) => a.challenge_type.localeCompare(b.challenge_type));
  }, [detailed?.items]);

  const typeLabel = (raw: string) => {
    const key = raw.toLowerCase().replace(/[^a-z0-9_]/g, "_");
    return t(`types.${key}`, { defaultValue: getChallengeTypeDisplay(raw) });
  };

  const masteryLabel = (raw: string) => {
    const key = raw.toLowerCase().replace(/[^a-z0-9_]/g, "_");
    return t(`mastery.${key}`, { defaultValue: raw });
  };

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-48">
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </DashboardWidgetSkeleton>
    );
  }

  const completionPercentage =
    totalChallenges > 0 ? Math.round((completedChallenges / totalChallenges) * 100) : 0;

  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  const showByType = !detailedError && sortedItems.length > 0;

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="border-border/50 bg-card/40 backdrop-blur-md h-full flex flex-col">
        <CardHeader className="pb-3 flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex flex-wrap items-center justify-between gap-2 text-foreground">
            <span className="flex items-center gap-2 min-w-0">
              <motion.div
                animate={!shouldReduceMotion ? { rotate: [0, -10, 10, -10, 0] } : {}}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Trophy className="w-5 h-5 shrink-0 text-warning" />
              </motion.div>
              <span className="min-w-0">{t("title")}</span>
            </span>
            <DashboardDataScopeBadge />
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-grow">
          {/* Barre de progression */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-muted-foreground">
                {completedChallenges} / {totalChallenges} {t("completed")}
              </span>
              <span className="font-semibold text-foreground">{completionPercentage}%</span>
            </div>
            <Progress value={completionPercentage} className="h-3" />
          </div>

          {/* Statistiques */}
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg p-3 bg-green-500/5 border border-green-500/15">
              <div className="flex items-center gap-2 mb-1">
                <Target className="w-4 h-4 text-green-400" />
                <div className="text-xs text-muted-foreground">{t("successRate")}</div>
              </div>
              <div className="text-lg font-bold text-success">{Math.round(successRate * 100)}%</div>
            </div>

            <div className="rounded-lg p-3 bg-primary/10 border border-primary/20">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-primary" />
                <div className="text-xs text-muted-foreground">{t("avgTime")}</div>
              </div>
              <div className="text-lg font-bold text-primary">
                {averageTime > 0 ? `${Math.round(averageTime)}s` : "-"}
              </div>
            </div>
          </div>

          {detailedLoading && !showByType ? (
            <div className="mt-4 pt-4 border-t border-border space-y-2" aria-busy="true">
              <Skeleton className="h-3 w-32" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : null}

          {showByType ? (
            <div className="mt-4 pt-4 border-t border-border space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {t("byTypeTitle")}
              </h3>
              <ul className="space-y-2" role="list">
                {sortedItems.map((row) => (
                  <li
                    key={row.challenge_type}
                    className="grid grid-cols-[1fr_auto] gap-2 rounded-lg px-3 py-2.5 bg-primary/5 border border-primary/10"
                  >
                    <span className="text-sm font-medium text-foreground min-w-0">
                      {typeLabel(row.challenge_type)}
                    </span>
                    <div className="text-right">
                      <div className="text-sm font-bold text-primary tabular-nums">
                        <span className="text-xs font-semibold text-muted-foreground">
                          {masteryLabel(row.mastery_level)}
                        </span>
                        <span className="text-muted-foreground/80 mx-1" aria-hidden="true">
                          ·
                        </span>
                        <span>{Math.round(row.completion_rate)}%</span>
                      </div>
                      <div className="text-xs text-muted-foreground tabular-nums">
                        {t("byTypeAttempts", {
                          correct: row.correct_attempts,
                          total: row.total_attempts,
                        })}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {completedChallenges === 0 && !detailedLoading && !showByType ? (
            <div className="mt-4 pt-4 border-t border-border text-sm text-muted-foreground">
              {t("noChallengesYet")}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}
