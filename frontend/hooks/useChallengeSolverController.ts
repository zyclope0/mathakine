"use client";

/**
 * useChallengeSolverController — logique runtime locale du solver de défi.
 *
 * Porte :
 *   - l'état local (réponse, soumission, indices, sélections visuelles, timer…)
 *   - les effets de reset / sync
 *   - les handlers (retry, submit, hint, puzzle, answer change)
 *   - les dérivés purs consommables par le container et la Command Bar
 *
 * Ce hook ne fait aucun fetch propre. Il délègue la communication réseau à
 * `useChallenges` (submitAnswer, getHint, setHints) passés en paramètre.
 *
 * FFI-L10 lot 3 — extraction hook controller.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import type { Challenge, ChallengeAttemptResponse } from "@/types/api";
import {
  getChallengeHintsArray,
  getChallengeVisualAnswerModel,
  isChallengeAnswerEmpty,
  getChallengeTextInputKind,
  normalizeChallengeChoices,
} from "@/lib/challenges/challengeSolver";
import type {
  ChallengeVisualAnswerModel,
  ChallengeTextInputKind,
} from "@/lib/challenges/challengeSolver";

// ─── Types ────────────────────────────────────────────────────────────────────

interface UseChallengeSolverControllerArgs {
  challengeId: number;
  challenge: Challenge | undefined;
  submitAnswer: (payload: {
    challenge_id: number;
    answer: string;
    time_spent: number;
    hints_used: number[];
  }) => Promise<ChallengeAttemptResponse>;
  isSubmitting: boolean;
  submitResult: ChallengeAttemptResponse | undefined;
  getHint: (challengeId: number) => Promise<string[]>;
  setHints: (hints: string[]) => void;
  onChallengeCompleted?: (() => void) | undefined;
}

export interface ChallengeSolverControllerState {
  // ─── State brut ────────────────────────────────────────────────────────────
  userAnswer: string;
  setUserAnswer: (answer: string) => void;
  hasSubmitted: boolean;
  hintsUsed: number[];
  availableHints: string[];
  puzzleOrder: string[];
  visualSelections: Record<number, string>;
  setVisualSelections: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  retryKey: number;
  // ─── Dérivés prêts à consommer ─────────────────────────────────────────────
  isCorrect: boolean;
  choicesArray: string[];
  /** visualModel est garanti non-null quand challenge est défini. */
  visualModel: ChallengeVisualAnswerModel | null;
  isAnswerEmpty: boolean;
  isDisabled: boolean;
  textInputKind: ChallengeTextInputKind;
  // ─── Handlers ──────────────────────────────────────────────────────────────
  handleRetry: () => void;
  handlePuzzleOrderChange: (order: string[]) => void;
  handleAnswerChange: (answer: string) => void;
  handleRequestHint: () => Promise<void>;
  handleSubmit: () => Promise<void>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useChallengeSolverController({
  challengeId,
  challenge,
  submitAnswer,
  isSubmitting,
  submitResult,
  getHint,
  setHints,
  onChallengeCompleted,
}: UseChallengeSolverControllerArgs): ChallengeSolverControllerState {
  // ─── State local ───────────────────────────────────────────────────────────
  const [userAnswer, setUserAnswer] = useState<string>("");
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [, setShowExplanation] = useState(false);
  const [hintsUsed, setHintsUsed] = useState<number[]>([]);
  const [availableHints, setAvailableHints] = useState<string[]>([]);
  const [puzzleOrder, setPuzzleOrder] = useState<string[]>([]);
  const [visualSelections, setVisualSelections] = useState<Record<number, string>>({});
  const [retryKey, setRetryKey] = useState<number>(0);
  const startTimeRef = useRef<number>(Date.now());

  // ─── Effects ───────────────────────────────────────────────────────────────

  // Initialise le timer au montage
  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  // Initialise les indices disponibles à chaque changement de défi
  useEffect(() => {
    if (challenge?.hints) {
      setAvailableHints(getChallengeHintsArray(challenge.hints));
      setHints([]);
    } else {
      setAvailableHints([]);
    }
  }, [challenge, setHints]);

  // Marque comme soumis + callback succès
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      if (submitResult.is_correct) {
        setShowExplanation(true);
        onChallengeCompleted?.();
      }
    }
  }, [submitResult, onChallengeCompleted]);

  // Réinitialise l'état à chaque changement d'id de défi
  useEffect(() => {
    if (challenge) {
      setUserAnswer("");
      setHasSubmitted(false);
      setShowExplanation(false);
      setHintsUsed([]);
      setPuzzleOrder([]);
      setVisualSelections({});
      startTimeRef.current = Date.now();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [challenge?.id]);

  // ─── Dérivés visuels ───────────────────────────────────────────────────────
  const visualModel = challenge ? getChallengeVisualAnswerModel(challenge, visualSelections) : null;

  // Sync sélections multi-position → userAnswer
  useEffect(() => {
    if (!visualModel?.hasVisualButtons || !visualModel.visualPositions.length) return;
    if (visualModel.visualPositions.length < 2) return;
    setUserAnswer(visualModel.derivedUserAnswerFromSelections);
  }, [
    visualModel?.hasVisualButtons,
    visualModel?.visualPositions,
    visualModel?.derivedUserAnswerFromSelections,
  ]);

  // ─── Dérivés consommables ──────────────────────────────────────────────────
  const isCorrect = submitResult?.is_correct ?? false;
  const choicesArray = challenge ? normalizeChallengeChoices(challenge) : [];

  const hasVisualButtons = visualModel?.hasVisualButtons ?? false;
  const visualPositions = visualModel?.visualPositions ?? [];
  const isVisualMultiComplete = visualModel?.isVisualMultiComplete ?? true;

  const isAnswerEmpty = isChallengeAnswerEmpty({
    hasVisualButtons,
    visualPositions,
    isVisualMultiComplete,
    userAnswer,
  });

  const isDisabled = isSubmitting || hasSubmitted || isAnswerEmpty;
  const textInputKind = getChallengeTextInputKind(challenge?.challenge_type);

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleRetry = () => {
    setUserAnswer("");
    setHasSubmitted(false);
    setShowExplanation(false);
    setPuzzleOrder([]);
    setVisualSelections({});
    setRetryKey((prev) => prev + 1);
    startTimeRef.current = Date.now();
  };

  const handlePuzzleOrderChange = useCallback(
    (order: string[]) => {
      setPuzzleOrder(order);
      if (challenge?.challenge_type?.toLowerCase() === "puzzle") {
        setUserAnswer(order.join(","));
      }
    },
    [challenge?.challenge_type]
  );

  const handleAnswerChange = useCallback(
    (answer: string) => {
      const type = challenge?.challenge_type?.toLowerCase();
      if (type === "sequence" || type === "pattern" || type === "deduction") {
        setUserAnswer(answer);
      }
    },
    [challenge?.challenge_type]
  );

  const handleRequestHint = async () => {
    if (!challenge || hintsUsed.length >= availableHints.length) return;
    const nextHintNumber = hintsUsed.length + 1;
    try {
      await getHint(challengeId);
    } catch {
      // L'indice local est révélé même si le tracking API échoue
    }
    setHintsUsed((prev) => [...prev, nextHintNumber]);
  };

  const handleSubmit = async () => {
    if (!userAnswer.trim() || !challenge || hasSubmitted) return;
    const timeSpent = (Date.now() - startTimeRef.current) / 1000;
    try {
      await submitAnswer({
        challenge_id: challenge.id,
        answer: userAnswer.trim(),
        time_spent: timeSpent,
        hints_used: hintsUsed,
      });
    } catch {
      // Erreur gérée par le hook useChallenges
    }
  };

  return {
    userAnswer,
    setUserAnswer,
    hasSubmitted,
    hintsUsed,
    availableHints,
    puzzleOrder,
    visualSelections,
    setVisualSelections,
    retryKey,
    isCorrect,
    choicesArray,
    visualModel,
    isAnswerEmpty,
    isDisabled,
    textInputKind,
    handleRetry,
    handlePuzzleOrderChange,
    handleAnswerChange,
    handleRequestHint,
    handleSubmit,
  };
}
