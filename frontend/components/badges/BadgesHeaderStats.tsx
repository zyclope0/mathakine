"use client";

/**
 * BadgesHeaderStats — barre de stats condensée sous le PageHeader.
 * Composant purement visuel.
 * FFI-L12.
 */

import { Zap, Star, Target } from "lucide-react";
import { cn } from "@/lib/utils";
import type { RankInfo } from "@/lib/badges/badgesPage";

interface BadgesHeaderStatsProps {
  totalPoints: number;
  currentLevel: number;
  rankInfo: RankInfo;
  earnedCount: number;
  totalCount: number;
  progressPercent: number;
  statsCompactLabel: string;
  levelTooltip: string;
  rankTooltip: string;
}

export function BadgesHeaderStats({
  totalPoints,
  currentLevel,
  rankInfo,
  earnedCount,
  totalCount,
  progressPercent,
  statsCompactLabel,
  levelTooltip,
  rankTooltip,
}: BadgesHeaderStatsProps) {
  return (
    <div
      className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground"
      role="region"
      aria-label={statsCompactLabel}
    >
      <span className="flex items-center gap-1.5">
        <Zap className="h-4 w-4 text-yellow-500" aria-hidden="true" />
        <strong className="text-foreground">{totalPoints}</strong> pts
      </span>
      <span className="flex items-center gap-1.5" title={levelTooltip}>
        <Star className="h-4 w-4 text-primary" aria-hidden="true" />
        <strong className="text-foreground">Niv. {currentLevel}</strong>
      </span>
      <span className={cn("flex items-center gap-1.5", rankInfo.color)} title={rankTooltip}>
        <span aria-hidden="true">{rankInfo.icon}</span>
        <strong>{rankInfo.title}</strong>
      </span>
      <span className="flex items-center gap-1.5">
        <Target className="h-4 w-4 text-green-500" aria-hidden="true" />
        <strong className="text-foreground">
          {earnedCount}/{totalCount}
        </strong>{" "}
        badges
      </span>
      <div
        className="w-24 bg-muted rounded-full h-2 overflow-hidden"
        role="progressbar"
        aria-valuenow={progressPercent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Progression: ${progressPercent.toFixed(0)}%`}
      >
        <div
          className="bg-primary h-2 rounded-full transition-all duration-700"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
    </div>
  );
}
