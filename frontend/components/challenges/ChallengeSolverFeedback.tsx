"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Lightbulb, RotateCcw } from "lucide-react";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import { MathText } from "@/components/ui/MathText";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";

interface ChallengeSolverFeedbackProps {
  isCorrect: boolean;
  pointsEarned?: number | null | undefined;
  solutionExplanation?: string | null | undefined;
  hintsUsedCount: number;
  availableHintsCount: number;
  onRetry: () => void;
  onRequestHint: () => void;
}

/**
 * Bloc feedback post-soumission : succès ou erreur, explication, growth mindset,
 * bouton hint si disponible, et actions (retry / next challenge).
 *
 * Rendu conditionnel géré par le parent (affiché uniquement si hasSubmitted=true).
 */
export function ChallengeSolverFeedback({
  isCorrect,
  pointsEarned,
  solutionExplanation,
  hintsUsedCount,
  availableHintsCount,
  onRetry,
  onRequestHint,
}: ChallengeSolverFeedbackProps) {
  const t = useTranslations("challenges.solver");

  return (
    <>
      {/* Feedback */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className={cn(
          "mt-6 rounded-xl p-4 border",
          isCorrect
            ? "bg-emerald-500/10 border-emerald-500/30 feedback-success-animate"
            : "bg-red-500/10 border-red-500/30 feedback-error-animate"
        )}
      >
        <div className="flex items-start gap-4">
          {isCorrect ? (
            <CheckCircle className="h-8 w-8 text-emerald-400 flex-shrink-0 mt-1" />
          ) : (
            <XCircle className="h-8 w-8 text-red-400 flex-shrink-0 mt-1" />
          )}
          <div className="flex-1 space-y-2">
            <h3
              className={cn(
                "text-lg font-semibold",
                isCorrect ? "text-emerald-400" : "text-red-400"
              )}
            >
              {isCorrect ? t("correctTitle") : t("incorrectTitle")}
            </h3>

            {isCorrect && typeof pointsEarned === "number" && pointsEarned > 0 && (
              <p
                className="text-sm font-medium text-emerald-500/95"
                data-testid="challenge-points-earned"
              >
                {t("pointsEarned", { count: pointsEarned })}
              </p>
            )}

            {isCorrect && solutionExplanation && (
              <div className="mt-4">
                <p className="font-medium text-foreground mb-2">{t("explanationLabel")}</p>
                <MathText size="base" className="text-muted-foreground">
                  {solutionExplanation}
                </MathText>
              </div>
            )}

            {!isCorrect && (
              <div className="mt-4">
                <GrowthMindsetHint
                  className="text-muted-foreground mb-3"
                  supportText={t("tryAgain")}
                  strategyText={t("tryAgainStrategy")}
                />
                {availableHintsCount > hintsUsedCount && (
                  <Button
                    onClick={onRequestHint}
                    variant="outline"
                    size="sm"
                    className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
                    aria-label={t("requestHint", {
                      current: hintsUsedCount + 1,
                      total: availableHintsCount,
                    })}
                  >
                    <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
                    {t("seeNextHint")}
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Actions post-soumission */}
      <div className="flex gap-3 pt-8 mt-8 border-t border-border">
        {!isCorrect && (
          <Button
            onClick={onRetry}
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
            aria-label={t("retryLabel")}
          >
            <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
            {t("retry")}
          </Button>
        )}
        {isCorrect && (
          <Button
            asChild
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
          >
            <Link href="/challenges">{t("nextChallenge")}</Link>
          </Button>
        )}
      </div>
    </>
  );
}
