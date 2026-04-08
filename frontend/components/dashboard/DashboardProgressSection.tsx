import { CategoryAccuracyChart } from "@/components/dashboard/CategoryAccuracyChart";
import { ChallengesProgressWidget } from "@/components/dashboard/ChallengesProgressWidget";
import { PracticeConsistencyWidget } from "@/components/dashboard/PracticeConsistencyWidget";
import { ProgressTimelineWidget } from "@/components/dashboard/ProgressTimelineWidget";
import { VolumeByTypeChartLazy } from "@/components/dashboard/VolumeByTypeChartLazy";
import { PageSection } from "@/components/layout";
import type { ChallengesProgress } from "@/hooks/useChallengesProgress";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { TimelinePeriod } from "@/hooks/useProgressTimeline";

interface DashboardProgressSectionProps {
  challengesProgress: ChallengesProgress | null;
  isLoadingChallenges: boolean;
  isLoadingProgress: boolean;
  progressStats: ProgressStats | null;
  timelinePeriod: TimelinePeriod;
  onTimelinePeriodChange: (value: TimelinePeriod) => void;
}

export function DashboardProgressSection({
  challengesProgress,
  isLoadingChallenges,
  isLoadingProgress,
  progressStats,
  timelinePeriod,
  onTimelinePeriodChange,
}: DashboardProgressSectionProps) {
  return (
    <>
      <PageSection>
        <ProgressTimelineWidget period={timelinePeriod} onPeriodChange={onTimelinePeriodChange} />
      </PageSection>
      <PageSection>
        <div className="grid gap-6 md:grid-cols-2 items-stretch">
          <ChallengesProgressWidget
            completedChallenges={challengesProgress?.completed_challenges || 0}
            totalChallenges={challengesProgress?.total_challenges || 0}
            successRate={challengesProgress?.success_rate || 0}
            averageTime={challengesProgress?.average_time || 0}
            isLoading={isLoadingChallenges}
          />
          <CategoryAccuracyChart
            categoryData={progressStats?.by_category || {}}
            isLoading={isLoadingProgress}
          />
        </div>
      </PageSection>
      <PageSection>
        <div className="grid gap-6 md:grid-cols-2 items-stretch">
          <VolumeByTypeChartLazy categoryData={progressStats?.by_category ?? {}} />
          <PracticeConsistencyWidget period={timelinePeriod} />
        </div>
      </PageSection>
    </>
  );
}
