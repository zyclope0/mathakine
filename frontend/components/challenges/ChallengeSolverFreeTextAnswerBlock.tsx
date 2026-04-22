"use client";

import { Input } from "@/components/ui/input";
import { BookOpen, ChevronDown } from "lucide-react";
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
      {textInputKind === "chess" && <ChessNotationGuide t={t} />}
      {textInputKind === "visual" && (
        <p className="text-xs text-muted-foreground">{t("visualAnswerFormat")}</p>
      )}
      {textInputKind === "visualOrderedCsv" && (
        <p className="text-xs text-muted-foreground">{t("visualOrderedAnswerFormat")}</p>
      )}
    </div>
  );
}

function ChessNotationGuide({ t }: { t: ChallengeSolverCommandBarT }) {
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">{t("chessAnswerFormat")}</p>
      <details className="group rounded-xl border border-border/60 bg-muted/30 px-3 py-2 text-sm">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 text-foreground marker:hidden">
          <span className="inline-flex items-center gap-2 font-medium">
            <BookOpen className="h-4 w-4 text-primary" aria-hidden />
            {t("chessNotationGuideTitle")}
          </span>
          <ChevronDown
            className="h-4 w-4 shrink-0 text-muted-foreground transition-transform group-open:rotate-180"
            aria-hidden
          />
        </summary>
        <div className="mt-2 space-y-3 border-t border-border/50 pt-3 text-xs leading-relaxed text-muted-foreground">
          <p>{t("chessNotationBoard")}</p>
          <div className="grid gap-2 sm:grid-cols-2">
            <div className="rounded-lg bg-background/70 p-3">
              <p className="font-medium text-foreground">{t("chessNotationFrenchTitle")}</p>
              <p className="mt-1">{t("chessNotationFrenchPieces")}</p>
            </div>
            <div className="rounded-lg bg-background/70 p-3">
              <p className="font-medium text-foreground">{t("chessNotationEnglishTitle")}</p>
              <p className="mt-1">{t("chessNotationEnglishPieces")}</p>
            </div>
          </div>
          <p>{t("chessNotationSymbols")}</p>
          <p>
            {t("chessNotationExamplePrefix")}{" "}
            <code className="rounded bg-background px-1.5 py-0.5 font-mono text-foreground">
              Dd7+, Rf8, Df7#
            </code>
          </p>
        </div>
      </details>
    </div>
  );
}
