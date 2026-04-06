"use client";

import { Button } from "@/components/ui/button";
import { Badge as UIBadge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Award, TrendingUp, Calendar } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { EmptyState } from "@/components/layout";
import type { UserBadge } from "@/types/api";
import { useRouter } from "next/navigation";

// Contrat local aligné avec RecentActivity (ActivityItem non exporté)
interface ActivityItem {
  type: string;
  description: string;
  time: string;
  is_correct?: boolean;
}

interface StatsLike {
  total_exercises?: number | null;
  success_rate?: number | null;
  recent_activity?: ActivityItem[];
}

interface GamificationLevel {
  current: number;
  title?: string;
  current_xp: number;
  next_level_xp: number;
  progression_rank?: string;
  jedi_rank?: string;
}

interface ProfileStatisticsSectionProps {
  stats: StatsLike | null | undefined;
  isLoadingStats: boolean;
  statsError: unknown;
  gamificationLevel?: GamificationLevel | null | undefined;
  recentBadges: (UserBadge & { earned_at: string })[];
  formatDate: (d: string | null | undefined) => string;
}

/**
 * Section statistiques, activité récente, badges récents.
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfileStatisticsSection({
  stats,
  isLoadingStats,
  statsError,
  gamificationLevel,
  recentBadges,
  formatDate,
}: ProfileStatisticsSectionProps) {
  const t = useTranslations("profile");
  const tStatistics = useTranslations("profile.statistics");
  const tBadges = useTranslations("profile.badges");
  const tDashboard = useTranslations("dashboard");
  const router = useRouter();

  return (
    <div className="space-y-8">
      {/* Erreur */}
      {statsError ? (
        <div className="animate-fade-in-up">
          <EmptyState title={t("error.title")} description={t("error.description")} />
        </div>
      ) : isLoadingStats ? (
        /* Skeleton */
        <div className="animate-fade-in-up">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="animate-pulse bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl h-[200px]">
              <CardHeader>
                <div className="h-6 w-32 bg-muted rounded" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 w-full bg-muted rounded" />
                  <div className="h-4 w-3/4 bg-muted rounded" />
                </div>
              </CardContent>
            </Card>
            <Card className="animate-pulse bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl h-[200px]">
              <CardHeader>
                <div className="h-6 w-40 bg-muted rounded" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 w-full bg-muted rounded" />
                  <div className="h-4 w-2/3 bg-muted rounded" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : stats ? (
        /* Contenu */
        <div className="animate-fade-in-up space-y-8">
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground">
              {tDashboard("profile.statsPeriodHint", {
                period: tDashboard("timeRange.30days"),
              })}
            </p>
            <div className="grid gap-6 md:grid-cols-2">
              {gamificationLevel ? (
                <LevelIndicator level={gamificationLevel} />
              ) : (
                <Card className="border-dashed bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl">
                  <CardContent className="p-6 sm:p-8">
                    <p className="text-sm font-semibold text-foreground">
                      {tDashboard("profile.levelUnavailableTitle")}
                    </p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {tDashboard("profile.levelUnavailableDescription")}
                    </p>
                  </CardContent>
                </Card>
              )}
              <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8 flex flex-col justify-center">
                <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    {tStatistics("overallPerformance")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="flex flex-col">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                      <div className="flex flex-col gap-1 pr-4">
                        <p className="text-sm font-medium text-foreground">
                          {tStatistics("totalAttempts")}
                        </p>
                      </div>
                      <p className="text-base font-semibold text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                        {stats.total_exercises ?? 0}
                      </p>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                      <div className="flex flex-col gap-1 pr-4">
                        <p className="text-sm font-medium text-foreground">
                          {tStatistics("successRate")}
                        </p>
                      </div>
                      <p className="text-base font-semibold text-primary sm:text-right mt-3 sm:mt-0 shrink-0">
                        {Math.round((stats.success_rate ?? 0) * 10) / 10}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Activité récente */}
          {stats.recent_activity && stats.recent_activity.length > 0 && (
            <div className="animate-fade-in-up-delay-1">
              <RecentActivity activities={stats.recent_activity} />
            </div>
          )}
        </div>
      ) : null}

      {/* Badges récents */}
      {recentBadges.length > 0 && (
        <div className="animate-fade-in-up-delay-2">
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2 px-1">
            <Award className="h-5 w-5 text-primary" aria-hidden="true" />
            {tBadges("title")}
          </h3>
          <div className="grid gap-6 md:grid-cols-3">
            {recentBadges.map((badge: UserBadge & { earned_at: string }, index: number) => (
              <Card
                key={badge.id}
                className={cn(
                  "bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6",
                  "relative overflow-hidden transition-all duration-300",
                  "hover:shadow-md hover:border-primary/20 hover:scale-[1.02]",
                  `animate-fade-in-up-delay-${Math.min(index + 1, 3)}`
                )}
              >
                <CardHeader className="p-0 mb-4 space-y-0">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2 rounded-full bg-primary/10 text-primary">
                      <Award className="h-6 w-6" />
                    </div>
                    <UIBadge variant="secondary" className="font-semibold bg-secondary/50">
                      {badge.points} pts
                    </UIBadge>
                  </div>
                  <CardTitle className="text-lg font-bold">{badge.name}</CardTitle>
                  <CardDescription className="mt-1 text-sm text-muted-foreground leading-relaxed">
                    {badge.description}
                  </CardDescription>
                </CardHeader>
                {badge.earned_at && (
                  <CardContent className="p-0 mt-auto">
                    <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground pt-4 border-t border-border/50">
                      <Calendar className="h-3.5 w-3.5" />
                      {formatDate(badge.earned_at)}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
          <div className="mt-8 text-center">
            <Button
              variant="outline"
              onClick={() => router.push("/badges")}
              aria-label={tBadges("viewAll")}
              className="transition-all duration-300 hover:scale-105 rounded-full px-6"
            >
              {tBadges("viewAll")}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
