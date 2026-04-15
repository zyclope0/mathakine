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

  const arrowClass =
    "h-4 w-4 shrink-0 transition-transform duration-200 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0 group-hover:translate-x-0.5";

  return (
    <section
      className="dashboard-card-surface--calm p-4 sm:p-5"
      aria-label={t("title")}
      data-quick-start-block="true"
    >
      <h2 className="text-base font-semibold text-foreground mb-3">{t("title")}</h2>

      {/* Layout asymétrique : exercice prend toute la largeur en priorité */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {/* Carte 1 — EXERCICE : primaire, pleine largeur, accent coloré */}
        <Link
          href={exerciseHref}
          onClick={handleExerciseClick}
          className="sm:col-span-2 dashboard-card-surface-interactive--calm group flex items-center gap-4 p-4 sm:p-5 border-l-4 border-primary"
          data-quick-start="exercise"
          data-quick-start-guided={!!bestExercise?.exercise_id}
        >
          <div className="dashboard-card-icon-chip--calm shrink-0">
            <Calculator className="h-6 w-6" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-semibold text-foreground">{t("exerciseCta")}</p>
            {bestExercise ? (
              <p className="text-sm text-muted-foreground mt-0.5 line-clamp-1 leading-snug">
                {bestExercise.exercise_title || bestExercise.exercise_type}
              </p>
            ) : (
              <p className="text-sm text-muted-foreground mt-0.5 leading-snug">{t("browseAll")}</p>
            )}
          </div>
          <div className="flex items-center gap-1.5 text-sm font-semibold text-primary shrink-0">
            <span>{t("startCta")}</span>
            <ArrowRight className={arrowClass} aria-hidden="true" />
          </div>
        </Link>

        {/* Carte 2 — DÉFI : secondaire, demi-largeur, hauteur autonome */}
        <Link
          href={challengeHref}
          onClick={handleChallengeClick}
          className="dashboard-card-surface-interactive--calm group flex flex-col gap-2 p-4 sm:p-5"
          data-quick-start="challenge"
          data-quick-start-guided={!!bestChallenge?.challenge_id}
        >
          <div className="flex items-start gap-3">
            <div className="dashboard-card-icon-chip--calm">
              <Puzzle className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-foreground">{t("challengeCta")}</p>
              {bestChallenge ? (
                <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2 leading-snug">
                  {bestChallenge.challenge_title || t("challengeDefault")}
                </p>
              ) : (
                <p className="text-sm text-muted-foreground mt-0.5 leading-snug">
                  {t("browseAll")}
                </p>
              )}
            </div>
          </div>
          <div className="mt-auto flex min-h-11 items-center gap-1.5 text-sm font-semibold text-primary group-hover:underline underline-offset-4">
            <span>{t("startCta")}</span>
            <ArrowRight className={arrowClass} aria-hidden="true" />
          </div>
        </Link>

        {/* Carte 3 — ENTRAÎNEMENT VARIÉ : tertiaire, ton sobre, badge pédagogique */}
        <Link
          href="/exercises/interleaved"
          onClick={handleInterleavedClick}
          className="dashboard-card-surface-interactive--calm group flex flex-col gap-2 p-4 sm:p-5"
          data-quick-start="interleaved"
        >
          <div className="flex items-start gap-3">
            <div className="dashboard-card-icon-chip--calm">
              <Layers className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="font-semibold text-foreground">{t("interleavedCta")}</p>
                <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-muted text-muted-foreground leading-none tracking-normal">
                  {t("interleavedBadge")}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mt-0.5 leading-snug">
                {t("interleavedSubtext")}
              </p>
            </div>
          </div>
          <div className="mt-auto flex min-h-11 items-center gap-1.5 text-sm font-medium text-muted-foreground group-hover:text-primary group-hover:underline underline-offset-4 transition-colors">
            <span>{t("startCta")}</span>
            <ArrowRight className={arrowClass} aria-hidden="true" />
          </div>
        </Link>
      </div>
    </section>
  );
}
