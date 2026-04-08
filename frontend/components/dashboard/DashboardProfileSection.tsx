"use client";

import { Trophy, Zap, CheckCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { AverageTimeWidget } from "@/components/dashboard/AverageTimeWidget";
import { DashboardLastUpdate } from "@/components/dashboard/DashboardLastUpdate";
import { LevelEstablishedWidget } from "@/components/dashboard/LevelEstablishedWidget";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { Card, CardContent } from "@/components/ui/card";
import { PageSection } from "@/components/layout";
import type { ChallengesProgress } from "@/hooks/useChallengesProgress";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { UserStats } from "@/hooks/useUserStats";
import type { User } from "@/types/api";

interface DashboardProfileSectionProps {
  challengesProgress: ChallengesProgress | null;
  isLoadingProgress: boolean;
  locale: string;
  progressStats: ProgressStats | null;
  stats: UserStats;
  timeRangeLabel: string;
  user: User | null;
}

export function DashboardProfileSection({
  challengesProgress,
  isLoadingProgress,
  locale,
  progressStats,
  stats,
  timeRangeLabel,
  user,
}: DashboardProfileSectionProps) {
  const t = useTranslations("dashboard");

  return (
    <>
      <PageSection>
        {user?.gamification_level ? (
          <LevelIndicator level={user.gamification_level} />
        ) : (
          <Card className="dashboard-card-surface border-dashed">
            <CardContent className="p-6 sm:p-8">
              <p className="text-sm font-semibold text-foreground">
                {t("profile.levelUnavailableTitle")}
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                {t("profile.levelUnavailableDescription")}
              </p>
            </CardContent>
          </Card>
        )}
      </PageSection>
      <PageSection>
        <LevelEstablishedWidget />
      </PageSection>
      <PageSection className="space-y-2">
        <p className="text-xs text-muted-foreground">
          {t("profile.statsPeriodHint", { period: timeRangeLabel })}
        </p>
        {stats.recent_activity?.[0]?.time && (
          <div className="flex justify-end">
            <DashboardLastUpdate time={stats.recent_activity[0].time} locale={locale} />
          </div>
        )}
        <div className="grid gap-4 md:grid-cols-3">
          <StatsCard
            icon={CheckCircle}
            value={stats.total_exercises || 0}
            label={t("stats.exercisesSolved")}
          />
          <StatsCard
            icon={Zap}
            value={`${Math.round(stats.success_rate || 0)}%`}
            label={t("stats.successRate")}
          />
          <StatsCard
            icon={Trophy}
            value={stats.total_challenges || 0}
            label={t("stats.challengesCompleted")}
            {...(challengesProgress && challengesProgress.average_time > 0
              ? {
                  footnote: t("stats.challengesAvgFootnote", {
                    seconds: Math.round(challengesProgress.average_time),
                  }),
                }
              : {})}
          />
        </div>
      </PageSection>
      <PageSection>
        <AverageTimeWidget
          averageTimeSeconds={progressStats?.average_time ?? 0}
          totalAttempts={progressStats?.total_attempts ?? 0}
          isLoading={isLoadingProgress}
        />
      </PageSection>
      {stats.recent_activity && stats.recent_activity.length > 0 && (
        <PageSection>
          <RecentActivity activities={stats.recent_activity} />
        </PageSection>
      )}
    </>
  );
}
