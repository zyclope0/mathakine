"use client";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export type ChallengeSolverGridAutoAnswerVariant = "sequence" | "pattern";

export interface ChallengeSolverGridAutoAnswerBlockProps {
  variant: ChallengeSolverGridAutoAnswerVariant;
  userAnswer: string;
  hasSubmitted: boolean;
  isSubmitting: boolean;
  onUserAnswerChange: (value: string) => void;
  onSubmit: () => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverGridAutoAnswerBlock({
  variant,
  userAnswer,
  hasSubmitted,
  isSubmitting,
  onUserAnswerChange,
  onSubmit,
  t,
}: ChallengeSolverGridAutoAnswerBlockProps) {
  const ariaLabel = variant === "sequence" ? t("sequenceAnswerLabel") : t("patternAnswerLabel");
  const placeholder =
    variant === "sequence" ? t("sequenceGridAnswerPlaceholder") : t("patternGridAnswerPlaceholder");
  const helperText =
    variant === "sequence" ? t("sequenceGridAnswerHelp") : t("patternGridAnswerHelp");

  return (
    <div className="space-y-3">
      <div className="p-4 bg-muted/50 rounded-xl border border-border">
        <p className="text-sm font-medium text-foreground mb-2">{t("yourAnswerLabel")}</p>
        {userAnswer.trim() ? (
          <Badge variant="outline" className="text-lg px-4 py-2">
            {userAnswer}
          </Badge>
        ) : (
          <p className="text-sm text-muted-foreground">{helperText}</p>
        )}
      </div>
      {userAnswer.trim() && <p className="text-xs text-muted-foreground">{helperText}</p>}
      <Input
        type="text"
        value={userAnswer}
        onChange={(e) => onUserAnswerChange(e.target.value)}
        placeholder={placeholder}
        className="text-lg"
        disabled={hasSubmitted}
        aria-label={ariaLabel}
        onKeyDown={(e) => {
          if (e.key === "Enter" && userAnswer.trim() && !isSubmitting) {
            onSubmit();
          }
        }}
      />
    </div>
  );
}
