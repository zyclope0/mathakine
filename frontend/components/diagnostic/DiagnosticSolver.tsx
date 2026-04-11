"use client";

/**
 * Façade diagnostic adaptatif (F03) — affichage par phase.
 * Logique métier : `useDiagnostic`. Sous-vues : `Diagnostic*State` + primitives partagées.
 */

import { useDiagnostic } from "@/hooks/useDiagnostic";
import { DiagnosticIdleState } from "@/components/diagnostic/DiagnosticIdleState";
import { DiagnosticLoadingState } from "@/components/diagnostic/DiagnosticLoadingState";
import { DiagnosticErrorState } from "@/components/diagnostic/DiagnosticErrorState";
import { DiagnosticResultsState } from "@/components/diagnostic/DiagnosticResultsState";
import { DiagnosticQuestionState } from "@/components/diagnostic/DiagnosticQuestionState";

export interface DiagnosticSolverProps {
  triggeredFrom?: "onboarding" | "settings";
  /** Appelé après finalisation réussie pour permettre la redirection parente */
  onComplete?: () => void;
}

export function DiagnosticSolver({
  triggeredFrom = "onboarding",
  onComplete,
}: DiagnosticSolverProps) {
  const {
    phase,
    currentQuestion,
    selectedAnswer,
    isCorrect,
    correctAnswerForFeedback,
    result,
    error,
    startDiagnostic,
    setSelectedAnswer,
    submitAnswer,
    nextQuestion,
  } = useDiagnostic(triggeredFrom);

  if (phase === "idle") {
    return <DiagnosticIdleState onStart={startDiagnostic} />;
  }

  if (phase === "loading") {
    return <DiagnosticLoadingState />;
  }

  if (phase === "error") {
    return <DiagnosticErrorState error={error} onRetry={startDiagnostic} />;
  }

  if (phase === "results" && result) {
    return onComplete ? (
      <DiagnosticResultsState result={result} onComplete={onComplete} />
    ) : (
      <DiagnosticResultsState result={result} />
    );
  }

  if (!currentQuestion) {
    return null;
  }

  return (
    <DiagnosticQuestionState
      phase={phase}
      currentQuestion={currentQuestion}
      selectedAnswer={selectedAnswer}
      isCorrect={isCorrect}
      correctAnswerForFeedback={correctAnswerForFeedback}
      setSelectedAnswer={setSelectedAnswer}
      submitAnswer={submitAnswer}
      nextQuestion={nextQuestion}
    />
  );
}
