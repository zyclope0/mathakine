"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { toast } from "sonner";

import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer, type SubmitAnswerResponse } from "@/hooks/useSubmitAnswer";
import { useIrtScores } from "@/hooks/useIrtScores";
import { fetchNextReviewApi } from "@/hooks/useNextReview";
import { api, ApiClientError } from "@/lib/api/client";
import {
  clearSpacedReviewNext,
  readSpacedReviewNext,
  storeSpacedReviewNext,
} from "@/lib/spacedReviewSession";
import type {
  NextReviewApiResponse,
  ReviewSafeExercisePayload,
} from "@/lib/validation/spacedRepetitionNextReview";
import type { Exercise } from "@/types/api";
import {
  INTERLEAVED_STORAGE_KEY,
  parseInterleavedSessionFromStorage,
  readSessionMode,
  type InterleavedSessionStored,
  type SessionMode,
} from "@/lib/exercises/exerciseSolverSession";
import {
  buildInterleavedSessionStorageJson,
  filterExerciseChoices,
  isInterleavedSessionEndScreen,
  mergeInterleavedAnalyticsForNextStep,
  resolveDisplayExercise,
  resolveSolverExplanationText,
  spacedReviewApplyPlanFromApi,
  type SolverDisplayExercise,
} from "@/lib/exercises/exerciseSolverFlow";

export type SpacedReviewPhase = "idle" | "loading" | "error" | "has_next" | "complete";

export type ReviewExerciseErrorCode = "no_review" | "request_failed";

export interface UseExerciseSolverControllerResult {
  sessionMode: SessionMode;
  exercise: Exercise | undefined;
  exerciseLoading: boolean;
  exerciseError: ApiClientError | null;
  submitResult: SubmitAnswerResponse | undefined;
  isSubmitting: boolean;
  selectedAnswer: string | null;
  hasSubmitted: boolean;
  showExplanation: boolean;
  showHint: boolean;
  setShowHint: (value: boolean) => void;
  sessionData: InterleavedSessionStored | null;
  isGeneratingNext: boolean;
  spacedReviewPhase: SpacedReviewPhase;
  nextSpacedExerciseId: number | null;
  reviewExercise: ReviewSafeExercisePayload | null;
  isReviewExerciseLoading: boolean;
  reviewExerciseError: ReviewExerciseErrorCode | null;
  displayExercise: SolverDisplayExercise | null;
  isOpenAnswer: boolean;
  choices: string[];
  isCorrect: boolean;
  isCorrectChoice: (choice: string) => boolean;
  explanationText: string;
  correctAnswerForChoices: string;
  isSessionEnd: boolean;
  handleSelectAnswer: (answer: string) => void;
  handleSubmit: () => Promise<void>;
  handleNextExercise: () => Promise<void>;
  handleRetrySpacedReviewFetch: () => Promise<void>;
  pushToExercise: (path: string) => void;
}

export function useExerciseSolverController(exerciseId: number): UseExerciseSolverControllerResult {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionMode = readSessionMode(searchParams);
  const tToasts = useTranslations("toasts.exercises");

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

  const [spacedReviewPhase, setSpacedReviewPhase] = useState<SpacedReviewPhase>("idle");
  const [nextSpacedExerciseId, setNextSpacedExerciseId] = useState<number | null>(null);
  const [reviewExercise, setReviewExercise] = useState<ReviewSafeExercisePayload | null>(null);
  const [isReviewExerciseLoading, setIsReviewExerciseLoading] = useState(false);
  const [reviewExerciseError, setReviewExerciseError] = useState<ReviewExerciseErrorCode | null>(
    null
  );

  const applySpacedReviewFetchResult = useCallback((parsed: NextReviewApiResponse | null) => {
    const plan = spacedReviewApplyPlanFromApi(parsed);
    if (plan.kind === "error") {
      setSpacedReviewPhase("error");
      setNextSpacedExerciseId(null);
      return;
    }
    if (plan.kind === "has_next") {
      storeSpacedReviewNext(plan.nextReview);
      setNextSpacedExerciseId(plan.nextReview.exercise_id);
      setSpacedReviewPhase("has_next");
    } else {
      clearSpacedReviewNext();
      setNextSpacedExerciseId(null);
      setSpacedReviewPhase("complete");
    }
  }, []);

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

  const isSessionEnd = isInterleavedSessionEndScreen(sessionMode, sessionData, hasSubmitted);

  useEffect(() => {
    if (isSessionEnd && typeof window !== "undefined") {
      sessionStorage.removeItem(INTERLEAVED_STORAGE_KEY);
    }
  }, [isSessionEnd]);

  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      setShowExplanation(true);
    }
  }, [submitResult]);

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

  const displayExercise = resolveDisplayExercise(sessionMode, exercise, reviewExercise);
  const isOpenAnswer = displayExercise ? resolveIsOpenAnswer(displayExercise.exercise_type) : false;

  const handleSelectAnswer = useCallback(
    (answer: string) => {
      if (hasSubmitted) return;
      setSelectedAnswer(answer);
    },
    [hasSubmitted]
  );

  const handleSubmit = useCallback(async () => {
    if (!selectedAnswer?.trim() || !displayExercise || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000;

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
  }, [displayExercise, hasSubmitted, selectedAnswer, sessionMode, submitAnswer]);

  const handleNextExercise = useCallback(async () => {
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
      const generated = await api.post<{ id?: number }>("/api/exercises/generate", {
        exercise_type: nextType,
        adaptive: true,
        save: true,
      });
      if (generated?.id) {
        const currentRaw =
          typeof window !== "undefined" ? sessionStorage.getItem(INTERLEAVED_STORAGE_KEY) : null;
        const analytics = mergeInterleavedAnalyticsForNextStep(sessionData, currentRaw);
        const payload = buildInterleavedSessionStorageJson({
          plan: sessionData.plan,
          completedCount: nextIndex,
          length: sessionData.length,
          analytics,
        });
        sessionStorage.setItem(INTERLEAVED_STORAGE_KEY, payload);
        router.push(`/exercises/${generated.id}?session=interleaved`);
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
  }, [isGeneratingNext, router, sessionData, tToasts]);

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

  const pushToExercise = useCallback(
    (path: string) => {
      router.push(path);
    },
    [router]
  );

  const choices = displayExercise ? filterExerciseChoices(displayExercise.choices) : [];
  const isCorrect = submitResult?.is_correct ?? false;
  const isCorrectChoice = useCallback(
    (choice: string) =>
      hasSubmitted && submitResult?.correct_answer ? choice === submitResult.correct_answer : false,
    [hasSubmitted, submitResult?.correct_answer]
  );
  const explanationText = resolveSolverExplanationText(
    submitResult?.explanation,
    exercise?.explanation
  );
  const correctAnswerForChoices = submitResult?.correct_answer ?? exercise?.correct_answer ?? "";

  return {
    sessionMode,
    exercise,
    exerciseLoading: isLoading,
    exerciseError: error ?? null,
    submitResult,
    isSubmitting,
    selectedAnswer,
    hasSubmitted,
    showExplanation,
    showHint,
    setShowHint,
    sessionData,
    isGeneratingNext,
    spacedReviewPhase,
    nextSpacedExerciseId,
    reviewExercise,
    isReviewExerciseLoading,
    reviewExerciseError,
    displayExercise,
    isOpenAnswer,
    choices,
    isCorrect,
    isCorrectChoice,
    explanationText,
    correctAnswerForChoices,
    isSessionEnd,
    handleSelectAnswer,
    handleSubmit,
    handleNextExercise,
    handleRetrySpacedReviewFetch,
    pushToExercise,
  };
}
