"use client";

import { useEffect, useRef, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useIrtScores } from "@/hooks/useIrtScores";
import { useTranslations } from "next-intl";
import { Loader2, CheckCircle2, XCircle, Lightbulb, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { MathText } from "@/components/ui/MathText";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import { ExerciseSolverHint } from "@/components/exercises/ExerciseSolverHint";

interface ExerciseModalProps {
  exerciseId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExerciseCompleted?: () => void;
}

interface ExerciseModalContentProps {
  exerciseId: number;
  onOpenChange: (open: boolean) => void;
  onExerciseCompleted?: (() => void) | undefined;
}

function ExerciseModalContent({
  exerciseId,
  onOpenChange,
  onExerciseCompleted,
}: ExerciseModalContentProps) {
  const { exercise, isLoading, error } = useExercise(exerciseId);
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { resolveIsOpenAnswer } = useIrtScores();
  const t = useTranslations("exercises.modal");
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const startTimeRef = useRef<number>(0);

  const hasSubmitted = Boolean(submitResult);
  const showExplanation = hasSubmitted;

  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  useEffect(() => {
    if (!submitResult?.is_correct) {
      return;
    }

    const timer = window.setTimeout(() => {
      onExerciseCompleted?.();
    }, 3000);

    return () => clearTimeout(timer);
  }, [submitResult?.is_correct, onExerciseCompleted]);

  const isOpenAnswer = exercise ? resolveIsOpenAnswer(exercise.exercise_type) : false;

  const handleSelectAnswer = (answer: string) => {
    if (hasSubmitted) return;
    setSelectedAnswer(answer);
  };

  const handleSubmit = async () => {
    if (!selectedAnswer || !exercise || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000;

    try {
      await submitAnswer({
        exercise_id: exercise.id,
        answer: selectedAnswer,
        time_spent: timeSpent,
      });
    } catch {
      // L'erreur est déjà gérée par le hook useSubmitAnswer
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onOpenChange(false);
    }
  };

  const typeDisplay = getTypeDisplay(exercise?.exercise_type);
  const ageGroupDisplay = getAgeDisplay(exercise?.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = exercise?.choices && exercise.choices.length > 0 ? exercise.choices : [];

  return (
    <DialogContent
      showCloseButton={false}
      aria-describedby={undefined}
      className="w-full max-w-[calc(100%-2rem)] md:max-w-3xl lg:max-w-4xl max-h-[90vh] p-0 gap-0 bg-[var(--bg-learner,var(--card))] border border-border/40 shadow-none rounded-2xl overflow-hidden"
      onPointerDownOutside={() => !isSubmitting && handleClose()}
    >
      {/* Contenu : stopPropagation pour éviter fermeture au clic dedans */}
      <div
        data-learner-context
        className="p-6 md:p-8 overflow-y-auto max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
        onPointerDown={(e) => e.stopPropagation()}
      >
        {/* En-tête : Titre + badges à gauche, bouton X à droite (flex, pas absolute) */}
        <div className="flex items-start justify-between gap-4 mb-2">
          <DialogHeader className="flex-1 min-w-0 p-0">
            {isLoading ? (
              <DialogTitle>{t("loading")}</DialogTitle>
            ) : error ? (
              <DialogTitle>{t("errorTitle")}</DialogTitle>
            ) : exercise ? (
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <DialogTitle className="text-xl md:text-2xl font-bold text-foreground">
                  {exercise.title}
                </DialogTitle>
                {ageGroupDisplay && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-muted/50 text-muted-foreground border border-border/50">
                    {ageGroupDisplay}
                  </span>
                )}
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-muted/50 text-muted-foreground border border-border/50">
                  {typeDisplay}
                </span>
              </div>
            ) : (
              <DialogTitle>Exercice</DialogTitle>
            )}
          </DialogHeader>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              handleClose();
            }}
            className="flex-shrink-0 p-2 rounded-full hover:bg-accent text-muted-foreground hover:text-foreground transition-colors z-50"
            aria-label={t("close", { default: "Fermer" })}
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center min-h-[300px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
              <p className="text-muted-foreground">{t("loading")}</p>
            </div>
          </div>
        ) : error ? (
          <div className="text-center space-y-4 py-8">
            <XCircle className="h-12 w-12 text-destructive mx-auto" />
            <div>
              <p className="text-muted-foreground mt-2">
                {error.status === 404 ? t("notFound") : error.message || t("loadError")}
              </p>
            </div>
          </div>
        ) : exercise ? (
          <>
            {/* Question — scroll conditionnel si très long */}
            {(() => {
              const question = exercise.question ?? "";
              const isLongText = question.length > 80;
              const isVeryLongText = question.length > 250;
              return (
                <div
                  className={cn(
                    "py-6 md:py-8 mb-8",
                    isVeryLongText && "max-h-[40vh] overflow-y-auto pr-2 modal-scrollbar"
                  )}
                >
                  <MathText
                    size="lg"
                    className={cn(
                      "font-normal text-lg text-foreground/85 leading-relaxed",
                      isLongText ? "text-left" : "text-center"
                    )}
                  >
                    {question}
                  </MathText>
                </div>
              );
            })()}
            {/* U2 — Aide de première visite : même clé localStorage que ExerciseSolver.
                Un enfant qui a déjà vu le hint dans le solver full-page ne le revoit pas ici. */}
            {!hasSubmitted && (
              <ExerciseSolverHint isOpenAnswer={isOpenAnswer} hasHint={!!exercise.hint} />
            )}

            {/* NI-10 — Indice avant les choix : visible sans scroll sur mobile.
                W3C COGA 2.2 : un enfant bloqué ne scroll pas pour chercher de l'aide. */}
            {!hasSubmitted && exercise.hint && !showHint && (
              <div className="flex justify-end pt-4 pb-1">
                <button
                  type="button"
                  onClick={() => setShowHint(true)}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={t("showHint")}
                >
                  <Lightbulb className="h-3.5 w-3.5" aria-hidden="true" />
                  {t("showHint")}
                </button>
              </div>
            )}

            <div className="space-y-3 pt-6 pb-4">
              {isOpenAnswer ? (
                <div className="space-y-2">
                  <label
                    htmlFor="modal-open-answer-input"
                    className="block text-sm font-medium text-muted-foreground mb-2"
                  >
                    {t("openAnswerLabel", { default: "Votre réponse" })}
                  </label>
                  <input
                    id="modal-open-answer-input"
                    type="text"
                    value={selectedAnswer ?? ""}
                    onChange={(e) => !hasSubmitted && setSelectedAnswer(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && selectedAnswer?.trim() && !hasSubmitted)
                        void handleSubmit();
                    }}
                    disabled={hasSubmitted}
                    autoFocus
                    className={cn(
                      "w-full rounded-2xl py-5 px-6 text-2xl font-medium text-foreground bg-secondary/50 border-2 border-border",
                      "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all",
                      "placeholder:text-muted-foreground",
                      hasSubmitted && "opacity-70 cursor-not-allowed",
                      hasSubmitted &&
                        submitResult?.is_correct &&
                        "border-emerald-500 bg-emerald-500/10 text-emerald-400",
                      hasSubmitted &&
                        !submitResult?.is_correct &&
                        "border-red-500 bg-red-500/10 text-red-400"
                    )}
                    placeholder={t("openAnswerPlaceholder", { default: "Entrez votre réponse…" })}
                    aria-label={t("openAnswerLabel", { default: "Votre réponse" })}
                  />
                </div>
              ) : choices.length > 0 ? (
                <div
                  className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-4"
                  role="radiogroup"
                  aria-label={t("answerChoicesLabel")}
                >
                  {choices.map((choice, index) => {
                    const isSelected = selectedAnswer === choice;
                    const isCorrectChoice =
                      hasSubmitted && submitResult?.correct_answer
                        ? choice === submitResult.correct_answer
                        : false;
                    const showCorrect = hasSubmitted && isCorrectChoice;
                    const showIncorrect = hasSubmitted && isSelected && !isCorrectChoice;

                    return (
                      <button
                        key={index}
                        type="button"
                        className={cn(
                          "rounded-2xl py-6 md:py-7 text-2xl font-medium text-foreground cursor-pointer transition-colors text-center border-2",
                          !hasSubmitted &&
                            !showCorrect &&
                            !showIncorrect &&
                            (isSelected
                              ? "border-primary bg-primary/20"
                              : "bg-secondary/50 border-border hover:bg-secondary hover:border-primary/50"),
                          showCorrect &&
                            "bg-emerald-500/20 border-emerald-500 text-emerald-400 hover:bg-emerald-500/20",
                          showIncorrect &&
                            "bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20",
                          hasSubmitted && !isSelected && !isCorrectChoice && "opacity-50"
                        )}
                        onClick={() => handleSelectAnswer(choice)}
                        disabled={hasSubmitted}
                        role="radio"
                        aria-checked={isSelected ? "true" : "false"}
                        aria-label={`Option ${index + 1}: ${choice}${hasSubmitted ? (isCorrectChoice ? ` - ${t("correctAnswer")}` : showIncorrect ? ` - ${t("incorrectAnswer")}` : "") : ""}`}
                        tabIndex={hasSubmitted ? -1 : isSelected || index === 0 ? 0 : -1}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            handleSelectAnswer(choice);
                          }
                          if (e.key === "ArrowRight" && index < choices.length - 1) {
                            e.preventDefault();
                            const next = e.currentTarget.parentElement?.children[
                              index + 1
                            ] as HTMLElement;
                            next?.focus();
                          }
                          if (e.key === "ArrowLeft" && index > 0) {
                            e.preventDefault();
                            const prev = e.currentTarget.parentElement?.children[
                              index - 1
                            ] as HTMLElement;
                            prev?.focus();
                          }
                        }}
                      >
                        <MathText size="base">{choice}</MathText>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="p-4 border rounded-lg bg-muted/50">
                  <p className="text-muted-foreground text-sm">{t("noMultipleChoice")}</p>
                </div>
              )}

              {!hasSubmitted && (
                <div className="space-y-2">
                  <Button
                    onClick={handleSubmit}
                    disabled={!selectedAnswer?.trim() || isSubmitting}
                    className={cn(
                      "w-full size-lg font-semibold transition-all",
                      !selectedAnswer?.trim() &&
                        "bg-muted text-muted-foreground opacity-60 cursor-not-allowed border border-border",
                      selectedAnswer?.trim() &&
                        "bg-primary text-primary-foreground hover:bg-primary/90"
                    )}
                    size="lg"
                    aria-label={isSubmitting ? t("saving") : t("validateAnswer")}
                    aria-busy={isSubmitting}
                    aria-describedby={!selectedAnswer?.trim() ? "modal-validate-hint" : undefined}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        {t("saving")}
                      </>
                    ) : (
                      t("validateAnswer")
                    )}
                  </Button>
                  {!selectedAnswer?.trim() && (
                    <p
                      id="modal-validate-hint"
                      className="text-center text-xs text-muted-foreground"
                      aria-live="polite"
                    >
                      {isOpenAnswer
                        ? t("validateHintOpen", { default: "Écris ta réponse pour continuer" })
                        : t("validateHintMcq", { default: "Choisis une réponse pour continuer" })}
                    </p>
                  )}
                </div>
              )}

              {hasSubmitted && submitResult && (
                <div
                  className={cn(
                    "p-4 rounded-lg border transition-all",
                    isCorrect
                      ? "bg-success/10 border-success/20 text-success"
                      : "bg-destructive/10 border-destructive/20 text-destructive"
                  )}
                >
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle2 className="h-6 w-6 mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="h-6 w-6 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="font-semibold mb-1">
                        {isCorrect ? t("correctTitle") : t("incorrectTitle")}
                      </p>
                      {!isCorrect && (
                        <GrowthMindsetHint
                          supportText={t("incorrectSupport")}
                          correctAnswerLabel={t("correctAnswerWas")}
                          correctAnswer={submitResult.correct_answer}
                        />
                      )}
                    </div>
                  </div>
                </div>
              )}

              {showExplanation && (exercise.explanation || submitResult?.explanation) && (
                <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground mb-2">{t("explanation")}</h4>
                      <MathText size="sm" className="text-foreground leading-relaxed">
                        {submitResult?.explanation || exercise.explanation || ""}
                      </MathText>
                    </div>
                  </div>
                </div>
              )}

              {showHint && exercise.hint && (
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="h-5 w-5 text-warning mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-warning mb-1">{t("hint")}</h4>
                      <MathText size="sm" className="text-foreground">
                        {exercise.hint}
                      </MathText>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : null}
      </div>
    </DialogContent>
  );
}

export function ExerciseModal({
  exerciseId,
  open,
  onOpenChange,
  onExerciseCompleted,
}: ExerciseModalProps) {
  if (!exerciseId) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onOpenChange(false)}>
      {open ? (
        <ExerciseModalContent
          key={exerciseId}
          exerciseId={exerciseId}
          onOpenChange={onOpenChange}
          onExerciseCompleted={onExerciseCompleted}
        />
      ) : null}
    </Dialog>
  );
}
