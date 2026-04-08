"use client";

import { Button } from "@/components/ui/button";
import { useExerciseSolverController } from "@/hooks/useExerciseSolverController";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { Loader2, XCircle, ArrowLeft, ArrowRight, Lightbulb } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { LearnerCard } from "@/components/learner";
import { ExerciseSolverHeader } from "@/components/exercises/ExerciseSolverHeader";
import { ExerciseSolverChoices } from "@/components/exercises/ExerciseSolverChoices";
import { ExerciseSolverFeedback } from "@/components/exercises/ExerciseSolverFeedback";
import { ExerciseSolverHint } from "@/components/exercises/ExerciseSolverHint";

interface ExerciseSolverProps {
  exerciseId: number;
}

export function ExerciseSolver({ exerciseId }: ExerciseSolverProps) {
  const t = useTranslations("exercises.solver");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const c = useExerciseSolverController(exerciseId);

  if (c.exerciseLoading) {
    return (
      <LearnerCard variant="exercise">
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("loading")}</p>
          </div>
        </div>
      </LearnerCard>
    );
  }

  if (c.exerciseError) {
    return (
      <LearnerCard variant="exercise">
        <div className="text-center space-y-4" role="alert" aria-live="assertive">
          <XCircle className="h-12 w-12 text-destructive mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-destructive">{t("error.title")}</h3>
            <p className="text-muted-foreground mt-2">
              {c.exerciseError.status === 404
                ? t("error.notFound")
                : c.exerciseError.message || t("error.generic")}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/exercises">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("backToExercises")}
            </Link>
          </Button>
        </div>
      </LearnerCard>
    );
  }

  if (c.sessionMode === "spaced-review" && c.isReviewExerciseLoading) {
    return (
      <LearnerCard variant="exercise">
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto motion-reduce:animate-none" />
            <p className="text-muted-foreground">{t("reviewPreparing")}</p>
          </div>
        </div>
      </LearnerCard>
    );
  }

  if (c.sessionMode === "spaced-review" && c.reviewExerciseError) {
    return (
      <LearnerCard variant="exercise">
        <div className="text-center space-y-4" role="status" aria-live="polite">
          <div>
            <h3 className="text-lg font-semibold text-foreground">{t("reviewUnavailableTitle")}</h3>
            <p className="text-muted-foreground mt-2">
              {c.reviewExerciseError === "no_review"
                ? t("reviewUnavailableBody")
                : t("reviewFetchNextError")}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild variant="default" className="min-h-11">
              <Link href="/dashboard">{t("reviewBackDashboard")}</Link>
            </Button>
            <Button asChild variant="outline" className="min-h-11">
              <Link href="/exercises">{t("backToExercises")}</Link>
            </Button>
          </div>
        </div>
      </LearnerCard>
    );
  }

  if (!c.displayExercise) {
    return null;
  }

  const typeDisplay = getTypeDisplay(c.displayExercise.exercise_type);
  const ageGroupDisplay = getAgeDisplay(c.displayExercise.age_group);

  return (
    <LearnerCard variant="exercise">
      {c.sessionMode === "interleaved" && c.sessionData && (
        <p className="text-sm text-muted-foreground mb-4" aria-live="polite">
          {t("sessionProgress", {
            current: c.sessionData.completedCount + 1,
            total: c.sessionData.length,
          })}
        </p>
      )}

      <ExerciseSolverHeader
        sessionMode={c.sessionMode}
        typeDisplay={typeDisplay}
        ageGroupDisplay={ageGroupDisplay}
        title={c.displayExercise.title}
        question={c.displayExercise.question}
        labels={{
          reviewNavLabel: t("reviewNavLabel"),
          reviewBackDashboard: t("reviewBackDashboard"),
          reviewAllExercises: t("reviewAllExercises"),
          reviewContextBadge: t("reviewContextBadge"),
          back: t("back"),
        }}
      />

      {!c.hasSubmitted && c.sessionMode !== "spaced-review" && (
        <ExerciseSolverHint
          isOpenAnswer={c.isOpenAnswer}
          hasHint={"hint" in c.displayExercise && !!c.displayExercise.hint}
        />
      )}

      {!c.hasSubmitted && c.exercise?.hint && !c.showHint && c.sessionMode !== "spaced-review" && (
        <div className="flex justify-end mb-2">
          <button
            type="button"
            onClick={() => c.setShowHint(true)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            aria-label={t("hint")}
          >
            <Lightbulb className="h-3.5 w-3.5" aria-hidden="true" />
            {t("hint")}
          </button>
        </div>
      )}

      <ExerciseSolverChoices
        isOpenAnswer={c.isOpenAnswer}
        choices={c.choices}
        selectedAnswer={c.selectedAnswer}
        hasSubmitted={c.hasSubmitted}
        isCorrectChoice={c.isCorrectChoice}
        sessionMode={c.sessionMode}
        correctAnswer={c.correctAnswerForChoices}
        onSelectAnswer={c.handleSelectAnswer}
        onSubmitOpenAnswer={c.handleSubmit}
        labels={{
          openAnswerLabel: t("openAnswerLabel", { default: "Votre réponse" }),
          openAnswerPlaceholder: t("openAnswerPlaceholder", { default: "Entrez votre réponse…" }),
          option: (index) => t("option", { index }),
          answerCorrect: t("answerCorrect"),
          answerIncorrect: t("answerIncorrect"),
          reviewNoChoicesFallback: t("reviewNoChoicesFallback"),
          noChoices: t("noChoices"),
        }}
      />

      {!c.hasSubmitted && (
        <div className="space-y-2">
          <Button
            onClick={() => void c.handleSubmit()}
            disabled={!c.selectedAnswer?.trim() || c.isSubmitting}
            className={cn(
              "w-full size-lg transition-all",
              !c.selectedAnswer?.trim() &&
                "bg-muted text-muted-foreground opacity-60 cursor-not-allowed border border-border",
              c.selectedAnswer?.trim() && "bg-primary text-primary-foreground"
            )}
            size="lg"
            aria-label={c.isSubmitting ? t("validating") : t("validateAnswer")}
            aria-busy={c.isSubmitting}
            aria-describedby={!c.selectedAnswer?.trim() ? "validate-hint" : undefined}
          >
            {c.isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                {t("validating")}
              </>
            ) : (
              t("validateMyAnswer")
            )}
          </Button>
          {!c.selectedAnswer?.trim() && (
            <p
              id="validate-hint"
              className="text-center text-xs text-muted-foreground"
              aria-live="polite"
            >
              {c.isOpenAnswer ? t("validateHintOpen") : t("validateHintMcq")}
            </p>
          )}
        </div>
      )}

      <ExerciseSolverFeedback
        hasSubmitted={c.hasSubmitted}
        submitResultPresent={!!c.submitResult}
        isCorrect={c.isCorrect}
        correctAnswer={c.submitResult?.correct_answer ?? ""}
        explanationText={c.explanationText}
        showExplanation={c.showExplanation}
        hint={c.exercise?.hint}
        showHint={c.showHint}
        sessionMode={c.sessionMode}
        labels={{
          correctTitle: t("correctTitle"),
          incorrectTitle: t("incorrectTitle"),
          incorrectSupport: t("incorrectSupport"),
          correctAnswerWas: t("correctAnswerWas"),
          explanation: t("explanation"),
          hint: t("hint"),
        }}
      />

      {c.hasSubmitted && c.sessionMode === "interleaved" && c.sessionData && (
        <>
          {c.sessionData.completedCount + 1 >= c.sessionData.plan.length ? (
            <div className="pt-8 mt-8 border-t border-border space-y-4">
              <h3 className="text-xl font-semibold text-foreground">{t("sessionEndTitle")}</h3>
              <p className="text-muted-foreground">{t("sessionEndDescription")}</p>
              <Button asChild variant="outline">
                <Link href="/exercises">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t("backToExercises")}
                </Link>
              </Button>
            </div>
          ) : (
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
                onClick={() => void c.handleNextExercise()}
                disabled={c.isGeneratingNext}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
                aria-label={t("nextExercise")}
              >
                {c.isGeneratingNext ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <ArrowRight className="mr-2 h-4 w-4" />
                )}
                {t("nextExercise")}
              </Button>
            </div>
          )}
        </>
      )}
      {c.hasSubmitted && c.sessionMode === "spaced-review" && (
        <section
          className="pt-8 mt-8 border-t border-border space-y-4"
          aria-label={t("reviewFollowUpLabel")}
        >
          {c.spacedReviewPhase === "loading" || c.spacedReviewPhase === "idle" ? (
            <p className="text-muted-foreground text-sm flex items-center gap-2 min-h-11">
              <Loader2
                className="h-4 w-4 shrink-0 animate-spin text-muted-foreground motion-reduce:animate-none"
                aria-hidden
              />
              {t("reviewCheckingNext")}
            </p>
          ) : null}
          {c.spacedReviewPhase === "error" ? (
            <div className="space-y-3">
              <p className="text-muted-foreground text-sm leading-relaxed">
                {t("reviewFetchNextError")}
              </p>
              <Button
                type="button"
                variant="outline"
                className="min-h-11"
                onClick={() => void c.handleRetrySpacedReviewFetch()}
              >
                {t("reviewRetry")}
              </Button>
            </div>
          ) : null}
          {c.spacedReviewPhase === "complete" ? (
            <div className="space-y-4 p-6 rounded-xl bg-muted/30 border border-border">
              <h3 className="text-lg font-semibold text-foreground">
                {t("reviewSessionCompleteTitle")}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {t("reviewSessionCompleteBody")}
              </p>
              <div className="flex flex-col sm:flex-row gap-3 pt-1">
                <Button asChild variant="default" className="min-h-11 w-full sm:w-auto">
                  <Link href="/dashboard">{t("reviewBackDashboard")}</Link>
                </Button>
                <Button asChild variant="outline" className="min-h-11 w-full sm:w-auto">
                  <Link href="/exercises">{t("backToExercises")}</Link>
                </Button>
              </div>
            </div>
          ) : null}
          {c.spacedReviewPhase === "has_next" && c.nextSpacedExerciseId !== null ? (
            <div className="flex flex-col sm:flex-row gap-3">
              <Button asChild variant="outline" className="min-h-11 flex-1">
                <Link href="/dashboard">{t("reviewBackDashboard")}</Link>
              </Button>
              <Button
                type="button"
                className="min-h-11 flex-1"
                onClick={() =>
                  c.pushToExercise(`/exercises/${c.nextSpacedExerciseId}?session=spaced-review`)
                }
              >
                <ArrowRight className="mr-2 h-4 w-4 shrink-0" aria-hidden />
                {t("reviewNext")}
              </Button>
            </div>
          ) : null}
        </section>
      )}
      {c.hasSubmitted &&
        !(c.sessionMode === "interleaved" && c.sessionData) &&
        c.sessionMode !== "spaced-review" && (
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
              onClick={() => c.pushToExercise("/exercises")}
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
              aria-label={t("newExercise")}
            >
              <ArrowRight className="mr-2 h-4 w-4" />
              {t("newExercise")}
            </Button>
          </div>
        )}
    </LearnerCard>
  );
}
