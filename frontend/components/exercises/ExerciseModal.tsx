"use client";

import { useState, useEffect, useRef } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useIrtScores } from "@/hooks/useIrtScores";
import { useTranslations } from "next-intl";
import { Loader2, CheckCircle2, XCircle, Lightbulb, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQueryClient } from "@tanstack/react-query";
import { MathText } from "@/components/ui/MathText";

interface ExerciseModalProps {
  exerciseId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExerciseCompleted?: () => void;
}

export function ExerciseModal({
  exerciseId,
  open,
  onOpenChange,
  onExerciseCompleted,
}: ExerciseModalProps) {
  const queryClient = useQueryClient();
  const { exercise, isLoading, error } = useExercise(exerciseId || 0);
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { resolveIsOpenAnswer } = useIrtScores();
  const t = useTranslations("exercises.modal");
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const startTimeRef = useRef<number>(0);

  // Réinitialiser l'état quand la modal s'ouvre ou l'exercice change
  useEffect(() => {
    if (open && exerciseId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSelectedAnswer(null);
      setHasSubmitted(false);
      setShowExplanation(false);
      setShowHint(false);
      startTimeRef.current = Date.now();
    }
  }, [open, exerciseId]);

  // Mettre à jour l'état quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHasSubmitted(true);
      setShowExplanation(true);

      // Si l'exercice est complété avec succès, invalider la progression (badge "Résolu").
      // Ne PAS invalider ["exercises"] pour éviter le reshuffle de l'ordre aléatoire.
      if (submitResult.is_correct) {
        queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
        queryClient.refetchQueries({ queryKey: ["completed-exercises"] });
      }
    }
  }, [submitResult, queryClient]);

  // Notifier le parent si l'exercice est complété (réponse correcte uniquement)
  useEffect(() => {
    if (hasSubmitted && submitResult?.is_correct) {
      const timer = setTimeout(() => {
        if (onExerciseCompleted) {
          onExerciseCompleted();
        }
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [hasSubmitted, submitResult, onExerciseCompleted]);

  // Mode de réponse résolu depuis les scores IRT par type (F03+F05) — pas depuis
  // le flag is_open_answer du générateur. QCM conservé pour les niveaux < GRAND_MAITRE.
  const isOpenAnswer = exercise ? resolveIsOpenAnswer(exercise.exercise_type) : false;

  const handleSelectAnswer = (answer: string) => {
    if (hasSubmitted) return;
    setSelectedAnswer(answer);
  };

  const handleSubmit = async () => {
    if (!selectedAnswer || !exercise || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000; // en secondes

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
      // Réinitialiser l'état après fermeture
      setTimeout(() => {
        setSelectedAnswer(null);
        setHasSubmitted(false);
        setShowExplanation(false);
      }, 200);
    }
  };

  if (!exerciseId) {
    return null;
  }

  const typeDisplay = getTypeDisplay(exercise?.exercise_type);
  const ageGroupDisplay = getAgeDisplay(exercise?.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = exercise?.choices && exercise.choices.length > 0 ? exercise.choices : [];

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && !isSubmitting && handleClose()}>
      <DialogContent
        showCloseButton={false}
        className="max-w-3xl max-h-[90vh] p-0 gap-0 bg-card/95 backdrop-blur-xl border border-border shadow-2xl rounded-2xl overflow-hidden"
        onPointerDownOutside={() => !isSubmitting && handleClose()}
      >
        {/* Contenu : stopPropagation pour éviter fermeture au clic dedans */}
        <div
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
                <div className="flex flex-wrap items-center gap-2">
                  <DialogTitle className="text-xl">{exercise.title}</DialogTitle>
                  {ageGroupDisplay && <Badge variant="outline">{ageGroupDisplay}</Badge>}
                  <Badge variant="outline">{typeDisplay}</Badge>
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
              {/* Énoncé — typographie dynamique selon la longueur */}
              {(() => {
                const question = exercise.question ?? "";
                const isLongText = question.length > 80;
                const isVeryLongText = question.length > 250;
                return (
                  <div
                    className={cn(
                      "py-6 md:py-8 mb-8",
                      isVeryLongText && "max-h-[40vh] overflow-y-auto pr-2 custom-scrollbar"
                    )}
                  >
                    <MathText
                      size={isLongText ? "lg" : "xl"}
                      className={cn(
                        isLongText
                          ? "font-normal text-left text-muted-foreground"
                          : "font-bold text-center text-foreground"
                      )}
                    >
                      {question}
                    </MathText>
                  </div>
                );
              })()}
              <div className="space-y-6 pt-6 pb-4">
                {/* Zone de réponse — QCM ou saisie libre selon is_open_answer */}
                {isOpenAnswer ? (
                  <div className="space-y-2">
                    <label
                      htmlFor="modal-open-answer-input"
                      className="block text-sm font-medium text-muted-foreground"
                    >
                      {t("openAnswerLabel", { default: "Votre réponse" })}
                    </label>
                    <input
                      id="modal-open-answer-input"
                      type="text"
                      value={selectedAnswer ?? ""}
                      onChange={(e) => !hasSubmitted && setSelectedAnswer(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && selectedAnswer && !hasSubmitted) handleSubmit();
                      }}
                      disabled={hasSubmitted}
                      autoFocus
                      className={cn(
                        "w-full rounded-xl py-4 px-5 text-xl font-medium text-foreground bg-secondary/50 border-2 border-border",
                        "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all",
                        hasSubmitted && "opacity-70 cursor-not-allowed",
                        hasSubmitted &&
                          submitResult?.is_correct &&
                          "border-green-500 bg-green-500/10 text-green-400",
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
                    className="grid grid-cols-2 gap-3"
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
                            "h-auto py-4 px-6 text-xl font-medium transition-all duration-200 rounded-xl text-left",
                            "border-2",
                            !hasSubmitted &&
                              !showCorrect &&
                              !showIncorrect &&
                              (isSelected
                                ? "border-primary bg-primary/20 text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.3)]"
                                : "bg-secondary/50 border-border hover:bg-secondary hover:border-primary/50 hover:-translate-y-1"),
                            showCorrect &&
                              "bg-green-500/20 border-green-500 text-green-400 hover:bg-green-500/20",
                            showIncorrect &&
                              "bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20",
                            hasSubmitted && !isSelected && !isCorrectChoice && "opacity-50"
                          )}
                          onClick={() => handleSelectAnswer(choice)}
                          disabled={hasSubmitted}
                          role="radio"
                          aria-checked={isSelected ? "true" : "false"}
                          aria-label={`Option ${index + 1}: ${choice}${hasSubmitted ? (isCorrectChoice ? ` - ${t("correctAnswer")}` : showIncorrect ? ` - ${t("incorrectAnswer")}` : "") : ""}`}
                          tabIndex={hasSubmitted ? -1 : isSelected ? 0 : -1}
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

                {/* Bouton Valider — actif uniquement si une réponse est sélectionnée */}
                {!hasSubmitted && (
                  <Button
                    onClick={handleSubmit}
                    disabled={!selectedAnswer || isSubmitting}
                    className={cn(
                      "w-full size-lg transition-all",
                      !selectedAnswer && "opacity-50 cursor-not-allowed",
                      selectedAnswer &&
                        "bg-primary text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.35)] hover:shadow-[0_0_20px_hsl(var(--primary)/0.5)]"
                    )}
                    size="lg"
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
                )}

                {/* Feedback après soumission */}
                {hasSubmitted && submitResult && (
                  <div
                    className={cn(
                      "p-4 rounded-lg border-2 transition-all",
                      isCorrect
                        ? "bg-green-500/10 border-green-500/30 text-green-400"
                        : "bg-red-500/10 border-red-500/30 text-red-400"
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
                          <p className="text-sm opacity-90">
                            {t("correctAnswerWas")} <strong>{submitResult.correct_answer}</strong>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Explication */}
                {showExplanation && (exercise.explanation || submitResult?.explanation) && (
                  <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="h-5 w-5 text-primary-on-dark mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-primary-on-dark mb-2">
                          {t("explanation")}
                        </h4>
                        <MathText size="sm" className="text-text-secondary">
                          {submitResult?.explanation || exercise.explanation || ""}
                        </MathText>
                      </div>
                    </div>
                  </div>
                )}

                {/* Indice (si disponible et pas encore soumis) */}
                {!hasSubmitted && exercise.hint && !showHint && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowHint(true)}
                    className="w-full"
                  >
                    <Lightbulb className="mr-2 h-4 w-4" />
                    {t("showHint")}
                  </Button>
                )}
                {showHint && exercise.hint && (
                  <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-yellow-400 mb-1">{t("hint")}</h4>
                        <MathText size="sm" className="text-text-secondary">
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
    </Dialog>
  );
}
