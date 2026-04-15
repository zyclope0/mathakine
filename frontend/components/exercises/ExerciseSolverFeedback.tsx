"use client";

import { CheckCircle2, XCircle, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";
import { MathText } from "@/components/ui/MathText";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import type { SessionMode } from "@/lib/exercises/exerciseSolverSession";

interface ExerciseSolverFeedbackProps {
  hasSubmitted: boolean;
  /** `null` until the API result arrives. */
  submitResultPresent: boolean;
  isCorrect: boolean;
  correctAnswer: string;
  explanationText: string;
  showExplanation: boolean;
  /** Hint to show (from non-review mode). */
  hint: string | null | undefined;
  showHint: boolean;
  sessionMode: SessionMode;
  labels: {
    correctTitle: string;
    incorrectTitle: string;
    incorrectSupport: string;
    correctAnswerWas: string;
    explanation: string;
    hint: string;
  };
}

export function ExerciseSolverFeedback({
  hasSubmitted,
  submitResultPresent,
  isCorrect,
  correctAnswer,
  explanationText,
  showExplanation,
  hint,
  showHint,
  sessionMode,
  labels,
}: ExerciseSolverFeedbackProps) {
  return (
    <>
      {/* Feedback après soumission */}
      {hasSubmitted && submitResultPresent && (
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className={cn(
            "rounded-xl p-4 font-semibold text-lg flex items-center gap-3 transition-all mt-8",
            isCorrect
              ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 feedback-success-animate"
              : "bg-red-500/10 border-2 border-red-500/30 text-red-400 feedback-error-animate"
          )}
        >
          {isCorrect ? (
            <CheckCircle2 className="h-6 w-6 flex-shrink-0" />
          ) : (
            <XCircle className="h-6 w-6 flex-shrink-0" />
          )}
          <div className="flex-1">
            <p className={isCorrect ? "mb-0" : "mb-1"}>
              {isCorrect ? labels.correctTitle : labels.incorrectTitle}
            </p>
            {!isCorrect && (
              <GrowthMindsetHint
                supportText={labels.incorrectSupport}
                correctAnswerLabel={labels.correctAnswerWas}
                correctAnswer={correctAnswer}
              />
            )}
          </div>
        </div>
      )}

      {/* Explication — Fiche de savoir */}
      {showExplanation && explanationText && (
        <div className="bg-primary/5 border border-primary/30 rounded-xl p-5 mt-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-primary mb-2">{labels.explanation}</h4>
              <MathText size="lg" className="text-foreground">
                {explanationText}
              </MathText>
            </div>
          </div>
        </div>
      )}

      {showHint && hint && sessionMode !== "spaced-review" && (
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 mt-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-yellow-400 mb-1">{labels.hint}</h4>
              <MathText size="sm" className="text-muted-foreground">
                {hint}
              </MathText>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
