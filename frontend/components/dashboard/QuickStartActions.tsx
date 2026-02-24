"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Calculator, Swords } from "lucide-react";
import { useRecommendations } from "@/hooks/useRecommendations";
import { useTranslations } from "next-intl";
import { trackDashboardView, trackQuickStartClick } from "@/lib/analytics/edtech";

/**
 * Parcours guidé (P1) — Bloc "Que veux-tu faire ?" en tête du dashboard.
 *
 * Comportement voulu :
 * - Exercice : avec reco → /exercises/:id (direct), sans reco → /exercises (liste)
 * - Défi : avec reco → /challenge/:id (direct), sans reco → /challenges (liste)
 * Les deux CTA sont symétriques : direct vers l'item recommandé ou liste.
 *
 * Priorisation : reco avec exercise_id ou challenge_id, tri par priority desc.
 * L'API exclut les exercices/défis archivés.
 *
 * Instrumentation EdTech : data-quick-start-* pour CTR, temps vers 1er attempt.
 */
export function QuickStartActions() {
  const { recommendations, isLoading } = useRecommendations();
  const t = useTranslations("dashboard.quickStart");

  // Priorisation : priority desc, puis premier exercice et premier défi
  const sorted = [...recommendations].sort(
    (a, b) => (b.priority ?? 5) - (a.priority ?? 5)
  );
  const bestExercise = sorted.find((r) => r.exercise_id && !r.challenge_id);
  const bestChallenge = sorted.find((r) => r.challenge_id);

  const exerciseHref = bestExercise?.exercise_id
    ? `/exercises/${bestExercise.exercise_id}`
    : "/exercises";
  const challengeHref = bestChallenge?.challenge_id
    ? `/challenge/${bestChallenge.challenge_id}`
    : "/challenges";

  useEffect(() => {
    trackDashboardView();
  }, []);

  const handleExerciseClick = () => {
    trackQuickStartClick({
      type: "exercise",
      guided: !!bestExercise?.exercise_id,
      ...(bestExercise?.exercise_id != null && { targetId: bestExercise.exercise_id }),
    });
  };
  const handleChallengeClick = () => {
    trackQuickStartClick({
      type: "challenge",
      guided: !!bestChallenge?.challenge_id,
      ...(bestChallenge?.challenge_id != null && { targetId: bestChallenge.challenge_id }),
    });
  };

  return (
    <section
      className="rounded-xl border border-primary/20 bg-primary/5 p-4 sm:p-5"
      aria-label={t("title")}
      data-quick-start-block="true"
    >
      <h2 className="text-base font-semibold text-foreground mb-4">
        {t("title")}
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:gap-4">
        <Link
          href={exerciseHref}
          onClick={handleExerciseClick}
          className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-primary/30 bg-card p-4 transition-all hover:border-primary hover:bg-primary/10 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          data-quick-start="exercise"
          data-quick-start-guided={!!bestExercise?.exercise_id}
        >
          <Calculator
            className="h-8 w-8 text-primary"
            aria-hidden="true"
          />
          <span className="text-sm font-medium text-center">
            {t("exerciseCta")}
          </span>
          {bestExercise && (
            <span className="text-xs text-muted-foreground line-clamp-1">
              {bestExercise.exercise_title || bestExercise.exercise_type}
            </span>
          )}
        </Link>
        <Link
          href={challengeHref}
          onClick={handleChallengeClick}
          className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-primary/30 bg-card p-4 transition-all hover:border-primary hover:bg-primary/10 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          data-quick-start="challenge"
          data-quick-start-guided={!!bestChallenge?.challenge_id}
        >
          <Swords
            className="h-8 w-8 text-primary"
            aria-hidden="true"
          />
          <span className="text-sm font-medium text-center">
            {t("challengeCta")}
          </span>
          {bestChallenge && (
            <span className="text-xs text-muted-foreground line-clamp-1">
              {bestChallenge.challenge_title || t("challengeDefault")}
            </span>
          )}
        </Link>
      </div>
    </section>
  );
}
