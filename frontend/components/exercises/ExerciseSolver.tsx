"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useIrtScores } from "@/hooks/useIrtScores";
import { Loader2, CheckCircle2, XCircle, Lightbulb, ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { MathText } from "@/components/ui/MathText";

interface ExerciseSolverProps {
  exerciseId: number;
}

export function ExerciseSolver({ exerciseId }: ExerciseSolverProps) {
  const router = useRouter();
  const t = useTranslations("exercises.solver");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { exercise, isLoading, error } = useExercise(exerciseId);
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const { resolveIsOpenAnswer } = useIrtScores();
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const startTimeRef = useRef<number>(0);
  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exercise?.id]);

  // Le mode de réponse est résolu depuis les scores IRT de l'utilisateur (F03+F05),
  // pas depuis le flag is_open_answer du générateur. Cela permet au backend de
  // toujours générer les choices, et au frontend de décider selon le niveau réel
  // par type (QCM pour les niveaux inférieurs, saisie libre à GRAND_MAITRE IRT).
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

  // Conteneur Focus Board (glassmorphism) — utilisé pour loading, error et contenu
  const FocusBoard = ({
    children,
    className = "",
  }: {
    children: React.ReactNode;
    className?: string;
  }) => (
    <div
      className={cn(
        "bg-card/90 backdrop-blur-xl border border-border shadow-[0_0_40px_rgba(0,0,0,0.15)] rounded-3xl p-8 md:p-12 w-full max-w-4xl mx-auto mt-8 md:mt-12",
        className
      )}
    >
      {children}
    </div>
  );

  if (isLoading) {
    return (
      <FocusBoard>
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("loading")}</p>
          </div>
        </div>
      </FocusBoard>
    );
  }

  if (error) {
    return (
      <FocusBoard>
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
      </FocusBoard>
    );
  }

  if (!exercise) {
    return null;
  }

  const typeDisplay = getTypeDisplay(exercise.exercise_type);
  const ageGroupDisplay = getAgeDisplay(exercise.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = exercise.choices && exercise.choices.length > 0 ? exercise.choices : [];
  const isCorrectChoice = (choice: string) =>
    hasSubmitted && submitResult?.correct_answer ? choice === submitResult.correct_answer : false;

  return (
    <FocusBoard>
      {/* Bouton Retour — en haut à gauche, discret */}
      <Link
        href="/exercises"
        className="text-muted-foreground hover:text-foreground transition-colors mb-6 inline-flex items-center gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("back")}
      </Link>

      {/* Tags centrés au-dessus du titre */}
      <div className="flex justify-center gap-2 mb-4">
        {ageGroupDisplay && <Badge variant="outline">{ageGroupDisplay}</Badge>}
        <Badge variant="outline">{typeDisplay}</Badge>
      </div>

      {/* Titre centré */}
      <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-8 text-center">
        {exercise.title}
      </h1>

      {/* Énoncé — la star de la page */}
      <div className="text-xl md:text-2xl font-medium text-foreground text-center mb-12 leading-relaxed">
        <MathText size="xl">{exercise.question}</MathText>
      </div>

      {/* Zone de réponse — QCM ou saisie libre selon is_open_answer */}
      {isOpenAnswer ? (
        <div className="mb-8 space-y-3">
          <label
            htmlFor="open-answer-input"
            className="block text-sm font-medium text-muted-foreground"
          >
            {t("openAnswerLabel", { default: "Votre réponse" })}
          </label>
          <input
            id="open-answer-input"
            type="text"
            value={selectedAnswer ?? ""}
            onChange={(e) => !hasSubmitted && setSelectedAnswer(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && selectedAnswer && !hasSubmitted) handleSubmit();
            }}
            disabled={hasSubmitted}
            autoFocus
            className={cn(
              "w-full rounded-2xl py-5 px-6 text-2xl font-medium text-foreground bg-secondary/50 border-2 border-border",
              "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all",
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
          className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8"
          role="radiogroup"
          aria-label="Choix de réponses pour l'exercice"
        >
          {choices.map((choice, index) => {
            const isSelected = selectedAnswer === choice;
            const showCorrect = hasSubmitted && isCorrectChoice(choice);
            const showIncorrect = hasSubmitted && isSelected && !isCorrectChoice(choice);

            return (
              <button
                key={index}
                type="button"
                className={cn(
                  "rounded-2xl py-6 md:py-8 text-2xl font-medium text-foreground cursor-pointer transition-all text-center border-2",
                  !hasSubmitted &&
                    !showCorrect &&
                    !showIncorrect &&
                    (isSelected
                      ? "border-primary bg-primary/20 shadow-[0_0_20px_hsl(var(--primary)/0.3)]"
                      : "bg-secondary/50 border-border hover:bg-secondary hover:border-primary/50 hover:-translate-y-1"),
                  showCorrect &&
                    "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:bg-emerald-500/20",
                  showIncorrect && "bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20",
                  hasSubmitted && !isSelected && !isCorrectChoice(choice) && "opacity-50"
                )}
                onClick={() => handleSelectAnswer(choice)}
                disabled={hasSubmitted}
                role="radio"
                aria-checked={isSelected ? "true" : "false"}
                aria-label={`${t("option", { index: index + 1 })}: ${choice}${hasSubmitted ? (isCorrectChoice(choice) ? ` - ${t("answerCorrect")}` : showIncorrect ? ` - ${t("answerIncorrect")}` : "") : ""}`}
                tabIndex={hasSubmitted ? -1 : isSelected ? 0 : -1}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handleSelectAnswer(choice);
                  }
                  if (e.key === "ArrowRight" && index < choices.length - 1) {
                    e.preventDefault();
                    const next = e.currentTarget.parentElement?.children[index + 1] as HTMLElement;
                    next?.focus();
                  }
                  if (e.key === "ArrowLeft" && index > 0) {
                    e.preventDefault();
                    const prev = e.currentTarget.parentElement?.children[index - 1] as HTMLElement;
                    prev?.focus();
                  }
                }}
              >
                {choice}
              </button>
            );
          })}
        </div>
      ) : (
        <div className="p-4 border rounded-lg bg-muted/50 mb-8">
          <p className="text-muted-foreground text-sm">
            {t("noChoices")}{" "}
            <strong>{submitResult?.correct_answer ?? exercise.correct_answer}</strong>
          </p>
        </div>
      )}

      {/* Bouton Valider — dynamique (grisé si aucune réponse, primaire si activé) */}
      {!hasSubmitted && (
        <Button
          onClick={handleSubmit}
          disabled={!selectedAnswer || isSubmitting}
          className={cn(
            "w-full size-lg transition-all",
            !selectedAnswer &&
              "bg-muted text-muted-foreground opacity-60 cursor-not-allowed border border-border",
            selectedAnswer &&
              "bg-primary text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.35)] hover:shadow-[0_0_20px_hsl(var(--primary)/0.5)]"
          )}
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
            "rounded-xl p-4 font-semibold text-lg flex items-center gap-3 transition-all mt-8",
            isCorrect
              ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
              : "bg-red-500/10 border-2 border-red-500/30 text-red-400"
          )}
        >
          {isCorrect ? (
            <CheckCircle2 className="h-6 w-6 flex-shrink-0" />
          ) : (
            <XCircle className="h-6 w-6 flex-shrink-0" />
          )}
          <div className="flex-1">
            <p className={isCorrect ? "mb-0" : "mb-1"}>
              {isCorrect ? t("correctTitle") : t("incorrectTitle")}
            </p>
            {!isCorrect && (
              <p className="text-sm opacity-90">
                {t("correctAnswerWas")} <strong>{submitResult.correct_answer}</strong>
              </p>
            )}
          </div>
        </div>
      )}

      {/* Explication — Fiche de savoir */}
      {showExplanation && (exercise.explanation || submitResult?.explanation) && (
        <div className="bg-primary/5 border-l-4 border-primary rounded-r-xl p-5 mt-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-primary mb-2">{t("explanation")}</h4>
              <MathText size="lg" className="text-foreground">
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
          className="w-full mt-6"
          aria-label={t("hint")}
        >
          <Lightbulb className="mr-2 h-4 w-4" />
          {t("hint")}
        </Button>
      )}
      {showHint && exercise.hint && (
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 mt-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-yellow-400 mb-1">{t("hint")}</h4>
              <MathText size="sm" className="text-muted-foreground">
                {exercise.hint || ""}
              </MathText>
            </div>
          </div>
        </div>
      )}

      {/* Actions après soumission */}
      {hasSubmitted && (
        <div className="flex gap-3 pt-8 mt-8 border-t border-border">
          <Button
            variant="outline"
            asChild
            className="flex-1 bg-transparent border border-border text-muted-foreground hover:bg-accent hover:text-foreground px-6 py-3 rounded-xl transition-colors"
          >
            <Link href="/exercises">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("backToExercises")}
            </Link>
          </Button>
          <Button
            onClick={() => router.push("/exercises")}
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
            aria-label={t("newExercise")}
          >
            <ArrowRight className="mr-2 h-4 w-4" />
            {t("newExercise")}
          </Button>
        </div>
      )}
    </FocusBoard>
  );
}
