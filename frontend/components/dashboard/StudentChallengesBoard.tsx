"use client";

/**
 * StudentChallengesBoard — Tableau de défis gamifié pour la vue étudiant (NI-13 / OVERDRIVE-C).
 *
 * Design : Constellation Board.
 * - 3 défis = 3 nœuds d'une constellation reliés par des traits SVG qui se "dessinent"
 *   progressivement au fur et à mesure des completions (stroke-dashoffset CSS).
 * - Arc de progression circulaire SVG pour le score global.
 * - Fond avec micro-particules colorées héritant de --primary (CSS box-shadow trick).
 * - Burst de complétion : @keyframes CSS pur, aucune lib externe.
 * - 100 % multi-thème via var(--primary), var(--card), var(--border), etc.
 * - prefers-reduced-motion respecté nativement (classe .motion-reduce:* + classe conditionnelle).
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

/* ── Icônes par type ─────────────────────────────────────────────────────── */
const CHALLENGE_ICONS = {
  volume_exercises: Calculator,
  specific_type: Target,
  logic_challenge: Puzzle,
} as const;

/* ── Points de la constellation (positions relatives, 0-100) ─────────────── */
const NODE_POSITIONS = [
  { x: 50, y: 18 }, // sommet
  { x: 14, y: 78 }, // bas gauche
  { x: 86, y: 78 }, // bas droite
] as const;

/* ── Traits de la constellation : paires d'indices de nœuds ─────────────── */
const EDGES = [
  [0, 1],
  [1, 2],
  [2, 0],
] as const;

/* ── Arc de progression circulaire ──────────────────────────────────────── */
const ARC_R = 36; // rayon SVG viewBox 100x100
const ARC_CIRCUMFERENCE = 2 * Math.PI * ARC_R;

function CircularProgress({
  value,
  size = 96,
  label,
}: {
  value: number; // 0-100
  size?: number;
  label: string;
}) {
  const offset = ARC_CIRCUMFERENCE * (1 - value / 100);
  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        aria-label={label}
        role="img"
        className="rotate-[-90deg]"
      >
        {/* Piste de fond */}
        <circle
          cx="50"
          cy="50"
          r={ARC_R}
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          className="text-border"
        />
        {/* Arc de progression */}
        <circle
          cx="50"
          cy="50"
          r={ARC_R}
          fill="none"
          stroke="currentColor"
          strokeWidth="7"
          strokeLinecap="round"
          className="text-primary transition-all duration-700 ease-out motion-reduce:transition-none"
          strokeDasharray={ARC_CIRCUMFERENCE}
          strokeDashoffset={offset}
        />
      </svg>
      {/* Texte centré — rotation inverse pour rester lisible */}
      <span
        className="absolute inset-0 flex flex-col items-center justify-center text-center leading-tight"
        aria-hidden="true"
      >
        <span className="text-xl font-bold text-foreground tabular-nums">{Math.round(value)}%</span>
      </span>
    </div>
  );
}

/* ── Nœud de constellation ───────────────────────────────────────────────── */
function ConstellationNode({
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

  const nodeClasses = cn(
    "flex flex-col items-center gap-3 rounded-2xl border p-4 transition-all duration-300",
    "motion-reduce:transition-none",
    isCompleted
      // Nœud terminé : statique, pas de hover (aucune action possible)
      ? "border-primary/40 bg-primary/[0.08]"
      // Nœud actif : interactif, hover explicite
      : "group border-border/60 bg-card hover:border-primary/30 hover:bg-primary/[0.04] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
  );

  // Nœuds complétés : non-cliquables (informatifs)
  // Nœuds en attente : Link vers la destination correspondant au type de défi
  if (isCompleted) {
    return (
      <div className={nodeClasses} role="listitem" aria-label={ariaLabel}>
        {/* Icône complétée avec halo */}
        <div className="relative">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-primary">
            <CheckCircle2
              className={cn("h-6 w-6", !reducedMotion && "animate-[challenge-pop_0.4s_ease-out_both]")}
              aria-hidden="true"
            />
          </div>
          {!reducedMotion && (
            <span
              className="pointer-events-none absolute inset-0 rounded-full bg-primary/30 animate-[challenge-halo_0.6s_ease-out_forwards]"
              aria-hidden="true"
            />
          )}
          <span
            className="absolute -right-2 -top-2 flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-[10px] font-bold bg-primary text-primary-foreground"
            aria-hidden="true"
          >
            +{challenge.bonus_points}
          </span>
        </div>

        {/* Label barré */}
        <p className="text-center text-xs font-medium leading-snug text-muted-foreground line-through">
          {label}
        </p>
      </div>
    );
  }

  // Nœud actif → Link cliquable vers la destination du défi
  const href = getChallengeHref(challenge);
  return (
    <Link
      href={href}
      className={nodeClasses}
      role="listitem"
      aria-label={ariaLabel}
    >
      {/* Icône avec burst conditionnel */}
      <div className="relative">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted/60 text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors duration-300">
          <IconComponent className="h-6 w-6" aria-hidden="true" />
        </div>

        {/* Badge points */}
        <span
          className="absolute -right-2 -top-2 flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-[10px] font-bold bg-muted text-muted-foreground"
          aria-hidden="true"
        >
          +{challenge.bonus_points}
        </span>
      </div>

      {/* Label */}
      <p className="text-center text-xs font-medium leading-snug text-foreground">
        {label}
      </p>

      {/* Mini barre de progression */}
      <div className="w-full space-y-1" aria-hidden="true">
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted/60">
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

/* ── SVG constellation ───────────────────────────────────────────────────── */
function ConstellationSvg({
  completedCount,
  reducedMotion,
}: {
  completedCount: number;
  reducedMotion: boolean;
}) {
  // Un trait est "allumé" si BOTH nœuds qu'il relie sont complétés
  // Simplifié : on allume les traits progressivement selon completedCount (0→3)
  const activeEdges = useMemo(() => {
    // Ordre d'activation : 0-1, 1-2, 2-0
    return EDGES.map((_, i) => i < completedCount);
  }, [completedCount]);

  const LINE_LENGTH = 120; // approximation pour stroke-dasharray

  return (
    <svg
      viewBox="0 0 200 150"
      className="pointer-events-none absolute inset-0 h-full w-full"
      aria-hidden="true"
    >
      {EDGES.map(([from, to], i) => {
        const x1 = (NODE_POSITIONS[from].x / 100) * 200;
        const y1 = (NODE_POSITIONS[from].y / 100) * 150;
        const x2 = (NODE_POSITIONS[to].x / 100) * 200;
        const y2 = (NODE_POSITIONS[to].y / 100) * 150;
        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const isActive = activeEdges[i];

        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            className={cn(
              isActive ? "text-primary" : "text-border/60",
              !reducedMotion && "transition-all duration-700"
            )}
            strokeDasharray={length}
            strokeDashoffset={reducedMotion ? 0 : isActive ? 0 : length}
            style={
              !reducedMotion
                ? {
                    transition: `stroke-dashoffset 0.7s ease ${i * 0.15}s, color 0.5s ease`,
                  }
                : undefined
            }
          />
        );
      })}

      {/* Points des nœuds */}
      {NODE_POSITIONS.map((pos, i) => (
        <circle
          key={i}
          cx={(pos.x / 100) * 200}
          cy={(pos.y / 100) * 150}
          r="4"
          fill="currentColor"
          className={cn(i < completedCount ? "text-primary" : "text-border/60")}
        />
      ))}
    </svg>
  );
}

/* ── Composant principal ─────────────────────────────────────────────────── */
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

  if (isLoading) {
    return (
      <div
        className="rounded-2xl border border-border/50 bg-card/60 p-6 space-y-4"
        aria-busy="true"
        aria-label={t("title")}
      >
        <div className="flex justify-between items-center">
          <div className="h-5 w-32 rounded bg-muted/60 animate-pulse" />
          <div className="h-16 w-16 rounded-full bg-muted/60 animate-pulse" />
        </div>
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-28 rounded-2xl bg-muted/40 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-border/50 bg-card/60 p-5 space-y-5"
      role="region"
      aria-label={t("title")}
    >
      {/* Micro-particules de fond — CSS box-shadow trick, hérite de --primary */}
      <div
        className="pointer-events-none absolute inset-0 opacity-40"
        aria-hidden="true"
        style={{
          backgroundImage: `
            radial-gradient(circle at 15% 25%, color-mix(in srgb, var(--primary) 12%, transparent) 0%, transparent 50%),
            radial-gradient(circle at 85% 70%, color-mix(in srgb, var(--primary) 8%, transparent) 0%, transparent 40%)
          `,
        }}
      />

      {/* Constellation SVG de fond (décorative) */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <ConstellationSvg completedCount={completedCount} reducedMotion={shouldReduceMotion} />
      </div>

      {/* En-tête avec arc de progression */}
      <div className="relative flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground">{t("title")}</h3>
          <p className="text-sm text-muted-foreground mt-0.5">
            {allDone ? t("allDone") : t("subtitle")}
          </p>
        </div>
        <CircularProgress
          value={progressPct}
          size={80}
          label={t("progressAriaLabel", { done: completedCount, total: challenges.length })}
        />
      </div>

      {/* Grille constellation — 3 nœuds */}
      <div className="relative grid grid-cols-3 gap-3" role="list">
        {challenges.map((challenge) => (
          <ConstellationNode
            key={challenge.id}
            challenge={challenge}
            getTypeDisplay={getTypeDisplay}
            t={t}
            reducedMotion={shouldReduceMotion}
          />
        ))}
      </div>

      {/* CTA */}
      {hasPending && (
        <Link
          href="/exercises"
          className={cn(
            "relative flex w-full items-center justify-center gap-2 rounded-xl",
            "bg-primary text-primary-foreground",
            "py-3 text-sm font-semibold",
            "transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]",
            "motion-reduce:transition-none motion-reduce:hover:scale-100 motion-reduce:active:scale-100",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          )}
        >
          {t("cta")}
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      )}

      {/* État victoire */}
      {allDone && (
        <div className="relative flex items-center justify-center gap-2 rounded-xl border border-primary/30 bg-primary/10 py-3 text-sm font-semibold text-primary">
          <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
          {t("allDoneMessage")}
        </div>
      )}
    </section>
  );
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */

/**
 * Détermine la route cible d'un nœud de défi selon son type.
 * - volume_exercises  → /exercises (liste libre)
 * - specific_type     → /exercises?type={exercise_type} (filtre pré-appliqué)
 * - logic_challenge   → /challenges
 */
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
