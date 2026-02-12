"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { Loader2, CheckCircle2, XCircle, Lightbulb, ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";

interface ExerciseSolverProps {
  exerciseId: number;
}

export function ExerciseSolver({ exerciseId }: ExerciseSolverProps) {
  const router = useRouter();
  const t = useTranslations("exercises.solver");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { exercise, isLoading, error } = useExercise(exerciseId);
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const startTimeRef = useRef<number>(Date.now());

  // Mettre à jour l'état quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      setShowExplanation(true);
    }
  }, [submitResult]);

  // Réinitialiser l'état quand l'exercice change
  useEffect(() => {
    if (exercise) {
      setSelectedAnswer(null);
      setHasSubmitted(false);
      setShowExplanation(false);
      startTimeRef.current = Date.now();
    }
  }, [exercise?.id]);

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
      // L'état sera mis à jour via useEffect quand submitResult change
    } catch (error) {
      // L'erreur est déjà gérée par le hook useSubmitAnswer
      // Ne pas logger en production pour éviter les fuites d'information
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">{t("loading")}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <div className="text-center space-y-4" role="alert" aria-live="assertive">
            <XCircle className="h-12 w-12 text-destructive mx-auto" />
            <div>
              <h3 className="text-lg font-semibold text-destructive">{t("error.title")}</h3>
              <p className="text-muted-foreground mt-2">
                {error.status === 404 ? t("error.notFound") : error.message || t("error.generic")}
              </p>
            </div>
            <Button asChild variant="outline">
              <Link href="/exercises">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {t("backToExercises")}
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!exercise) {
    return null;
  }

  const typeDisplay = getTypeDisplay(exercise.exercise_type);
  const ageGroupDisplay = getAgeDisplay(exercise.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = exercise.choices && exercise.choices.length > 0 ? exercise.choices : [];

  return (
    <div className="space-y-6">
      {/* En-tête avec badges */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/exercises">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
          <div className="flex gap-2">
            <Badge variant="outline">{ageGroupDisplay}</Badge>
            <Badge variant="outline">{typeDisplay}</Badge>
          </div>
        </div>
      </div>

      {/* Carte principale de l'exercice */}
      <Card className="bg-surface-elevated border-primary/20 shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl">{exercise.title}</CardTitle>
          <CardDescription className="text-base mt-2">{exercise.question}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Choix de réponses */}
          {choices.length > 0 ? (
            <div
              className="grid grid-cols-2 gap-3"
              role="radiogroup"
              aria-label="Choix de réponses pour l'exercice"
            >
              {choices.map((choice, index) => {
                const isSelected = selectedAnswer === choice;
                const isCorrectChoice = choice === exercise.correct_answer;
                const showCorrect = hasSubmitted && isCorrectChoice;
                const showIncorrect = hasSubmitted && isSelected && !isCorrectChoice;

                return (
                  <Button
                    key={index}
                    variant={isSelected ? "default" : "outline"}
                    size="lg"
                    className={cn(
                      "h-auto py-4 px-6 text-lg font-medium transition-all",
                      !hasSubmitted && "hover:bg-primary/10 hover:border-primary/50",
                      showCorrect &&
                        "bg-green-500/20 border-green-500 text-green-400 hover:bg-green-500/20",
                      showIncorrect &&
                        "bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20",
                      hasSubmitted && !isSelected && !isCorrectChoice && "opacity-50"
                    )}
                    onClick={() => handleSelectAnswer(choice)}
                    disabled={hasSubmitted}
                    role="radio"
                    aria-checked={isSelected}
                    aria-label={`${t("option", { index: index + 1 })}: ${choice}${hasSubmitted ? (isCorrectChoice ? ` - ${t("answerCorrect")}` : showIncorrect ? ` - ${t("answerIncorrect")}` : "") : ""}`}
                    tabIndex={isSelected ? 0 : -1}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleSelectAnswer(choice);
                      }
                      // Navigation par flèches
                      if (e.key === "ArrowRight" && index < choices.length - 1) {
                        e.preventDefault();
                        const nextButton = e.currentTarget.parentElement?.children[
                          index + 1
                        ] as HTMLElement;
                        nextButton?.focus();
                      }
                      if (e.key === "ArrowLeft" && index > 0) {
                        e.preventDefault();
                        const prevButton = e.currentTarget.parentElement?.children[
                          index - 1
                        ] as HTMLElement;
                        prevButton?.focus();
                      }
                    }}
                  >
                    {choice}
                  </Button>
                );
              })}
            </div>
          ) : (
            <div className="p-4 border rounded-lg bg-muted/50">
              <p className="text-muted-foreground text-sm">
                {t("noChoices")} <strong>{exercise.correct_answer}</strong>
              </p>
            </div>
          )}

          {/* Bouton de soumission */}
          {!hasSubmitted && (
            <Button
              onClick={handleSubmit}
              disabled={!selectedAnswer || isSubmitting}
              className="w-full"
              size="lg"
              aria-label={isSubmitting ? t("validating") : t("validateAnswer")}
              aria-busy={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  {t("saving")}
                </>
              ) : (
                t("validateMyAnswer")
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
                  <h4 className="font-semibold text-primary-on-dark mb-2">{t("explanation")}</h4>
                  <p className="text-sm text-text-secondary">
                    {submitResult?.explanation || exercise.explanation}
                  </p>
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
              aria-label={t("hint")}
            >
              <Lightbulb className="mr-2 h-4 w-4" />
              {t("hint")}
            </Button>
          )}
          {showHint && exercise.hint && (
            <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
              <div className="flex items-start gap-3">
                <Lightbulb className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="font-semibold text-yellow-400 mb-1">{t("hint")}</h4>
                  <p className="text-sm text-muted-foreground">{exercise.hint}</p>
                </div>
              </div>
            </div>
          )}

          {/* Actions après soumission */}
          {hasSubmitted && (
            <div className="flex gap-3 pt-4 border-t">
              <Button variant="outline" asChild className="flex-1">
                <Link href="/exercises">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t("backToExercises")}
                </Link>
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  // Rediriger vers la liste des exercices pour choisir un nouvel exercice
                  router.push("/exercises");
                }}
                className="flex-1"
                aria-label={t("newExercise")}
              >
                <ArrowRight className="mr-2 h-4 w-4" />
                {t("newExercise")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
