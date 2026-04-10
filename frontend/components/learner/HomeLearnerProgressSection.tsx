"use client";

import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { LevelEstablishedWidget } from "@/components/dashboard/LevelEstablishedWidget";
import type { HomeLearnerNamespaceT } from "@/components/learner/homeLearnerI18n";
import type { GamificationLevelIndicator } from "@/types/api";

interface HomeLearnerProgressSectionProps {
  currentStreak: number;
  highestStreak: number;
  isLoadingProgress: boolean;
  gamificationLevel: GamificationLevelIndicator | null | undefined;
  t: HomeLearnerNamespaceT;
}

export function HomeLearnerProgressSection({
  currentStreak,
  highestStreak,
  isLoadingProgress,
  gamificationLevel,
  t,
}: HomeLearnerProgressSectionProps) {
  return (
    <section id="section-progress" aria-labelledby="progress-heading" className="scroll-mt-20">
      <h2 id="progress-heading" className="sr-only">
        {t("progress.heading")}
      </h2>

      <div className="flex flex-col gap-4">
        <StreakWidget
          currentStreak={currentStreak}
          highestStreak={highestStreak}
          isLoading={isLoadingProgress}
        />

        {gamificationLevel && <LevelIndicator level={gamificationLevel} />}

        <LevelEstablishedWidget />
      </div>
    </section>
  );
}
