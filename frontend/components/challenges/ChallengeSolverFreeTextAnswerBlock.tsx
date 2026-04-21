"use client";

import { Input } from "@/components/ui/input";
import type { ChallengeTextInputKind } from "@/lib/challenges/challengeSolver";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export interface ChallengeSolverFreeTextAnswerBlockProps {
  userAnswer: string;
  hasSubmitted: boolean;
  isSubmitting: boolean;
  textInputKind: ChallengeTextInputKind;
  onUserAnswerChange: (value: string) => void;
  onSubmit: () => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverFreeTextAnswerBlock({
  userAnswer,
  hasSubmitted,
  isSubmitting,
  textInputKind,
  onUserAnswerChange,
  onSubmit,
  t,
}: ChallengeSolverFreeTextAnswerBlockProps) {
  const placeholder =
    textInputKind === "chess"
      ? t("chessAnswerPlaceholder")
      : textInputKind === "visualOrderedCsv"
        ? t("visualOrderedAnswerPlaceholder")
        : textInputKind === "visual"
          ? t("visualAnswerPlaceholder")
          : t("enterAnswer");

  return (
    <div className="space-y-1.5">
      <Input
        type="text"
        value={userAnswer}
        onChange={(e) => onUserAnswerChange(e.target.value)}
        placeholder={placeholder}
        className="text-lg"
        disabled={hasSubmitted}
        aria-label={t("answerFieldLabel")}
        aria-required="true"
        onKeyDown={(e) => {
          if (e.key === "Enter" && userAnswer.trim() && !isSubmitting) {
            onSubmit();
          }
        }}
      />
      {textInputKind === "chess" && (
        <p className="text-xs text-muted-foreground">{t("chessAnswerFormat")}</p>
      )}
      {textInputKind === "visual" && (
        <p className="text-xs text-muted-foreground">{t("visualAnswerFormat")}</p>
      )}
      {textInputKind === "visualOrderedCsv" && (
        <p className="text-xs text-muted-foreground">{t("visualOrderedAnswerFormat")}</p>
      )}
    </div>
  );
}
