import Link from "next/link";
import { BookOpen, ChevronRight } from "lucide-react";
import { DailyChallengesWidget } from "@/components/dashboard/DailyChallengesWidget";
import { QuickStartActions } from "@/components/dashboard/QuickStartActions";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { Button } from "@/components/ui/button";
import { PageSection } from "@/components/layout";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { UserStats } from "@/hooks/useUserStats";

interface DashboardBetaHelpContent {
  title: string;
  description: string;
  cta: string;
}

interface DashboardOverviewSectionProps {
  betaHelp: DashboardBetaHelpContent;
  isLoadingProgress: boolean;
  progressStats: ProgressStats | null;
  stats: UserStats;
}

export function DashboardOverviewSection({
  betaHelp,
  isLoadingProgress,
  progressStats,
  stats,
}: DashboardOverviewSectionProps) {
  return (
    <PageSection>
      <div className="space-y-4">
        <QuickStartActions />
        <section
          aria-label={betaHelp.title}
          className="rounded-2xl bg-muted/15 px-4 py-4 ring-1 ring-border/50 sm:px-5 sm:py-5"
        >
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
            <div className="min-w-0 space-y-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary ring-1 ring-primary/15">
                <BookOpen className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                <span>{betaHelp.title}</span>
              </div>
              <p className="max-w-[62ch] text-pretty text-sm leading-relaxed text-muted-foreground">
                {betaHelp.description}
              </p>
            </div>
            <Button asChild variant="outline" className="w-full min-h-11 shrink-0 gap-2 sm:w-auto">
              <Link href="/docs">
                {betaHelp.cta}
                <ChevronRight className="h-4 w-4 shrink-0" aria-hidden="true" />
              </Link>
            </Button>
          </div>
        </section>
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
