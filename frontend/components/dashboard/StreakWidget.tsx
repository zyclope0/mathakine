"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Flame, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils/cn";
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
      <Card className="bg-card border-primary/20 animate-pulse h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="h-6 w-32 bg-muted rounded"></div>
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="h-12 w-20 bg-muted rounded mb-2"></div>
          <div className="h-4 w-40 bg-muted rounded"></div>
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
      <Card
        className={cn(
          "bg-card border-2 h-full flex flex-col",
          currentStreak > 0 ? "border-orange-500/40 bg-orange-500/5" : "border-primary/20"
        )}
      >
        <CardHeader className="pb-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <motion.div
                animate={
                  !shouldReduceMotion && currentStreak > 0
                    ? {
                        rotate: [0, -10, 10, -10, 0],
                        scale: [1, 1.1, 1],
                      }
                    : {}
                }
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Flame
                  className={cn(
                    "w-5 h-5",
                    currentStreak > 0 ? "text-orange-400" : "text-muted-foreground"
                  )}
                />
              </motion.div>
              {t("title")}
            </CardTitle>
            {isNewRecord && (
              <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {t("record")}
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="flex-grow">
          <div className="flex items-baseline gap-3 mb-3">
            <div
              className={cn(
                "text-5xl font-bold",
                currentStreak > 0 ? "text-orange-400" : "text-muted-foreground"
              )}
            >
              {currentStreak}
            </div>
            <div className="text-sm text-muted-foreground">
              {t("days", { count: currentStreak })}
            </div>
          </div>

          <div className="text-sm text-muted-foreground flex items-center gap-2">
            <span>{t("best")}:</span>
            <span className="font-semibold text-foreground">
              {highestStreak} {t("days", { count: highestStreak })}
            </span>
          </div>

          {currentStreak > 0 && (
            <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
              {t("keepGoing")}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
