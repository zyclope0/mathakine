"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardWidgetSkeleton } from "@/components/dashboard/DashboardSkeletons";
import { Trophy, ChevronRight } from "lucide-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useLeaderboard, type LeaderboardEntry } from "@/hooks/useLeaderboard";
import { RANK_MEDALS } from "@/lib/constants/leaderboard";
import { UserAvatar } from "@/components/ui/UserAvatar";

export function LeaderboardWidget() {
  const t = useTranslations("dashboard.leaderboardWidget");
  const { leaderboard, isLoading } = useLeaderboard(5);
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  if (isLoading) {
    return (
      <DashboardWidgetSkeleton titleWidth="w-36">
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
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
      whileHover={!shouldReduceMotion ? { scale: 1.01 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="dashboard-card-surface h-full flex flex-col overflow-hidden">
        <CardHeader className="pb-2 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <Trophy className="w-5 h-5 text-warning" />
              {t("title")}
            </CardTitle>
            <Link
              href="/leaderboard"
              className="text-xs font-medium text-primary hover:underline flex items-center gap-1"
              aria-label={t("viewAll")}
            >
              {t("viewAll")}
              <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </CardHeader>

        <CardContent className="flex-grow pt-0 px-0 pb-0">
          {leaderboard.length === 0 ? (
            <p className="text-sm text-muted-foreground px-4 pb-4">{t("empty")}</p>
          ) : (
            <ul role="list">
              {leaderboard.map((entry: LeaderboardEntry, idx: number) => (
                <li
                  key={`${entry.rank}-${entry.username}`}
                  className={cn(
                    "flex items-center gap-2.5 px-4 py-2",
                    "transition-colors duration-150 hover:bg-muted/35",
                    idx < leaderboard.length - 1 && "border-b border-border/50",
                    entry.is_current_user
                      ? "bg-primary/5 border-l-[3px] border-l-primary"
                      : "border-l-[3px] border-l-transparent"
                  )}
                >
                  <span className="flex-shrink-0 w-6 text-center text-base leading-none">
                    {RANK_MEDALS[entry.rank] ?? (
                      <span className="text-xs font-mono text-muted-foreground">{entry.rank}</span>
                    )}
                  </span>

                  <UserAvatar username={entry.username} size="sm" />

                  <span
                    className={cn(
                      "flex-1 min-w-0 truncate text-sm font-medium",
                      entry.is_current_user ? "text-foreground" : "text-foreground/90"
                    )}
                  >
                    {entry.username}
                  </span>

                  {entry.is_current_user && (
                    <span className="flex-shrink-0 text-xs bg-primary text-primary-foreground font-bold px-1.5 py-0.5 rounded-full">
                      {t("you")}
                    </span>
                  )}

                  <span className="flex-shrink-0 text-sm font-bold text-warning tabular-nums">
                    {entry.total_points.toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
