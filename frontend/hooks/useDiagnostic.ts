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
  correct_answer: string;
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
  const [session, setSession] = useState<SessionState | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<DiagnosticQuestion | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Timestamps pour mesurer la durée totale
  const startTsRef = useRef<number>(0);

  // ---- helpers internes -------------------------------------------------- //

  const setErr = useCallback((msg: string) => {
    setError(msg);
    setPhase("error");
  }, []);

  // ---- fetchNextQuestion -------------------------------------------------- //

  const fetchNextQuestion = useCallback(async (currentSession: SessionState) => {
    setPhase("loading");
    try {
      const res = await api.post<{ done: boolean; question?: DiagnosticQuestion }>(
        "/api/diagnostic/question",
        { session: currentSession }
      );
      if (res.done) {
        // Session terminée côté backend — on finalise
        await finalizeSession(currentSession);
      } else if (res.question) {
        setCurrentQuestion(res.question);
        setSelectedAnswer(null);
        setIsCorrect(null);
        setPhase("question");
      } else {
        setErr("Aucune question retournée par le serveur.");
      }
    } catch (e) {
      setErr(
        e instanceof Error ? e.message : "Erreur réseau lors de la génération de la question."
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---- finalizeSession ---------------------------------------------------- //

  const finalizeSession = useCallback(async (currentSession: SessionState) => {
    setPhase("loading");
    const durationSeconds = Math.round((Date.now() - startTsRef.current) / 1000);
    try {
      const res = await api.post<{ success: boolean; result?: DiagnosticResult; error?: string }>(
        "/api/diagnostic/complete",
        { session: currentSession, duration_seconds: durationSeconds }
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
  }, []);

  // ---- start -------------------------------------------------------------- //

  const startDiagnostic = useCallback(async () => {
    setPhase("loading");
    setError(null);
    setResult(null);
    setSession(null);
    setCurrentQuestion(null);
    setSelectedAnswer(null);
    setIsCorrect(null);

    try {
      const res = await api.post<{ session: SessionState; started_at_ts: number }>(
        "/api/diagnostic/start",
        { triggered_from: triggeredFrom }
      );
      startTsRef.current = Date.now();
      setSession(res.session);
      await fetchNextQuestion(res.session);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Impossible de démarrer le diagnostic.");
    }
  }, [triggeredFrom, fetchNextQuestion, setErr]);

  // ---- submitAnswer ------------------------------------------------------- //

  const submitAnswer = useCallback(async () => {
    if (!session || !currentQuestion || !selectedAnswer) return;

    setPhase("loading");
    try {
      const res = await api.post<{
        is_correct: boolean;
        session: SessionState;
        session_complete: boolean;
      }>("/api/diagnostic/answer", {
        session,
        exercise_type: currentQuestion.exercise_type,
        user_answer: selectedAnswer,
        correct_answer: currentQuestion.correct_answer,
      });

      setIsCorrect(res.is_correct);
      setSession(res.session);
      setPhase("feedback");

      if (res.session_complete) {
        // On affiche le feedback brièvement puis finalise
        setTimeout(() => finalizeSession(res.session), 1800);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erreur lors de la soumission de la réponse.");
    }
  }, [session, currentQuestion, selectedAnswer, finalizeSession, setErr]);

  // ---- nextQuestion ------------------------------------------------------- //

  const nextQuestion = useCallback(async () => {
    if (!session) return;
    await fetchNextQuestion(session);
  }, [session, fetchNextQuestion]);

  // ---- public API --------------------------------------------------------- //

  return {
    // État
    phase,
    currentQuestion,
    selectedAnswer,
    isCorrect,
    result,
    error,
    // Actions
    startDiagnostic,
    setSelectedAnswer,
    submitAnswer,
    nextQuestion,
  };
}
