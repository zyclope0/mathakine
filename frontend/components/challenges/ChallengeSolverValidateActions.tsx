"use client";

import { Button } from "@/components/ui/button";
import { Loader2, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export interface ChallengeSolverValidateActionsProps {
  hasSubmitted: boolean;
  isSubmitting: boolean;
  isAnswerEmpty: boolean;
  isDisabled: boolean;
  hintsUsedCount: number;
  availableHintsCount: number;
  hasHints: boolean;
  onSubmit: () => void;
  onRequestHint: () => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverValidateActions({
  hasSubmitted,
  isSubmitting,
  isAnswerEmpty,
  isDisabled,
  hintsUsedCount,
  availableHintsCount,
  hasHints,
  onSubmit,
  onRequestHint,
  t,
}: ChallengeSolverValidateActionsProps) {
  return (
    <div className="space-y-2 flex-1">
      <div className="flex gap-3">
        <Button
          onClick={onSubmit}
          disabled={isDisabled}
          className={cn(
            "flex-1 px-6 py-3 rounded-2xl font-medium transition-all",
            isAnswerEmpty && !isSubmitting
              ? "opacity-60 cursor-not-allowed bg-muted text-muted-foreground border border-border"
              : "bg-primary text-primary-foreground"
          )}
          aria-label={isSubmitting ? t("validating") : t("validateAnswer")}
          aria-busy={isSubmitting}
          aria-describedby={isAnswerEmpty && !isSubmitting ? "challenge-validate-hint" : undefined}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {t("checking")}
            </>
          ) : (
            t("validate")
          )}
        </Button>

        {hasHints && (
          <Button
            onClick={onRequestHint}
            variant="outline"
            disabled={
              hasSubmitted || (availableHintsCount > 0 && hintsUsedCount >= availableHintsCount)
            }
            className="border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 transition-colors px-6 py-3 rounded-2xl"
            aria-label={
              availableHintsCount > 0
                ? t("requestHint", {
                    current: hintsUsedCount + 1,
                    total: availableHintsCount,
                  })
                : t("requestHintGeneric")
            }
          >
            <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
            {availableHintsCount > 0
              ? t("hintButton", {
                  current: hintsUsedCount + 1,
                  total: availableHintsCount,
                })
              : t("hintButtonGeneric")}
          </Button>
        )}
      </div>

      {isAnswerEmpty && !isSubmitting && (
        <p
          id="challenge-validate-hint"
          className="text-center text-xs text-muted-foreground"
          aria-live="polite"
        >
          {t("validateHint")}
        </p>
      )}
    </div>
  );
}
