"use client";

/**
 * ChallengeSolverCommandBar — Zone de réponse et de validation du défi.
 *
 * Façade FFI-L10 + FFI-L18B : sous-composants `ChallengeSolver*` dans le même dossier.
 * Logique métier / dérivation : useChallengeSolverController + lib/challenges/challengeSolver*.
 */

import { useTranslations } from "next-intl";
import type { ChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";
import type { ChallengeTextInputKind } from "@/lib/challenges/challengeSolver";
import { getCommandBarInteractionModeFlags } from "@/lib/challenges/challengeSolverCommandBar";
import { ChallengeSolverFreeTextAnswerBlock } from "@/components/challenges/ChallengeSolverFreeTextAnswerBlock";
import { ChallengeSolverGridAutoAnswerBlock } from "@/components/challenges/ChallengeSolverGridAutoAnswerBlock";
import { ChallengeSolverGridDeductionBlock } from "@/components/challenges/ChallengeSolverGridDeductionBlock";
import { ChallengeSolverMcqGrid } from "@/components/challenges/ChallengeSolverMcqGrid";
import { ChallengeSolverOrderPuzzleBlock } from "@/components/challenges/ChallengeSolverOrderPuzzleBlock";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";
import { ChallengeSolverValidateActions } from "@/components/challenges/ChallengeSolverValidateActions";
import { ChallengeSolverVisualButtons } from "@/components/challenges/ChallengeSolverVisualButtons";

export interface ChallengeSolverCommandBarProps {
  userAnswer: string;
  hasSubmitted: boolean;
  isSubmitting: boolean;
  isAnswerEmpty: boolean;
  isDisabled: boolean;
  hintsUsedCount: number;
  availableHintsCount: number;
  hasHints: boolean;

  showMcq: boolean;
  choicesArray: string[];
  hasVisualButtons: boolean;
  visualChoices: string[];
  visualPositions: number[];
  visualSelections: Record<number, string>;
  responseMode: ChallengeResponseMode;
  challengeType: string;
  hasVisualData: boolean;
  puzzleOrder: string[];
  textInputKind: ChallengeTextInputKind;

  onSelectChoice: (choice: string) => void;
  onSelectVisualPosition: (pos: number, choice: string) => void;
  onSelectVisualSimple: (choice: string) => void;
  onUserAnswerChange: (value: string) => void;
  onSubmit: () => void;
  onRequestHint: () => void;
}

export function ChallengeSolverCommandBar({
  userAnswer,
  hasSubmitted,
  isSubmitting,
  isAnswerEmpty,
  isDisabled,
  hintsUsedCount,
  availableHintsCount,
  hasHints,
  showMcq,
  choicesArray,
  hasVisualButtons,
  visualChoices,
  visualPositions,
  visualSelections,
  responseMode,
  challengeType,
  hasVisualData,
  puzzleOrder,
  textInputKind,
  onSelectChoice,
  onSelectVisualPosition,
  onSelectVisualSimple,
  onUserAnswerChange,
  onSubmit,
  onRequestHint,
}: ChallengeSolverCommandBarProps) {
  const tRaw = useTranslations("challenges.solver");
  const t: ChallengeSolverCommandBarT = (key, values) =>
    values === undefined ? tRaw(key) : tRaw(key, values);

  const { isOrderPuzzle, isGridSequence, isGridPattern, isGridDeduction } =
    getCommandBarInteractionModeFlags({
      responseMode,
      challengeType,
      userAnswer,
      hasVisualData,
      puzzleOrderLength: puzzleOrder.length,
    });

  return (
    <div
      data-learner-context
      className="bg-[var(--bg-learner,var(--card))] border border-border/40 rounded-2xl p-6 max-w-5xl mx-auto"
    >
      <h3 className="text-lg font-semibold text-foreground mb-4">{t("yourAnswer")}</h3>
      <div className="space-y-4">
        {showMcq ? (
          <ChallengeSolverMcqGrid
            choicesArray={choicesArray}
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            onSelectChoice={onSelectChoice}
            t={t}
          />
        ) : hasVisualButtons ? (
          <ChallengeSolverVisualButtons
            visualPositions={visualPositions}
            visualChoices={visualChoices}
            visualSelections={visualSelections}
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            onSelectPosition={onSelectVisualPosition}
            onSelectSimple={onSelectVisualSimple}
            t={t}
          />
        ) : isOrderPuzzle ? (
          <ChallengeSolverOrderPuzzleBlock
            puzzleOrder={puzzleOrder}
            userAnswer={userAnswer}
            onUserAnswerChange={onUserAnswerChange}
            t={t}
          />
        ) : isGridSequence ? (
          <ChallengeSolverGridAutoAnswerBlock
            variant="sequence"
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            isSubmitting={isSubmitting}
            onUserAnswerChange={onUserAnswerChange}
            onSubmit={onSubmit}
            t={t}
          />
        ) : isGridPattern ? (
          <ChallengeSolverGridAutoAnswerBlock
            variant="pattern"
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            isSubmitting={isSubmitting}
            onUserAnswerChange={onUserAnswerChange}
            onSubmit={onSubmit}
            t={t}
          />
        ) : isGridDeduction ? (
          <ChallengeSolverGridDeductionBlock userAnswer={userAnswer} t={t} />
        ) : (
          <ChallengeSolverFreeTextAnswerBlock
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            isSubmitting={isSubmitting}
            textInputKind={textInputKind}
            onUserAnswerChange={onUserAnswerChange}
            onSubmit={onSubmit}
            t={t}
          />
        )}

        <ChallengeSolverValidateActions
          hasSubmitted={hasSubmitted}
          isSubmitting={isSubmitting}
          isAnswerEmpty={isAnswerEmpty}
          isDisabled={isDisabled}
          hintsUsedCount={hintsUsedCount}
          availableHintsCount={availableHintsCount}
          hasHints={hasHints}
          onSubmit={onSubmit}
          onRequestHint={onRequestHint}
          t={t}
        />
      </div>
    </div>
  );
}
