"use client";

import { Calculator, BookOpen, Target, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useUserStats } from "@/hooks/useUserStats";
import { useRecommendations } from "@/hooks/useRecommendations";
import { LearnerLayout } from "@/components/learner/LearnerLayout";
import { StudentChallengesBoard } from "@/components/dashboard/StudentChallengesBoard";
import { EMPTY_SPACED_REPETITION } from "@/components/learner/homeLearnerConstants";
import { HomeLearnerPageMap } from "@/components/learner/HomeLearnerPageMap";
import type { HomeLearnerPageAnchor } from "@/components/learner/HomeLearnerPageMap";
import { HomeLearnerReviewsSection } from "@/components/learner/HomeLearnerReviewsSection";
import { HomeLearnerActionsSection } from "@/components/learner/HomeLearnerActionsSection";
import { HomeLearnerProgressSection } from "@/components/learner/HomeLearnerProgressSection";

/**
 * Contenu page apprenant — hooks + composition des sections.
 * Ordre conditionnel révisions / CTA inchangé (NI-4 / NI-13).
 */
export function HomeLearnerContent() {
  const t = useTranslations("homeLearner");
  const { user } = useAuth();
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { stats, isLoading: isLoadingStats } = useUserStats();
  const { recommendations, isLoading: isLoadingReco, recordOpen } = useRecommendations();

  const firstExerciseRec = recommendations.find(
    (r) => (r.recommendation_type === "exercise" || !r.recommendation_type) && r.exercise_id != null
  );
  const firstChallengeRec = recommendations.find(
    (r) => r.recommendation_type === "challenge" && r.challenge_id != null
  );

  const exerciseHref = firstExerciseRec?.exercise_id
    ? `/exercises/${firstExerciseRec.exercise_id}`
    : "/exercises";
  const challengeHref = firstChallengeRec?.challenge_id
    ? `/challenge/${firstChallengeRec.challenge_id}`
    : "/challenges";

  const exerciseRecoLabel =
    !isLoadingReco && firstExerciseRec?.exercise_title
      ? t("actions.exercisesReco", { title: firstExerciseRec.exercise_title })
      : null;
  const challengeRecoLabel =
    !isLoadingReco && firstChallengeRec?.challenge_title
      ? t("actions.challengesReco", { title: firstChallengeRec.challenge_title })
      : null;

  const firstName = user?.full_name?.split(" ")[0] ?? user?.username ?? null;

  const sr = stats?.spaced_repetition ?? EMPTY_SPACED_REPETITION;

  const hasUrgentReviews = !isLoadingStats && (sr.due_today_count > 0 || sr.overdue_count > 0);

  const pageAnchors: HomeLearnerPageAnchor[] = hasUrgentReviews
    ? [
        { id: "section-reviews", icon: BookOpen, labelKey: "pageMap.reviews" },
        { id: "section-actions", icon: Calculator, labelKey: "pageMap.actions" },
        { id: "section-challenges", icon: Target, labelKey: "pageMap.challenges" },
        { id: "section-progress", icon: TrendingUp, labelKey: "pageMap.progress" },
      ]
    : [
        { id: "section-actions", icon: Calculator, labelKey: "pageMap.actions" },
        { id: "section-reviews", icon: BookOpen, labelKey: "pageMap.reviews" },
        { id: "section-challenges", icon: Target, labelKey: "pageMap.challenges" },
        { id: "section-progress", icon: TrendingUp, labelKey: "pageMap.progress" },
      ];

  const reviewsSection = (
    <HomeLearnerReviewsSection
      summary={sr}
      isLoading={isLoadingStats}
      hasError={!isLoadingStats && !stats}
      t={t}
    />
  );

  const actionsSection = (
    <HomeLearnerActionsSection
      exerciseHref={exerciseHref}
      challengeHref={challengeHref}
      exerciseRecoLabel={exerciseRecoLabel}
      challengeRecoLabel={challengeRecoLabel}
      onExerciseLinkNavigate={() => {
        if (firstExerciseRec) void recordOpen(firstExerciseRec.id);
      }}
      onChallengeLinkNavigate={() => {
        if (firstChallengeRec) void recordOpen(firstChallengeRec.id);
      }}
      t={t}
    />
  );

  return (
    <LearnerLayout maxWidth="2xl">
      <div className="pt-4 pb-2">
        <h1 className="text-2xl font-bold text-foreground leading-snug">
          {firstName ? t("greeting", { name: firstName }) : t("greetingGeneric")}
        </h1>
        <p className="mt-1 text-base text-muted-foreground">{t("subtitle")}</p>

        <HomeLearnerPageMap anchors={pageAnchors} t={t} />
      </div>

      {hasUrgentReviews ? (
        <>
          {reviewsSection}
          {actionsSection}
        </>
      ) : (
        <>
          {actionsSection}
          {reviewsSection}
        </>
      )}

      <section
        id="section-challenges"
        aria-labelledby="challenges-heading"
        className="scroll-mt-20"
      >
        <h2 id="challenges-heading" className="heading-section mb-4">
          {t("challenges.heading")}
        </h2>
        <StudentChallengesBoard />
      </section>

      <HomeLearnerProgressSection
        currentStreak={progressStats?.current_streak ?? 0}
        highestStreak={progressStats?.highest_streak ?? 0}
        isLoadingProgress={isLoadingProgress}
        gamificationLevel={user?.gamification_level}
        t={t}
      />
    </LearnerLayout>
  );
}
