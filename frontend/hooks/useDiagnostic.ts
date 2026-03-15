"use client";

/**
 * Hook d'état pour la session de diagnostic adaptatif (F03).
 *
 * Gère le cycle complet :
 *   idle → loading → question → answering → feedback → [next question | results]
 *
 * Principe stateless backend : l'état de session JSON est transporté dans chaque
 * requête. Le backend ne stocke rien jusqu'à /complete.
 */

import { useState, useCallback, useRef } from "react";
import { api } from "@/lib/api/client";

// -------------------------------------------------------------------------- //
// Types                                                                       //
// -------------------------------------------------------------------------- //

export type DiagnosticPhase =
  | "idle" // pas encore démarré
  | "loading" // requête en cours
  | "question" // question affichée, attente réponse
  | "feedback" // réponse soumise, feedback affiché
  | "results" // session complète, résultats affichés
  | "error"; // erreur non récupérable

export interface DiagnosticQuestion {
  exercise_type: string;
  difficulty: string;
  level_ordinal: number;
  question: string;
  choices: string[];
  explanation: string;
  hint: string;
  question_number: number;
  max_questions: number;
  types_remaining: number;
}

export interface DiagnosticTypeScore {
  level: number;
  difficulty: string;
  correct: number;
  total: number;
}

export interface DiagnosticScores {
  [exerciseType: string]: DiagnosticTypeScore;
}

export interface DiagnosticResult {
  id: number;
  completed_at: string;
  triggered_from: string;
  questions_asked: number;
  duration_seconds: number | null;
  scores: DiagnosticScores;
}

// Etat de session opaque — synchronisé avec le backend
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SessionState = Record<string, any>;

// -------------------------------------------------------------------------- //
// Hook                                                                        //
// -------------------------------------------------------------------------- //

export function useDiagnostic(triggeredFrom: "onboarding" | "settings" = "onboarding") {
  const [phase, setPhase] = useState<DiagnosticPhase>("idle");
  const [, setSession] = useState<SessionState | null>(null);
  const [stateToken, setStateToken] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<DiagnosticQuestion | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [correctAnswerForFeedback, setCorrectAnswerForFeedback] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Timestamps pour mesurer la durée totale
  const startTsRef = useRef<number>(0);

  // ---- helpers internes -------------------------------------------------- //

  const setErr = useCallback((msg: string) => {
    setError(msg);
    setPhase("error");
  }, []);

  // ---- finalizeSession ---------------------------------------------------- //

  const finalizeSession = useCallback(
    async (currentStateToken: string | null) => {
      if (!currentStateToken) return;
      setPhase("loading");
      const durationSeconds = Math.round((Date.now() - startTsRef.current) / 1000);
      try {
        const res = await api.post<{ success: boolean; result?: DiagnosticResult; error?: string }>(
          "/api/diagnostic/complete",
          { state_token: currentStateToken, duration_seconds: durationSeconds }
        );
        if (res.success && res.result) {
          setResult(res.result);
          setPhase("results");
        } else {
          setErr(res.error ?? "Erreur lors de la finalisation du diagnostic.");
        }
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Erreur réseau lors de la finalisation.");
      }
    },
    [setErr]
  );

  // ---- fetchNextQuestion -------------------------------------------------- //

  const fetchNextQuestion = useCallback(
    async (token: string | null) => {
      if (!token) return;
      setPhase("loading");
      try {
        const res = await api.post<{
          done: boolean;
          question?: DiagnosticQuestion;
          state_token?: string;
        }>("/api/diagnostic/question", { state_token: token });
        const nextToken = res.state_token ?? null;
        setStateToken(nextToken);
        if (res.done) {
          await finalizeSession(nextToken);
        } else if (res.question) {
          setCurrentQuestion(res.question);
          setSelectedAnswer(null);
          setIsCorrect(null);
          setCorrectAnswerForFeedback(null);
          setPhase("question");
        } else {
          setErr("Aucune question retournée par le serveur.");
        }
      } catch (e) {
        setErr(
          e instanceof Error ? e.message : "Erreur réseau lors de la génération de la question."
        );
      }
    },
    [finalizeSession, setErr]
  );

  // ---- start -------------------------------------------------------------- //

  const startDiagnostic = useCallback(async () => {
    setPhase("loading");
    setError(null);
    setResult(null);
    setSession(null);
    setStateToken(null);
    setCurrentQuestion(null);
    setSelectedAnswer(null);
    setIsCorrect(null);
    setCorrectAnswerForFeedback(null);

    try {
      const res = await api.post<{
        session: SessionState;
        state_token: string;
        started_at_ts: number;
      }>("/api/diagnostic/start", { triggered_from: triggeredFrom });
      startTsRef.current = Date.now();
      setSession(res.session);
      setStateToken(res.state_token);
      await fetchNextQuestion(res.state_token);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Impossible de démarrer le diagnostic.");
    }
  }, [triggeredFrom, fetchNextQuestion, setErr]);

  // ---- submitAnswer ------------------------------------------------------- //

  const submitAnswer = useCallback(async () => {
    if (!stateToken || !currentQuestion || !selectedAnswer) return;

    setPhase("loading");
    try {
      const res = await api.post<{
        is_correct: boolean;
        correct_answer?: string;
        session: SessionState;
        state_token: string;
        session_complete: boolean;
      }>("/api/diagnostic/answer", {
        state_token: stateToken,
        user_answer: selectedAnswer,
      });

      setIsCorrect(res.is_correct);
      setCorrectAnswerForFeedback(res.correct_answer ?? null);
      setSession(res.session);
      setStateToken(res.state_token);
      setPhase("feedback");

      if (res.session_complete) {
        setTimeout(() => finalizeSession(res.state_token), 1800);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erreur lors de la soumission de la réponse.");
    }
  }, [stateToken, currentQuestion, selectedAnswer, finalizeSession, setErr]);

  // ---- nextQuestion ------------------------------------------------------- //

  const nextQuestion = useCallback(async () => {
    if (!stateToken) return;
    await fetchNextQuestion(stateToken);
  }, [stateToken, fetchNextQuestion]);

  // ---- public API --------------------------------------------------------- //

  return {
    // État
    phase,
    currentQuestion,
    selectedAnswer,
    isCorrect,
    correctAnswerForFeedback,
    result,
    error,
    // Actions
    startDiagnostic,
    setSelectedAnswer,
    submitAnswer,
    nextQuestion,
  };
}
