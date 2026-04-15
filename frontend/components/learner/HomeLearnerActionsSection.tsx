"use client";

import Link from "next/link";
import { Calculator, Puzzle, Award } from "lucide-react";
import { LearnerCard } from "@/components/learner/LearnerCard";
import { cn } from "@/lib/utils";
import type { HomeLearnerNamespaceT } from "@/components/learner/homeLearnerI18n";

interface HomeLearnerActionsSectionProps {
  exerciseHref: string;
  challengeHref: string;
  exerciseRecoLabel: string | null;
  challengeRecoLabel: string | null;
  onExerciseLinkNavigate: () => void;
  onChallengeLinkNavigate: () => void;
  t: HomeLearnerNamespaceT;
}

export function HomeLearnerActionsSection({
  exerciseHref,
  challengeHref,
  exerciseRecoLabel,
  challengeRecoLabel,
  onExerciseLinkNavigate,
  onChallengeLinkNavigate,
  t,
}: HomeLearnerActionsSectionProps) {
  return (
    <section id="section-actions" aria-labelledby="actions-heading">
      <LearnerCard>
        <h2 id="actions-heading" className="section-title mb-4">
          {t("actions.heading")}
        </h2>

        <div className="flex flex-col gap-3">
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
            onClick={onExerciseLinkNavigate}
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
            onClick={onChallengeLinkNavigate}
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
}
