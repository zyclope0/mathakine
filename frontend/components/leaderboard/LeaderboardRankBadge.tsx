"use client";

import { cn } from "@/lib/utils";
import { RANK_MEDALS } from "@/lib/constants/leaderboard";

export function LeaderboardRankBadge({ rank, label }: { rank: number; label: string }) {
  const isPodium = rank >= 1 && rank <= 3;
  const medalClass = cn(
    "flex-shrink-0 text-center leading-none",
    isPodium ? "w-10" : "w-10 flex items-center justify-center"
  );

  if (RANK_MEDALS[rank]) {
    return (
      <span
        className={cn(medalClass, rank === 1 ? "text-4xl" : rank === 2 ? "text-3xl" : "text-2xl")}
        aria-label={label}
      >
        {RANK_MEDALS[rank]}
      </span>
    );
  }
  return (
    <span className={medalClass} aria-label={label}>
      <span className="h-8 w-8 rounded-full bg-muted/40 flex items-center justify-center font-mono text-sm text-muted-foreground">
        {rank}
      </span>
    </span>
  );
}
