"use client";

import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";
import type { HomeLearnerNamespaceT } from "@/components/learner/homeLearnerI18n";

interface HomeLearnerReviewsSectionProps {
  summary: SpacedRepetitionUserSummary;
  isLoading: boolean;
  hasError: boolean;
  t: HomeLearnerNamespaceT;
}

export function HomeLearnerReviewsSection({
  summary,
  isLoading,
  hasError,
  t,
}: HomeLearnerReviewsSectionProps) {
  return (
    <section id="section-reviews" aria-labelledby="reviews-heading" className="scroll-mt-20">
      <h2 id="reviews-heading" className="section-title mb-4">
        {t("reviews.heading")}
      </h2>
      <SpacedRepetitionSummaryWidget summary={summary} isLoading={isLoading} hasError={hasError} />
    </section>
  );
}
