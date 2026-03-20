"use client";

import Link from "next/link";
import { useDailyChallenges } from "@/hooks/useDailyChallenges";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useTranslations } from "next-intl";
import { Calendar, ChevronRight, CheckCircle2, Calculator, Puzzle, Target } from "lucide-react";
import type { DailyChallenge } from "@/types/api";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

/** Icônes par type de défi — défini au niveau module pour éviter "component created during render" */
const CHALLENGE_ICONS = {
  volume_exercises: Calculator,
  specific_type: Target,
  logic_challenge: Puzzle,
} as const;

/**
 * Widget F02 — Défis quotidiens.
 *
 * Affiche les 3 défis du jour avec barre de progression.
 * Fondements EdTech : Cepeda (pratique distribuée), Deci & Ryan (SDT, optionnel).
 */
export function DailyChallengesWidget() {
  const { challenges, isLoading } = useDailyChallenges();
  const { getTypeDisplay } = useExerciseTranslations();
  const t = useTranslations("dashboard.dailyChallenges");

  if (isLoading) {
    return (
      <div
        className="rounded-xl border border-border/50 bg-card/40 backdrop-blur-md shadow-sm p-4 md:p-5"
        role="region"
        aria-busy="true"
        aria-label={t("title")}
      >
        <div className="flex items-center gap-3 mb-4">
          <Skeleton className="h-10 w-10 rounded-full shrink-0" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-48" />
          </div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3 rounded-lg border border-border p-3">
              <Skeleton className="h-9 w-9 rounded-lg shrink-0" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-16" />
              </div>
              <Skeleton className="h-5 w-12 shrink-0" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const completedCount = challenges.filter((c) => c.status === "completed").length;
  const hasPending = challenges.some((c) => c.status === "pending");

  return (
    <div
      className="flex-1 min-h-0 flex flex-col rounded-xl border border-border/50 bg-card/40 backdrop-blur-md shadow-sm p-4 md:p-5"
      role="region"
      aria-label={t("title")}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
            <Calendar className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-foreground">{t("title")}</h3>
            <p className="text-xs text-muted-foreground">{t("subtitle")}</p>
          </div>
        </div>
        {completedCount > 0 && (
          <span className="text-sm font-medium text-primary">
            {completedCount}/3 {t("completed")}
          </span>
        )}
      </div>

      <div className="space-y-3">
        {challenges.map((challenge) => (
          <ChallengeItem
            key={challenge.id}
            challenge={challenge}
            getTypeDisplay={getTypeDisplay}
            t={t}
          />
        ))}
      </div>

      {hasPending && (
        <Link
          href="/exercises"
          className="mt-4 flex items-center justify-center gap-1 rounded-lg text-sm font-medium transition-colors border border-border bg-transparent hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 w-full"
        >
          {t("cta")}
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      )}
    </div>
  );
}

function ChallengeItem({
  challenge,
  getTypeDisplay,
  t,
}: {
  challenge: DailyChallenge;
  getTypeDisplay: (type: string | null) => string;
  t: (key: string, values?: Record<string, number | string>) => string;
}) {
  const isCompleted = challenge.status === "completed";
  const label = getChallengeLabel(challenge, getTypeDisplay, t);
  const IconComponent =
    CHALLENGE_ICONS[challenge.challenge_type as keyof typeof CHALLENGE_ICONS] ?? Target;

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border p-3 transition-colors",
        isCompleted
          ? "border-success/30 bg-success/5"
          : "bg-muted/30 hover:bg-muted/50 border-border/50"
      )}
    >
      <div
        className={cn(
          "flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center",
          isCompleted ? "bg-success/20 text-success" : "bg-primary/10 text-primary"
        )}
      >
        {isCompleted ? (
          <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
        ) : (
          <IconComponent className="h-5 w-5" aria-hidden="true" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p
          className={cn(
            "text-sm font-medium",
            isCompleted ? "text-muted-foreground line-through" : "text-foreground"
          )}
        >
          {label}
        </p>
        {!isCompleted && (
          <p className="text-xs text-muted-foreground mt-0.5">
            {t("pending", {
              current: challenge.completed_count,
              target: challenge.target_count,
            })}
          </p>
        )}
      </div>
      <span
        className={cn(
          "inline-flex items-center px-2 py-1 rounded-md text-xs font-bold shrink-0",
          isCompleted ? "bg-success/10 text-success" : "bg-primary/10 text-primary"
        )}
      >
        {t("bonus", { points: challenge.bonus_points })}
      </span>
    </div>
  );
}

function getChallengeLabel(
  c: DailyChallenge,
  getTypeDisplay: (type: string | null) => string,
  t: (key: string, values?: Record<string, number | string>) => string
): string {
  const count = c.target_count;
  if (c.challenge_type === "volume_exercises") {
    return t("volume", { count });
  }
  if (c.challenge_type === "specific_type") {
    const type = (c.metadata?.exercise_type ?? "").toLowerCase();
    return t("specific", {
      count,
      type: getTypeDisplay(type) || type,
    });
  }
  if (c.challenge_type === "logic_challenge") {
    return t("logic", { count });
  }
  return t("fallback", { count });
}
