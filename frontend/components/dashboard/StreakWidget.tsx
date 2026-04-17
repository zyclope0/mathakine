"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { Badge } from "@/components/ui/badge";
import { DocTip } from "@/components/ui/DocTip";
import { Flame, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

interface StreakWidgetProps {
  currentStreak: number;
  highestStreak: number;
  isLoading?: boolean;
}

export function StreakWidget({ currentStreak, highestStreak, isLoading }: StreakWidgetProps) {
  const t = useTranslations("dashboard.streak");
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  const isNewRecord = currentStreak === highestStreak && currentStreak > 0;

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-32">
        <div className="space-y-2">
          <Skeleton className="h-12 w-20" />
          <Skeleton className="h-4 w-40" />
        </div>
      </DashboardWidgetSkeleton>
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
      className="rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
    >
      <Card className="dashboard-card-surface--calm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2 text-foreground">
              <motion.div
                animate={
                  !shouldReduceMotion && currentStreak > 0
                    ? { rotate: [0, -10, 10, -10, 0], scale: [1, 1.1, 1] }
                    : {}
                }
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Flame
                  className={cn(
                    "w-5 h-5",
                    currentStreak > 0 ? "text-warning" : "text-muted-foreground"
                  )}
                />
              </motion.div>
              <span className="flex min-w-0 items-center gap-1.5">
                {t("title")}
                <DocTip label={t("docTip")} side="top" />
              </span>
            </CardTitle>
            {isNewRecord && (
              <Badge className="bg-warning/20 text-warning border-warning/30 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {t("record")}
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="pt-1 pb-4 space-y-1">
          {/* Chiffre principal — taille réduite, hiérarchie relative au contenu */}
          <div className="flex items-baseline gap-2">
            <span
              className={cn(
                "text-5xl font-bold tabular-nums leading-none",
                currentStreak > 0 ? "text-warning" : "text-muted-foreground"
              )}
            >
              {currentStreak}
            </span>
            <span className="text-sm text-muted-foreground">
              {t("days", { count: currentStreak })}
            </span>
          </div>

          {/* Meilleure série — contexte immédiat, sans séparateur */}
          <p className="text-sm text-muted-foreground">
            {t("best")}:{" "}
            <span className="font-semibold text-foreground">
              {highestStreak} {t("days", { count: highestStreak })}
            </span>
          </p>

          {/* Message motivationnel — inline, pas de border-t */}
          {currentStreak > 0 && (
            <p className="text-sm text-muted-foreground leading-snug pt-1">{t("keepGoing")}</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
