"use client";

/**
 * StudentChallengesBoard — Bandeau « défis du jour » (vue apprenant).
 *
 * Métaphore distincte de la constellation de progression (niveaux / paliers) : ici un
 * triplet d’objectifs quotidiens en rail pleine largeur, séparateurs discrets, sans carte
 * dashboard générique ni particules de fond.
 */

import Link from "next/link";
import { useMemo } from "react";
import { useDailyChallenges } from "@/hooks/useDailyChallenges";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useTranslations } from "next-intl";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { Calculator, Puzzle, Target, CheckCircle2, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DailyChallenge } from "@/types/api";

const CHALLENGE_ICONS = {
  volume_exercises: Calculator,
  specific_type: Target,
  logic_challenge: Puzzle,
} as const;

const ARC_R = 36;
const ARC_CIRCUMFERENCE = 2 * Math.PI * ARC_R;

function CircularProgress({ value, label }: { value: number; label: string }) {
  const offset = ARC_CIRCUMFERENCE * (1 - value / 100);
  return (
    <div className="relative flex size-20 shrink-0 items-center justify-center">
      <svg
        className="size-full rotate-[-90deg]"
        viewBox="0 0 100 100"
        aria-label={label}
        role="img"
      >
        <circle
          cx="50"
          cy="50"
          r={ARC_R}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          className="text-border"
        />
        <circle
          cx="50"
          cy="50"
          r={ARC_R}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          strokeLinecap="round"
          className="text-primary transition-[stroke-dashoffset] duration-700 ease-out motion-reduce:transition-none"
          strokeDasharray={ARC_CIRCUMFERENCE}
          strokeDashoffset={offset}
        />
      </svg>
      <span
        className="absolute inset-0 flex flex-col items-center justify-center text-center leading-tight"
        aria-hidden="true"
      >
        <span className="text-lg font-bold text-foreground tabular-nums sm:text-xl">
          {Math.round(value)}%
        </span>
      </span>
    </div>
  );
}

function DailyChallengeSlot({
  challenge,
  getTypeDisplay,
  t,
  reducedMotion,
}: {
  challenge: DailyChallenge;
  getTypeDisplay: (type: string | null) => string;
  t: ReturnType<typeof useTranslations>;
  reducedMotion: boolean;
}) {
  const isCompleted = challenge.status === "completed";
  const IconComponent =
    CHALLENGE_ICONS[challenge.challenge_type as keyof typeof CHALLENGE_ICONS] ?? Target;

  const label = getChallengeLabel(challenge, getTypeDisplay, t);
  const progress =
    challenge.target_count > 0
      ? Math.min(100, Math.round((challenge.completed_count / challenge.target_count) * 100))
      : 0;

  const ariaLabel = `${label} — ${isCompleted ? t("completed") : t("pending", { current: challenge.completed_count, target: challenge.target_count })}`;

  const slotShell = cn(
    "flex min-h-[8.5rem] flex-1 flex-col items-center justify-between gap-3 px-3 py-4 sm:min-h-[9rem] sm:px-4 sm:py-5",
    "transition-colors duration-200 motion-reduce:transition-none"
  );

  if (isCompleted) {
    return (
      <div className={cn(slotShell, "bg-muted/20")} aria-label={ariaLabel}>
        <div className="relative flex flex-col items-center gap-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-primary/15 text-primary">
            <CheckCircle2
              className={cn(
                "h-5 w-5",
                !reducedMotion && "motion-safe:animate-[challenge-pop_0.35s_ease-out_both]"
              )}
              aria-hidden="true"
            />
          </div>
          <span
            className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-[10px] font-bold bg-primary text-primary-foreground"
            aria-hidden="true"
          >
            +{challenge.bonus_points}
          </span>
        </div>
        <p className="text-center text-xs font-medium leading-snug text-muted-foreground line-through">
          {label}
        </p>
      </div>
    );
  }

  const href = getChallengeHref(challenge);
  return (
    <Link
      href={href}
      className={cn(
        slotShell,
        "group border-border/40 bg-background/40 hover:bg-muted/30",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      )}
      aria-label={ariaLabel}
    >
      <div className="relative flex flex-col items-center gap-2">
        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-muted text-foreground transition-colors group-hover:bg-primary/10 group-hover:text-primary">
          <IconComponent className="h-5 w-5" aria-hidden="true" />
        </div>
        <span
          className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-[10px] font-bold bg-muted-foreground/15 text-foreground"
          aria-hidden="true"
        >
          +{challenge.bonus_points}
        </span>
      </div>

      <p className="text-center text-xs font-medium leading-snug text-foreground">{label}</p>

      <div className="w-full max-w-[10rem] space-y-1" aria-hidden="true">
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-border">
          <div
            className="h-full rounded-full bg-primary transition-[width] duration-500 ease-out motion-reduce:transition-none"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-center text-[10px] text-muted-foreground tabular-nums">
          {challenge.completed_count}/{challenge.target_count}
        </p>
      </div>
    </Link>
  );
}

function DailyChallengesLoading({ title }: { title: string }) {
  return (
    <section
      className="w-full overflow-hidden rounded-xl border border-border/80 bg-muted/10"
      aria-busy="true"
      aria-label={title}
    >
      <div className="border-b border-border/60 px-4 py-4 sm:px-5 sm:py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="h-6 w-40 rounded-md bg-muted/70" />
            <div className="h-4 w-56 max-w-full rounded-md bg-muted/50" />
          </div>
          <div className="h-20 w-20 shrink-0 rounded-full bg-muted/70" />
        </div>
      </div>
      <div className="flex flex-col divide-y divide-border/60 sm:flex-row sm:divide-x sm:divide-y-0">
        {[0, 1, 2].map((i) => (
          <div key={i} className="min-h-[8.5rem] flex-1 px-3 py-4 sm:min-h-[9rem] sm:px-4">
            <div className="mx-auto flex h-11 w-11 rounded-full bg-muted/70" />
            <div className="mx-auto mt-3 h-3 w-24 rounded bg-muted/50" />
            <div className="mx-auto mt-4 h-1.5 w-full max-w-[10rem] rounded-full bg-muted/50" />
          </div>
        ))}
      </div>
    </section>
  );
}

export function StudentChallengesBoard() {
  const { challenges, isLoading } = useDailyChallenges();
  const { getTypeDisplay } = useExerciseTranslations();
  const t = useTranslations("dashboard.dailyChallenges");
  const { shouldReduceMotion } = useAccessibleAnimation();

  const completedCount = useMemo(
    () => challenges.filter((c) => c.status === "completed").length,
    [challenges]
  );

  const progressPct = challenges.length > 0 ? (completedCount / challenges.length) * 100 : 0;
  const allDone = completedCount === challenges.length && challenges.length > 0;
  const hasPending = challenges.some((c) => c.status === "pending");

  const firstPending = challenges.find((c) => c.status === "pending");
  const primaryCtaHref = firstPending ? getChallengeHref(firstPending) : "/exercises";

  if (isLoading) {
    return <DailyChallengesLoading title={t("title")} />;
  }

  return (
    <section
      className="w-full overflow-hidden rounded-xl border border-border/80 bg-muted/10 shadow-sm"
      role="region"
      aria-label={t("title")}
    >
      <div className="border-b border-border/60 px-4 py-4 sm:px-5 sm:py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <h3 className="text-lg font-semibold tracking-tight text-foreground">{t("title")}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {allDone ? t("allDone") : t("subtitle")}
            </p>
          </div>
          <CircularProgress
            value={progressPct}
            label={t("progressAriaLabel", { done: completedCount, total: challenges.length })}
          />
        </div>
      </div>

      <ul className="m-0 flex list-none flex-col divide-y divide-border/60 p-0 sm:flex-row sm:divide-x sm:divide-y-0">
        {challenges.map((challenge) => (
          <li key={challenge.id} className="min-w-0 flex-1">
            <DailyChallengeSlot
              challenge={challenge}
              getTypeDisplay={getTypeDisplay}
              t={t}
              reducedMotion={shouldReduceMotion}
            />
          </li>
        ))}
      </ul>

      {hasPending ? (
        <div className="border-t border-border/60 bg-muted/5 px-4 py-4 sm:px-5">
          <Link
            href={primaryCtaHref}
            className={cn(
              "flex w-full items-center justify-center gap-2 rounded-lg",
              "bg-primary px-4 py-3.5 text-sm font-semibold text-primary-foreground",
              "transition-colors hover:bg-primary/90",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            )}
          >
            {t("cta")}
            <ChevronRight className="h-4 w-4 shrink-0" aria-hidden="true" />
          </Link>
        </div>
      ) : null}

      {allDone ? (
        <div className="border-t border-border/60 px-4 py-3 sm:px-5">
          <div className="flex items-center justify-center gap-2 rounded-lg border border-border/60 bg-muted/20 py-3 text-sm font-medium text-foreground">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
            {t("allDoneMessage")}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function getChallengeHref(challenge: DailyChallenge): string {
  if (challenge.challenge_type === "logic_challenge") {
    return "/challenges";
  }
  if (challenge.challenge_type === "specific_type") {
    const type = (challenge.metadata?.exercise_type ?? "").toLowerCase();
    return type ? `/exercises?type=${encodeURIComponent(type)}` : "/exercises";
  }
  return "/exercises";
}

function getChallengeLabel(
  c: DailyChallenge,
  getTypeDisplay: (type: string | null) => string,
  t: ReturnType<typeof useTranslations>
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
