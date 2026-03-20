"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Calculator, Puzzle, Layers, ArrowRight } from "lucide-react";
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
  const { recommendations, recordOpen } = useRecommendations();
  const t = useTranslations("dashboard.quickStart");

  // Priorisation : priority desc, puis premier exercice et premier défi
  const sorted = [...recommendations].sort((a, b) => (b.priority ?? 5) - (a.priority ?? 5));
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
    // R4b — feedback reco : uniquement parcours guidé (reco réelle avec id)
    if (bestExercise?.id != null && bestExercise.exercise_id != null) {
      void recordOpen(bestExercise.id).catch(() => {
        /* ne pas bloquer la navigation */
      });
    }
  };
  const handleChallengeClick = () => {
    trackQuickStartClick({
      type: "challenge",
      guided: !!bestChallenge?.challenge_id,
      ...(bestChallenge?.challenge_id != null && { targetId: bestChallenge.challenge_id }),
    });
    if (bestChallenge?.id != null && bestChallenge.challenge_id != null) {
      void recordOpen(bestChallenge.id).catch(() => {
        /* ne pas bloquer la navigation */
      });
    }
  };
  const handleInterleavedClick = () => {
    trackQuickStartClick({
      type: "interleaved",
      guided: false,
    });
  };

  return (
    <section
      className="dashboard-card-surface p-4 sm:p-5"
      aria-label={t("title")}
      data-quick-start-block="true"
    >
      <h2 className="text-base font-semibold text-foreground mb-4">{t("title")}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <Link
          href={exerciseHref}
          onClick={handleExerciseClick}
          className="dashboard-card-surface-interactive group flex flex-col gap-4 p-5
            focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          data-quick-start="exercise"
          data-quick-start-guided={!!bestExercise?.exercise_id}
        >
          <div className="flex items-start gap-4">
            <div className="dashboard-card-icon-chip">
              <Calculator className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-foreground">{t("exerciseCta")}</p>
              {bestExercise ? (
                <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                  {bestExercise.exercise_title || bestExercise.exercise_type}
                </p>
              ) : (
                <p className="text-xs text-muted-foreground mt-0.5">{t("browseAll")}</p>
              )}
            </div>
          </div>
          <span className="self-start inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium transition-colors duration-200 group-hover:bg-primary/20 group-hover:gap-3">
            {t("startCta")} <ArrowRight className="h-4 w-4 shrink-0" aria-hidden="true" />
          </span>
        </Link>

        <Link
          href={challengeHref}
          onClick={handleChallengeClick}
          className="dashboard-card-surface-interactive group flex flex-col gap-4 p-5
            focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          data-quick-start="challenge"
          data-quick-start-guided={!!bestChallenge?.challenge_id}
        >
          <div className="flex items-start gap-4">
            <div className="dashboard-card-icon-chip">
              <Puzzle className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-foreground">{t("challengeCta")}</p>
              {bestChallenge ? (
                <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                  {bestChallenge.challenge_title || t("challengeDefault")}
                </p>
              ) : (
                <p className="text-xs text-muted-foreground mt-0.5">{t("browseAll")}</p>
              )}
            </div>
          </div>
          <span className="self-start inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium transition-colors duration-200 group-hover:bg-primary/20 group-hover:gap-3">
            {t("startCta")} <ArrowRight className="h-4 w-4 shrink-0" aria-hidden="true" />
          </span>
        </Link>

        <Link
          href="/exercises/interleaved"
          onClick={handleInterleavedClick}
          className="dashboard-card-surface-interactive group flex flex-col gap-4 p-5
            focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          data-quick-start="interleaved"
        >
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary shadow-sm">
              <Layers className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-foreground">{t("interleavedCta")}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{t("interleavedSubtext")}</p>
            </div>
          </div>
          <span className="self-start inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium transition-colors duration-200 group-hover:bg-primary/20 group-hover:gap-3">
            {t("startCta")} <ArrowRight className="h-4 w-4 shrink-0" aria-hidden="true" />
          </span>
        </Link>
      </div>
    </section>
  );
}
