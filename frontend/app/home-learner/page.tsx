"use client";

import Link from "next/link";
import { Calculator, Puzzle, Award, BookOpen, Target, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useUserStats } from "@/hooks/useUserStats";
import { useRecommendations } from "@/hooks/useRecommendations";
import { HOME_LEARNER_ROUTE_ACCESS } from "@/lib/auth/routeAccess";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LearnerLayout } from "@/components/learner/LearnerLayout";
import { LearnerCard } from "@/components/learner/LearnerCard";
import { StreakWidget } from "@/components/dashboard/StreakWidget";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { LevelEstablishedWidget } from "@/components/dashboard/LevelEstablishedWidget";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import { StudentChallengesBoard } from "@/components/dashboard/StudentChallengesBoard";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";
import { cn } from "@/lib/utils";

/** Fallback vide — utilisé quand stats n'est pas encore chargé.
 * Évite de masquer la section Révisions et de casser l'ancrage de la page-map. */
const EMPTY_SPACED_REPETITION: SpacedRepetitionUserSummary = {
  f04_initialized: false,
  active_cards_count: 0,
  due_today_count: 0,
  overdue_count: 0,
  next_review_date: null,
};

/**
 * Page d'accueil dédiée aux apprenants (rôle canonique `apprenant`). — NI-4 / NI-13
 *
 * Structure linéaire, colonne unique, zéro onglets.
 *
 * Ordre des sections — conditionnel selon urgence révisions :
 *
 * Cas normal (aucune révision urgente) :
 *   1. Salutation + mini-index d'ancrage
 *   2. "Que veux-tu faire ?" — 3 CTA
 *   3. "À revoir aujourd'hui" — SpacedRepetitionSummaryWidget
 *   4. "Mes défis du jour" — StudentChallengesBoard
 *   5. "Ma progression" — Streak + Niveau
 *
 * Cas urgent (due_today_count + overdue_count > 0) :
 *   1. Salutation + mini-index d'ancrage
 *   2. "À revoir aujourd'hui" — remonté avant les CTA
 *   3. "Que veux-tu faire ?" — 3 CTA
 *   4. "Mes défis du jour"
 *   5. "Ma progression"
 *
 * Les chips PAGE_ANCHORS reflètent l'ordre réel affiché.
 * Scroll natif CSS — aucune lib, prefers-reduced-motion respecté par le navigateur.
 */
export default function HomeLearnerPage() {
  return (
    <ProtectedRoute
      requireOnboardingCompleted={HOME_LEARNER_ROUTE_ACCESS.requireOnboardingCompleted}
      allowedRoles={HOME_LEARNER_ROUTE_ACCESS.allowedRoles}
      prioritizeRoleRedirect={HOME_LEARNER_ROUTE_ACCESS.prioritizeRoleRedirect}
      redirectAuthenticatedTo={HOME_LEARNER_ROUTE_ACCESS.redirectAuthenticatedTo}
    >
      <HomeLearnerContent />
    </ProtectedRoute>
  );
}

function HomeLearnerContent() {
  const t = useTranslations("homeLearner");
  const { user } = useAuth();
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { stats, isLoading: isLoadingStats } = useUserStats();
  const { recommendations, isLoading: isLoadingReco, recordOpen } = useRecommendations();

  // Eager fallback: use general pages while loading, switch to specific reco once available.
  // Picks the first recommendation that has a resolved target id.
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

  // Révisions urgentes dès que les stats sont chargées et qu'il y a du travail en attente.
  // Pendant le chargement (isLoadingStats), on reste en ordre normal pour éviter le layout shift.
  const hasUrgentReviews = !isLoadingStats && (sr.due_today_count > 0 || sr.overdue_count > 0);

  // Chips d'ancrage reflétant l'ordre réel affiché (COGA 4.1.1 prévisibilité structurelle).
  // En mode urgent, les Révisions passent avant les CTA dans la liste de chips.
  const pageAnchors = hasUrgentReviews
    ? [
        { id: "section-reviews", icon: BookOpen, labelKey: "pageMap.reviews" as const },
        { id: "section-actions", icon: Calculator, labelKey: "pageMap.actions" as const },
        { id: "section-challenges", icon: Target, labelKey: "pageMap.challenges" as const },
        { id: "section-progress", icon: TrendingUp, labelKey: "pageMap.progress" as const },
      ]
    : [
        { id: "section-actions", icon: Calculator, labelKey: "pageMap.actions" as const },
        { id: "section-reviews", icon: BookOpen, labelKey: "pageMap.reviews" as const },
        { id: "section-challenges", icon: Target, labelKey: "pageMap.challenges" as const },
        { id: "section-progress", icon: TrendingUp, labelKey: "pageMap.progress" as const },
      ];

  const reviewsSection = (
    <section id="section-reviews" aria-labelledby="reviews-heading" className="scroll-mt-20">
      <h2
        id="reviews-heading"
        className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4"
      >
        {t("reviews.heading")}
      </h2>
      <SpacedRepetitionSummaryWidget
        summary={sr}
        isLoading={isLoadingStats}
        hasError={!isLoadingStats && !stats}
      />
    </section>
  );

  const actionsSection = (
    <section id="section-actions" aria-labelledby="actions-heading">
      <LearnerCard>
        <h2
          id="actions-heading"
          className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4"
        >
          {t("actions.heading")}
        </h2>

        <div className="flex flex-col gap-3">
          {/* Action primaire — exercices (lien vers reco si disponible, sinon liste générale) */}
          <Link
            href={exerciseHref}
            className={cn(
              "flex items-center gap-4 rounded-xl px-5 py-4",
              "bg-primary text-primary-foreground",
              "hover:bg-primary/90 active:scale-[0.98]",
              "transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label={
              exerciseRecoLabel
                ? `${t("actions.exercises")} — ${exerciseRecoLabel}`
                : t("actions.exercises")
            }
            onClick={() => {
              if (firstExerciseRec) void recordOpen(firstExerciseRec.id);
            }}
          >
            <Calculator className="h-6 w-6 flex-shrink-0" aria-hidden="true" />
            <span className="flex flex-col">
              <span className="text-base font-semibold">{t("actions.exercises")}</span>
              {exerciseRecoLabel && (
                <span className="text-xs font-normal opacity-80 leading-tight mt-0.5">
                  {exerciseRecoLabel}
                </span>
              )}
            </span>
          </Link>

          {/* Action secondaire — défis (lien vers reco si disponible, sinon liste générale) */}
          <Link
            href={challengeHref}
            className={cn(
              "flex items-center gap-4 rounded-xl px-5 py-4",
              "bg-[var(--bg-learner,var(--card))] border border-border/60",
              "text-foreground hover:border-primary/40 hover:bg-primary/5",
              "transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label={
              challengeRecoLabel
                ? `${t("actions.challenges")} — ${challengeRecoLabel}`
                : t("actions.challenges")
            }
            onClick={() => {
              if (firstChallengeRec) void recordOpen(firstChallengeRec.id);
            }}
          >
            <Puzzle className="h-6 w-6 flex-shrink-0 text-primary" aria-hidden="true" />
            <span className="flex flex-col">
              <span className="text-base font-medium">{t("actions.challenges")}</span>
              {challengeRecoLabel && (
                <span className="text-xs font-normal text-muted-foreground leading-tight mt-0.5">
                  {challengeRecoLabel}
                </span>
              )}
            </span>
          </Link>

          {/* Action tertiaire — badges */}
          <Link
            href="/badges"
            className={cn(
              "flex items-center gap-4 rounded-xl px-5 py-4",
              "bg-[var(--bg-learner,var(--card))] border border-border/60",
              "text-foreground hover:border-primary/40 hover:bg-primary/5",
              "transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label={t("actions.badges")}
          >
            <Award
              className="h-6 w-6 flex-shrink-0"
              style={{ color: "var(--rank-gold)" }}
              aria-hidden="true"
            />
            <span className="text-base font-medium">{t("actions.badges")}</span>
          </Link>
        </div>
      </LearnerCard>
    </section>
  );

  return (
    <LearnerLayout maxWidth="2xl">
      {/* Salutation + mini-index */}
      <div className="pt-4 pb-2">
        <h1 className="text-2xl font-bold text-foreground leading-snug">
          {firstName ? t("greeting", { name: firstName }) : t("greetingGeneric")}
        </h1>
        <p className="mt-1 text-base text-muted-foreground">{t("subtitle")}</p>

        {/* Mini-index d'ancrage — COGA 4.1.1 prévisibilité structurelle.
            Chips cliquables → scroll doux vers la section cible.
            Ordre reflète le rendu réel (urgent = révisions avant CTA).
            Navigation native <a href="#id">, zéro JS, accessible clavier. */}
        <nav className="mt-4 flex flex-wrap gap-2" aria-label={t("pageMap.label")}>
          {pageAnchors.map(({ id, icon: Icon, labelKey }) => (
            <a
              key={id}
              href={`#${id}`}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5",
                "border border-border/60 bg-[var(--bg-learner,var(--card))]",
                "text-xs font-medium text-muted-foreground",
                "hover:border-primary/40 hover:text-primary hover:bg-primary/5",
                "transition-colors duration-150",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
              )}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {t(labelKey)}
            </a>
          ))}
        </nav>
      </div>

      {/* Ordre conditionnel : révisions urgentes remontent avant les CTA */}
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

      {/* Défis du jour — Constellation Board (design OVERDRIVE-C / NI-13) */}
      <section
        id="section-challenges"
        aria-labelledby="challenges-heading"
        className="scroll-mt-20"
      >
        <h2
          id="challenges-heading"
          className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4"
        >
          {t("challenges.heading")}
        </h2>
        <StudentChallengesBoard />
      </section>

      {/* Progression — après les CTA, pas en concurrence */}
      <section id="section-progress" aria-labelledby="progress-heading" className="scroll-mt-20">
        {/* Heading sr-only : ancre chip navigation conservée, pas de doublon visuel
            avec les titres internes de StreakWidget et LevelIndicator. */}
        <h2 id="progress-heading" className="sr-only">
          {t("progress.heading")}
        </h2>

        <div className="flex flex-col gap-4">
          <StreakWidget
            currentStreak={progressStats?.current_streak ?? 0}
            highestStreak={progressStats?.highest_streak ?? 0}
            isLoading={isLoadingProgress}
          />

          {user?.gamification_level && <LevelIndicator level={user.gamification_level} />}

          <LevelEstablishedWidget />
        </div>
      </section>
    </LearnerLayout>
  );
}
