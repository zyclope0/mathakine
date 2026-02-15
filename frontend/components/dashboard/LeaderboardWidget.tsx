"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Trophy, ChevronRight, User } from "lucide-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { cn } from "@/lib/utils/cn";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useLeaderboard, type LeaderboardEntry } from "@/hooks/useLeaderboard";

const RANK_ICONS: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

export function LeaderboardWidget() {
  const t = useTranslations("dashboard.leaderboardWidget");
  const { leaderboard, isLoading } = useLeaderboard(5);
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  if (isLoading) {
    return (
      <Card className="bg-card border-primary/20 animate-pulse h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="h-6 w-36 bg-muted rounded" />
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-8 w-full bg-muted rounded" />
            ))}
          </div>
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
      whileHover={!shouldReduceMotion ? { scale: 1.01 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="bg-card border-primary/20 h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <Trophy className="w-5 h-5 text-yellow-400" />
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

        <CardContent className="flex-grow pt-0">
          {leaderboard.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t("empty")}</p>
          ) : (
            <ul className="space-y-1.5" role="list">
              {leaderboard.map((entry: LeaderboardEntry) => (
                <li
                  key={`${entry.rank}-${entry.username}`}
                  className={cn(
                    "flex items-center gap-2 rounded px-2 py-1.5 text-sm",
                    entry.is_current_user && "bg-primary/10 ring-1 ring-primary/20"
                  )}
                >
                  <span className="w-6 text-base">
                    {RANK_ICONS[entry.rank] ?? `#${entry.rank}`}
                  </span>
                  <User className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                  <span className="flex-1 truncate font-medium">{entry.username}</span>
                  <span className="text-muted-foreground font-semibold text-primary">
                    {entry.total_points}
                  </span>
                  {entry.is_current_user && (
                    <span className="text-xs bg-primary/20 px-1.5 py-0.5 rounded">
                      {t("you")}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
