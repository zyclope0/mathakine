"use client";

import { cn } from "@/lib/utils";
import { useCountUp } from "@/lib/hooks/useCountUp";

/** Points animés : count-up de 0 → valeur, rejoue à chaque changement de valeur */
export function LeaderboardAnimatedPoints({ value, rank }: { value: number; rank: number }) {
  const duration = rank <= 3 ? 900 : rank <= 10 ? 650 : 450;
  const displayed = useCountUp(value, duration);

  const colorClass =
    rank === 1
      ? "text-[var(--rank-gold)]"
      : rank === 2
        ? "text-[var(--rank-silver)]"
        : rank === 3
          ? "text-[var(--rank-bronze)]"
          : "text-amber-400";

  return (
    <span
      className={cn(
        "flex-shrink-0 font-bold tabular-nums",
        rank <= 3 ? "text-base sm:text-lg" : "text-sm sm:text-base",
        colorClass
      )}
      aria-label={`${value} points`}
      aria-live="off"
    >
      {displayed.toLocaleString()}
      <span className="text-xs font-normal opacity-60 ml-0.5" aria-hidden>
        pts
      </span>
    </span>
  );
}
