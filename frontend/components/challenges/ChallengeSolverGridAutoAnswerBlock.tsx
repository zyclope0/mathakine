"use client";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export type ChallengeSolverGridAutoAnswerVariant = "sequence" | "pattern";

export interface ChallengeSolverGridAutoAnswerBlockProps {
  variant: ChallengeSolverGridAutoAnswerVariant;
  userAnswer: string;
  onUserAnswerChange: (value: string) => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverGridAutoAnswerBlock({
  variant,
  userAnswer,
  onUserAnswerChange,
  t,
}: ChallengeSolverGridAutoAnswerBlockProps) {
  const ariaLabel = variant === "sequence" ? t("sequenceAnswerLabel") : t("patternAnswerLabel");

  return (
    <div className="space-y-3">
      <div className="p-4 bg-muted/50 rounded-xl border border-border">
        <p className="text-sm font-medium text-foreground mb-2">{t("yourAnswerLabel")}</p>
        <Badge variant="outline" className="text-lg px-4 py-2">
          {userAnswer}
        </Badge>
      </div>
      <p className="text-xs text-muted-foreground">{t("modifyInVisualization")}</p>
      <Input
        type="text"
        value={userAnswer}
        onChange={(e) => onUserAnswerChange(e.target.value)}
        placeholder={t("answerFromVisualization")}
        className="opacity-50"
        disabled
        aria-label={ariaLabel}
      />
    </div>
  );
}
