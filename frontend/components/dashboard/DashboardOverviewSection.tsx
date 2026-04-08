import { DailyChallengesWidget } from "@/components/dashboard/DailyChallengesWidget";
import { QuickStartActions } from "@/components/dashboard/QuickStartActions";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { PageSection } from "@/components/layout";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { UserStats } from "@/hooks/useUserStats";

interface DashboardOverviewSectionProps {
  isLoadingProgress: boolean;
  progressStats: ProgressStats | null;
  stats: UserStats;
}

export function DashboardOverviewSection({
  isLoadingProgress,
  progressStats,
  stats,
}: DashboardOverviewSectionProps) {
  return (
    <PageSection>
      <div className="space-y-3">
        <QuickStartActions />
        <SpacedRepetitionSummaryWidget summary={stats.spaced_repetition} />
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-stretch">
          <div className="md:col-span-8 flex flex-col min-h-0">
            <DailyChallengesWidget />
          </div>
          <div className="md:col-span-4 flex flex-col min-h-0">
            <StreakWidget
              currentStreak={progressStats?.current_streak || 0}
              highestStreak={progressStats?.highest_streak || 0}
              isLoading={isLoadingProgress}
            />
          </div>
        </div>
      </div>
    </PageSection>
  );
}
