"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Trophy, Target, Clock } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils/cn";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

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

  if (isLoading) {
    return (
      <Card className="bg-card border-primary/20 animate-pulse h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="h-6 w-48 bg-muted rounded"></div>
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="space-y-3">
            <div className="h-4 w-full bg-muted rounded"></div>
            <div className="h-4 w-3/4 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const completionPercentage =
    totalChallenges > 0 ? Math.round((completedChallenges / totalChallenges) * 100) : 0;

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
      <Card className="bg-card border-primary/20 h-full flex flex-col">
        <CardHeader className="pb-3 flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <motion.div
              animate={!shouldReduceMotion ? { rotate: [0, -10, 10, -10, 0] } : {}}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Trophy className="w-5 h-5 text-yellow-400" />
            </motion.div>
            {t("title")}
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
            <div className="rounded-lg p-3 bg-green-500/10 border border-green-500/20">
              <div className="flex items-center gap-2 mb-1">
                <Target className="w-4 h-4 text-green-400" />
                <div className="text-xs text-muted-foreground">{t("successRate")}</div>
              </div>
              <div className="text-lg font-bold text-green-400">
                {Math.round(successRate * 100)}%
              </div>
            </div>

            <div className="rounded-lg p-3 bg-blue-500/10 border border-blue-500/20">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-blue-400" />
                <div className="text-xs text-muted-foreground">{t("avgTime")}</div>
              </div>
              <div className="text-lg font-bold text-blue-400">
                {averageTime > 0 ? `${Math.round(averageTime)}s` : "-"}
              </div>
            </div>
          </div>

          {completedChallenges === 0 && (
            <div className="mt-4 pt-4 border-t border-border text-sm text-muted-foreground">
              {t("noChallengesYet")}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
