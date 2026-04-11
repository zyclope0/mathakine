"use client";

import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { DiagnosticTypeScore } from "@/hooks/useDiagnostic";

/** Shell glassmorphism — composant de module stable (évite remontage si défini inline). */
export function DiagnosticFocusBoard({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-card/90 backdrop-blur-xl border border-border shadow-[0_0_40px_rgba(0,0,0,0.15)] rounded-3xl p-8 md:p-12 w-full max-w-4xl mx-auto mt-8 md:mt-12",
        className
      )}
    >
      {children}
    </div>
  );
}

export function DiagnosticProgressBar({
  current,
  max,
  label,
}: {
  current: number;
  max: number;
  label: string;
}) {
  const pct = Math.min(100, Math.round((current / max) * 100));
  return (
    <div className="mb-8">
      <div className="flex justify-between text-sm text-muted-foreground mb-2">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
          role="progressbar"
          title={label}
          aria-label={label}
          aria-valuenow={current}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
}

const LEVEL_COLORS: Record<string, string> = {
  INITIE: "text-sky-400 border-sky-500/30 bg-sky-500/10",
  PADAWAN: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
  CHEVALIER: "text-amber-400 border-amber-500/30 bg-amber-500/10",
  MAITRE: "text-orange-400 border-orange-500/30 bg-orange-500/10",
  GRAND_MAITRE: "text-rose-400 border-rose-500/30 bg-rose-500/10",
};

export function DiagnosticScoreCard({
  typeKey,
  score,
  typeLabel,
  levelLabel,
  scoreDetail,
}: {
  typeKey: string;
  score: DiagnosticTypeScore;
  typeLabel: string;
  levelLabel: string;
  scoreDetail: string;
}) {
  const colorClass =
    LEVEL_COLORS[score.difficulty] ?? "text-muted-foreground border-border bg-muted/50";
  return (
    <div
      className={cn("flex items-center justify-between rounded-xl border p-4", colorClass)}
      aria-label={`${typeKey}: ${levelLabel}`}
    >
      <div>
        <p className="font-semibold text-foreground capitalize">{typeLabel}</p>
        <p className="text-sm mt-0.5 opacity-80">{scoreDetail}</p>
      </div>
      <Badge variant="outline" className={cn("text-sm font-medium border", colorClass)}>
        {levelLabel}
      </Badge>
    </div>
  );
}
