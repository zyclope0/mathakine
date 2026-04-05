"use client";

import Link from "next/link";
import { Calculator, Puzzle, Award, Star, BookOpen, Target, TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useUserStats } from "@/hooks/useUserStats";
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
 * Structure linéaire, colonne unique, zéro onglets :
 *   1. Salutation + mini-index d'ancrage (COGA 4.1.1 — prévisibilité structurelle)
 *   2. "Que veux-tu faire ?" — 3 CTA empilés
 *   3. "Mes révisions du jour" — SpacedRepetitionSummaryWidget
 *   4. "Mes défis" — StudentChallengesBoard (Constellation Board, design OVERDRIVE-C/NI-13)
 *   5. "Ma progression" — Streak + Niveau + Compétences
 *
 * Mini-index : chips d'ancrage visibles dès le chargement, permettant à l'apprenant
 * de savoir ce qui l'attend avant de scroller (UDL 1.3, W3C COGA 4.1.1).
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

/** Chips d'ancrage — index visuel de la page */
const PAGE_ANCHORS = [
  { id: "section-reviews", icon: BookOpen, labelKey: "pageMap.reviews" },
  { id: "section-challenges", icon: Target, labelKey: "pageMap.challenges" },
  { id: "section-progress", icon: TrendingUp, labelKey: "pageMap.progress" },
] as const;

function HomeLearnerContent() {
  const t = useTranslations("homeLearner");
  const { user } = useAuth();
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { stats, isLoading: isLoadingStats } = useUserStats();

  const firstName = user?.full_name?.split(" ")[0] ?? user?.username ?? null;

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
            Navigation native <a href="#id">, zéro JS, accessible clavier. */}
        <nav className="mt-4 flex flex-wrap gap-2" aria-label={t("pageMap.label")}>
          {PAGE_ANCHORS.map(({ id, icon: Icon, labelKey }) => (
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

      {/* Actions rapides — colonne unique, boutons pleine largeur */}
      <LearnerCard>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
          {t("actions.heading")}
        </h2>

        <div className="flex flex-col gap-3">
          {/* Action primaire — exercices */}
          <Link
            href="/exercises"
            className={cn(
              "flex items-center gap-4 rounded-xl px-5 py-4",
              "bg-primary text-primary-foreground",
              "hover:bg-primary/90 active:scale-[0.98]",
              "transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label={t("actions.exercises")}
          >
            <Calculator className="h-6 w-6 flex-shrink-0" aria-hidden="true" />
            <span className="text-base font-semibold">{t("actions.exercises")}</span>
          </Link>

          {/* Action secondaire — défis */}
          <Link
            href="/challenges"
            className={cn(
              "flex items-center gap-4 rounded-xl px-5 py-4",
              "bg-[var(--bg-learner,var(--card))] border border-border/60",
              "text-foreground hover:border-primary/40 hover:bg-primary/5",
              "transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label={t("actions.challenges")}
          >
            <Puzzle className="h-6 w-6 flex-shrink-0 text-primary" aria-hidden="true" />
            <span className="text-base font-medium">{t("actions.challenges")}</span>
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
            <Award className="h-6 w-6 flex-shrink-0 text-amber-400" aria-hidden="true" />
            <span className="text-base font-medium">{t("actions.badges")}</span>
          </Link>
        </div>
      </LearnerCard>

      {/* Révisions espacées du jour — toujours rendu pour ne pas casser l'ancrage page-map.
          isLoading passe le skeleton au widget ; hasError affiche un état d'erreur propre. */}
      <section id="section-reviews" aria-labelledby="reviews-heading" className="scroll-mt-20">
        <h2
          id="reviews-heading"
          className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4"
        >
          {t("reviews.heading")}
        </h2>
        <SpacedRepetitionSummaryWidget
          summary={stats?.spaced_repetition ?? EMPTY_SPACED_REPETITION}
          isLoading={isLoadingStats}
          hasError={!isLoadingStats && !stats}
        />
      </section>

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
        <h2
          id="progress-heading"
          className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4"
        >
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

      {/* Lien secondaire — voir tous les badges */}
      <div className="pb-4">
        <Link
          href="/badges"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors"
        >
          <Star className="h-4 w-4" aria-hidden="true" />
          {t("progress.seeBadges")}
        </Link>
      </div>
    </LearnerLayout>
  );
}
