"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useIrtScores } from "@/hooks/useIrtScores";
import { Loader2, XCircle, ArrowLeft, ArrowRight, Lightbulb } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { fetchNextReviewApi } from "@/hooks/useNextReview";
import {
  clearSpacedReviewNext,
  readSpacedReviewNext,
  storeSpacedReviewNext,
} from "@/lib/spacedReviewSession";
import type { ReviewSafeExercisePayload } from "@/lib/validation/spacedRepetitionNextReview";
import { LearnerCard } from "@/components/learner";
import {
  INTERLEAVED_STORAGE_KEY,
  parseInterleavedSessionFromStorage,
  readSessionMode,
  type InterleavedSessionStored,
} from "@/lib/exercises/exerciseSolverSession";
import { ExerciseSolverHeader } from "@/components/exercises/ExerciseSolverHeader";
import { ExerciseSolverChoices } from "@/components/exercises/ExerciseSolverChoices";
import { ExerciseSolverFeedback } from "@/components/exercises/ExerciseSolverFeedback";

interface ExerciseSolverProps {
  exerciseId: number;
}

export function ExerciseSolver({ exerciseId }: ExerciseSolverProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionMode = readSessionMode(searchParams);
  const t = useTranslations("exercises.solver");
  const tToasts = useTranslations("toasts.exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { exercise, isLoading, error } = useExercise(exerciseId, {
    enabled: sessionMode !== "spaced-review",
  });
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const { resolveIsOpenAnswer } = useIrtScores();
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [sessionData, setSessionData] = useState<InterleavedSessionStored | null>(null);
  const [isGeneratingNext, setIsGeneratingNext] = useState(false);
  const startTimeRef = useRef<number>(0);
  const [spacedReviewPhase, setSpacedReviewPhase] = useState<
    "idle" | "loading" | "error" | "has_next" | "complete"
  >("idle");
  const [nextSpacedExerciseId, setNextSpacedExerciseId] = useState<number | null>(null);
  const [reviewExercise, setReviewExercise] = useState<ReviewSafeExercisePayload | null>(null);
  const [isReviewExerciseLoading, setIsReviewExerciseLoading] = useState(false);
  const [reviewExerciseError, setReviewExerciseError] = useState<string | null>(null);

  const applySpacedReviewFetchResult = useCallback(
    (parsed: Awaited<ReturnType<typeof fetchNextReviewApi>>) => {
      if (!parsed) {
        setSpacedReviewPhase("error");
        setNextSpacedExerciseId(null);
        return;
      }
      if (parsed.has_due_review && parsed.next_review) {
        storeSpacedReviewNext(parsed.next_review);
        setNextSpacedExerciseId(parsed.next_review.exercise_id);
        setSpacedReviewPhase("has_next");
      } else {
        clearSpacedReviewNext();
        setNextSpacedExerciseId(null);
        setSpacedReviewPhase("complete");
      }
    },
    []
  );

  useEffect(() => {
    if (sessionMode !== "spaced-review") {
      setSpacedReviewPhase("idle");
      setNextSpacedExerciseId(null);
      setReviewExercise(null);
      setIsReviewExerciseLoading(false);
      setReviewExerciseError(null);
      return;
    }
    setSpacedReviewPhase("idle");
    setNextSpacedExerciseId(null);
    setReviewExercise(null);
    setReviewExerciseError(null);
    const stored = readSpacedReviewNext(exerciseId);
    if (stored) {
      setReviewExercise(stored.exercise);
      setIsReviewExerciseLoading(false);
      return;
    }

    let cancelled = false;
    setIsReviewExerciseLoading(true);
    void (async () => {
      try {
        const parsed = await fetchNextReviewApi();
        if (cancelled) {
          return;
        }
        if (!parsed || !parsed.has_due_review || !parsed.next_review) {
          clearSpacedReviewNext();
          setReviewExercise(null);
          setReviewExerciseError("no_review");
          return;
        }
        storeSpacedReviewNext(parsed.next_review);
        if (parsed.next_review.exercise_id !== exerciseId) {
          router.replace(`/exercises/${parsed.next_review.exercise_id}?session=spaced-review`);
          return;
        }
        setReviewExercise(parsed.next_review.exercise);
        setReviewExerciseError(null);
      } catch {
        if (!cancelled) {
          setReviewExercise(null);
          setReviewExerciseError("request_failed");
        }
      } finally {
        if (!cancelled) {
          setIsReviewExerciseLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [exerciseId, router, sessionMode]);

  useEffect(() => {
    if (sessionMode !== "spaced-review" || !hasSubmitted || !submitResult) {
      return;
    }
    let cancelled = false;
    setSpacedReviewPhase("loading");
    void (async () => {
      try {
        const parsed = await fetchNextReviewApi();
        if (cancelled) {
          return;
        }
        applySpacedReviewFetchResult(parsed);
      } catch {
        if (!cancelled) {
          setSpacedReviewPhase("error");
          setNextSpacedExerciseId(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionMode, hasSubmitted, submitResult, exerciseId, applySpacedReviewFetchResult]);

  useEffect(() => {
    if (sessionMode === "interleaved" && typeof window !== "undefined") {
      try {
        const raw = sessionStorage.getItem(INTERLEAVED_STORAGE_KEY);
        if (raw) {
          const parsed = parseInterleavedSessionFromStorage(raw);
          if (parsed) {
            setSessionData(parsed);
          }
        }
      } catch {
        // Ignore invalid storage
      }
    }
  }, [sessionMode]);

  // Clear session storage when we show the end screen
  const isSessionEnd =
    sessionMode === "interleaved" &&
    sessionData &&
    hasSubmitted &&
    sessionData.completedCount + 1 >= sessionData.plan.length;
  useEffect(() => {
    if (isSessionEnd && typeof window !== "undefined") {
      sessionStorage.removeItem(INTERLEAVED_STORAGE_KEY);
    }
  }, [isSessionEnd]);
  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  // Mettre à jour l'état quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      // Retrieval-first before submit, explanatory feedback after the learner answers.
      setShowExplanation(true);
    }
  }, [submitResult]);

  // Réinitialiser l'état quand l'exercice change
  useEffect(() => {
    const displayExerciseAvailable =
      sessionMode === "spaced-review" ? reviewExercise != null : exercise != null;
    if (displayExerciseAvailable) {
      setSelectedAnswer(null);
      setHasSubmitted(false);
      setShowExplanation(false);
      setShowHint(false);
      startTimeRef.current = Date.now();
    }
    // exhaustive-deps: reset seulement si l'exercice courant change de réalité visible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exercise?.id, reviewExercise?.id, sessionMode]);

  // Le mode de réponse est résolu depuis les scores IRT de l'utilisateur (F03+F05),
  // pas depuis le flag is_open_answer du générateur. Cela permet au backend de
  // toujours générer les choices, et au frontend de décider selon le niveau réel
  // par type (QCM pour les niveaux inférieurs, saisie libre à GRAND_MAITRE IRT).
  const displayExercise = sessionMode === "spaced-review" ? reviewExercise : exercise;
  const isOpenAnswer = displayExercise ? resolveIsOpenAnswer(displayExercise.exercise_type) : false;

  const handleSelectAnswer = (answer: string) => {
    if (hasSubmitted) return;
    setSelectedAnswer(answer);
  };

  const handleSubmit = async () => {
    if (!selectedAnswer?.trim() || !displayExercise || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000; // en secondes

    try {
      await submitAnswer({
        exercise_id: displayExercise.id,
        answer: selectedAnswer,
        time_spent: timeSpent,
        analytics_type: sessionMode === "interleaved" ? "interleaved" : "exercise",
      });
    } catch {
      // L'erreur est déjà gérée par le hook useSubmitAnswer
    }
  };

  const handleNextExercise = async () => {
    if (!sessionData || isGeneratingNext) return;
    const nextIndex = sessionData.completedCount + 1;
    if (nextIndex >= sessionData.plan.length) {
      sessionStorage.removeItem(INTERLEAVED_STORAGE_KEY);
      setSessionData(null);
      return;
    }
    setIsGeneratingNext(true);
    try {
      const nextType = sessionData.plan[nextIndex];
      const exercise = await api.post<{ id?: number }>("/api/exercises/generate", {
        exercise_type: nextType,
        adaptive: true,
        save: true,
      });
      if (exercise?.id) {
        let analytics = sessionData.analytics ?? { firstAttemptTracked: false };
        const currentRaw = sessionStorage.getItem(INTERLEAVED_STORAGE_KEY);
        const current = currentRaw ? parseInterleavedSessionFromStorage(currentRaw) : null;
        if (current?.analytics?.firstAttemptTracked) {
          analytics = { ...analytics, firstAttemptTracked: true };
        }
        sessionStorage.setItem(
          INTERLEAVED_STORAGE_KEY,
          JSON.stringify({
            plan: sessionData.plan,
            completedCount: nextIndex,
            length: sessionData.length,
            analytics,
          })
        );
        router.push(`/exercises/${exercise.id}?session=interleaved`);
      } else {
        toast.error(tToasts("generateError"), {
          description: tToasts("generateErrorDescription"),
        });
      }
    } catch (err) {
      toast.error(tToasts("generateError"), {
        description:
          err instanceof ApiClientError ? err.message : tToasts("generateErrorDescription"),
      });
    } finally {
      setIsGeneratingNext(false);
    }
  };

  const handleRetrySpacedReviewFetch = useCallback(async () => {
    setSpacedReviewPhase("loading");
    try {
      const parsed = await fetchNextReviewApi();
      applySpacedReviewFetchResult(parsed);
    } catch {
      setSpacedReviewPhase("error");
      setNextSpacedExerciseId(null);
    }
  }, [applySpacedReviewFetchResult]);

  if (isLoading) {
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

  if (error) {
    return (
      <LearnerCard variant="exercise">
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
      </LearnerCard>
    );
  }

  if (sessionMode === "spaced-review" && isReviewExerciseLoading) {
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

  if (sessionMode === "spaced-review" && reviewExerciseError) {
    return (
      <LearnerCard variant="exercise">
        <div className="text-center space-y-4" role="status" aria-live="polite">
          <div>
            <h3 className="text-lg font-semibold text-foreground">{t("reviewUnavailableTitle")}</h3>
            <p className="text-muted-foreground mt-2">
              {reviewExerciseError === "no_review"
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

  if (!displayExercise) {
    return null;
  }

  const typeDisplay = getTypeDisplay(displayExercise.exercise_type);
  const ageGroupDisplay = getAgeDisplay(displayExercise.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = Array.isArray(displayExercise.choices)
    ? displayExercise.choices.filter((choice): choice is string => typeof choice === "string")
    : [];
  const isCorrectChoice = (choice: string) =>
    hasSubmitted && submitResult?.correct_answer ? choice === submitResult.correct_answer : false;
  const explanationText = submitResult?.explanation || exercise?.explanation || "";

  return (
    <LearnerCard variant="exercise">
      {/* Progression session entrelacée */}
      {sessionMode === "interleaved" && sessionData && (
        <p className="text-sm text-muted-foreground mb-4" aria-live="polite">
          {t("sessionProgress", {
            current: sessionData.completedCount + 1,
            total: sessionData.length,
          })}
        </p>
      )}

      <ExerciseSolverHeader
        sessionMode={sessionMode}
        typeDisplay={typeDisplay}
        ageGroupDisplay={ageGroupDisplay}
        title={displayExercise.title}
        question={displayExercise.question}
        labels={{
          reviewNavLabel: t("reviewNavLabel"),
          reviewBackDashboard: t("reviewBackDashboard"),
          reviewAllExercises: t("reviewAllExercises"),
          reviewContextBadge: t("reviewContextBadge"),
          back: t("back"),
        }}
      />

      {/* NI-10 — Indice avant les choix : visible sans scroll sur mobile 375px.
          W3C COGA 2.2 : un enfant bloqué ne scroll pas pour chercher de l'aide. */}
      {!hasSubmitted && exercise?.hint && !showHint && sessionMode !== "spaced-review" && (
        <div className="flex justify-end mb-2">
          <button
            type="button"
            onClick={() => setShowHint(true)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            aria-label={t("hint")}
          >
            <Lightbulb className="h-3.5 w-3.5" aria-hidden="true" />
            {t("hint")}
          </button>
        </div>
      )}

      <ExerciseSolverChoices
        isOpenAnswer={isOpenAnswer}
        choices={choices}
        selectedAnswer={selectedAnswer}
        hasSubmitted={hasSubmitted}
        isCorrectChoice={isCorrectChoice}
        sessionMode={sessionMode}
        correctAnswer={submitResult?.correct_answer ?? exercise?.correct_answer ?? ""}
        onSelectAnswer={handleSelectAnswer}
        onSubmitOpenAnswer={handleSubmit}
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

      {/* Bouton Valider — dynamique (grisé si aucune réponse, primaire si activé) */}
      {!hasSubmitted && (
        <div className="space-y-2">
          <Button
            onClick={handleSubmit}
            disabled={!selectedAnswer?.trim() || isSubmitting}
            className={cn(
              "w-full size-lg transition-all",
              !selectedAnswer?.trim() &&
                "bg-muted text-muted-foreground opacity-60 cursor-not-allowed border border-border",
              selectedAnswer?.trim() && "bg-primary text-primary-foreground"
            )}
            size="lg"
            aria-label={isSubmitting ? t("validating") : t("validateAnswer")}
            aria-busy={isSubmitting}
            aria-describedby={!selectedAnswer?.trim() ? "validate-hint" : undefined}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                {t("validating")}
              </>
            ) : (
              t("validateMyAnswer")
            )}
          </Button>
          {!selectedAnswer?.trim() && (
            <p
              id="validate-hint"
              className="text-center text-xs text-muted-foreground"
              aria-live="polite"
            >
              {isOpenAnswer ? t("validateHintOpen") : t("validateHintMcq")}
            </p>
          )}
        </div>
      )}

      <ExerciseSolverFeedback
        hasSubmitted={hasSubmitted}
        submitResultPresent={!!submitResult}
        isCorrect={isCorrect}
        correctAnswer={submitResult?.correct_answer ?? ""}
        explanationText={explanationText}
        showExplanation={showExplanation}
        hint={exercise?.hint}
        showHint={showHint}
        sessionMode={sessionMode}
        labels={{
          correctTitle: t("correctTitle"),
          incorrectTitle: t("incorrectTitle"),
          incorrectSupport: t("incorrectSupport"),
          correctAnswerWas: t("correctAnswerWas"),
          explanation: t("explanation"),
          hint: t("hint"),
        }}
      />

      {/* Actions après soumission */}
      {hasSubmitted && sessionMode === "interleaved" && sessionData && (
        <>
          {sessionData.completedCount + 1 >= sessionData.plan.length ? (
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
                onClick={handleNextExercise}
                disabled={isGeneratingNext}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
                aria-label={t("nextExercise")}
              >
                {isGeneratingNext ? (
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
      {hasSubmitted && sessionMode === "spaced-review" && (
        <section
          className="pt-8 mt-8 border-t border-border space-y-4"
          aria-label={t("reviewFollowUpLabel")}
        >
          {spacedReviewPhase === "loading" || spacedReviewPhase === "idle" ? (
            <p className="text-muted-foreground text-sm flex items-center gap-2 min-h-11">
              <Loader2
                className="h-4 w-4 shrink-0 animate-spin text-muted-foreground motion-reduce:animate-none"
                aria-hidden
              />
              {t("reviewCheckingNext")}
            </p>
          ) : null}
          {spacedReviewPhase === "error" ? (
            <div className="space-y-3">
              <p className="text-muted-foreground text-sm leading-relaxed">
                {t("reviewFetchNextError")}
              </p>
              <Button
                type="button"
                variant="outline"
                className="min-h-11"
                onClick={() => void handleRetrySpacedReviewFetch()}
              >
                {t("reviewRetry")}
              </Button>
            </div>
          ) : null}
          {spacedReviewPhase === "complete" ? (
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
          {spacedReviewPhase === "has_next" && nextSpacedExerciseId !== null ? (
            <div className="flex flex-col sm:flex-row gap-3">
              <Button asChild variant="outline" className="min-h-11 flex-1">
                <Link href="/dashboard">{t("reviewBackDashboard")}</Link>
              </Button>
              <Button
                type="button"
                className="min-h-11 flex-1"
                onClick={() =>
                  router.push(`/exercises/${nextSpacedExerciseId}?session=spaced-review`)
                }
              >
                <ArrowRight className="mr-2 h-4 w-4 shrink-0" aria-hidden />
                {t("reviewNext")}
              </Button>
            </div>
          ) : null}
        </section>
      )}
      {hasSubmitted &&
        !(sessionMode === "interleaved" && sessionData) &&
        sessionMode !== "spaced-review" && (
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
    </LearnerCard>
  );
}
