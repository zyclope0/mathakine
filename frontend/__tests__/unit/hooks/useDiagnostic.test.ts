/**
 * Unit tests for useDiagnostic (TEST-DIAGNOSTIC-HOOK-01) — API mocked, no UI.
 */

import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api/client";
import { useDiagnostic } from "@/hooks/useDiagnostic";
import type { DiagnosticQuestion, DiagnosticResult } from "@/hooks/useDiagnostic";

vi.mock("@/lib/api/client", () => ({
  api: {
    post: vi.fn(),
  },
}));

const mockPost = vi.mocked(api.post);

const question1: DiagnosticQuestion = {
  exercise_type: "addition",
  difficulty: "INITIE",
  level_ordinal: 1,
  question: "2+2?",
  choices: ["4", "5"],
  explanation: "ex",
  hint: "",
  question_number: 1,
  max_questions: 10,
  types_remaining: 3,
};

const question2: DiagnosticQuestion = {
  ...question1,
  question_number: 2,
  question: "3+3?",
};

const startPayload = {
  session: { k: 1 },
  state_token: "tok-start",
  started_at_ts: 1_700_000_000,
};

const mockResult: DiagnosticResult = {
  id: 42,
  completed_at: "2026-01-15T12:00:00Z",
  triggered_from: "onboarding",
  questions_asked: 5,
  duration_seconds: 12,
  scores: {
    addition: { level: 1, difficulty: "INITIE", correct: 3, total: 5 },
  },
};

async function startWithFirstQuestion(triggeredFrom: "onboarding" | "settings" = "onboarding") {
  mockPost.mockResolvedValueOnce(startPayload).mockResolvedValueOnce({
    done: false,
    question: question1,
    state_token: "tok-q1",
  });
  const hook = renderHook(() => useDiagnostic(triggeredFrom));
  await act(async () => {
    await hook.result.current.startDiagnostic();
  });
  return hook;
}

describe("useDiagnostic", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("démarrage réussi : POST /start puis /question, phase question et currentQuestion", async () => {
    const { result } = await startWithFirstQuestion();

    expect(mockPost).toHaveBeenNthCalledWith(1, "/api/diagnostic/start", {
      triggered_from: "onboarding",
    });
    expect(mockPost).toHaveBeenNthCalledWith(2, "/api/diagnostic/question", {
      state_token: "tok-start",
    });
    expect(result.current.phase).toBe("question");
    expect(result.current.currentQuestion).toEqual(question1);
    expect(result.current.error).toBeNull();
  });

  it("démarrage : triggered_from settings est transmis à /start", async () => {
    mockPost
      .mockResolvedValueOnce(startPayload)
      .mockResolvedValueOnce({ done: false, question: question1, state_token: "t1" });
    const { result } = renderHook(() => useDiagnostic("settings"));
    await act(async () => {
      await result.current.startDiagnostic();
    });
    expect(mockPost).toHaveBeenNthCalledWith(1, "/api/diagnostic/start", {
      triggered_from: "settings",
    });
  });

  it("démarrage échoué : erreur sur /start → phase error et message", async () => {
    mockPost.mockRejectedValueOnce(new Error("connexion refusée"));
    const { result } = renderHook(() => useDiagnostic());
    await act(async () => {
      await result.current.startDiagnostic();
    });
    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("connexion refusée");
  });

  it("nextQuestion : recharge une question et réinitialise sélection / feedback", async () => {
    const { result } = await startWithFirstQuestion();
    expect(result.current.selectedAnswer).toBeNull();

    act(() => {
      result.current.setSelectedAnswer("4");
    });
    expect(result.current.selectedAnswer).toBe("4");

    mockPost.mockResolvedValueOnce({
      done: false,
      question: question2,
      state_token: "tok-q2",
    });
    await act(async () => {
      await result.current.nextQuestion();
    });

    expect(mockPost).toHaveBeenLastCalledWith("/api/diagnostic/question", {
      state_token: "tok-q1",
    });
    expect(result.current.phase).toBe("question");
    expect(result.current.currentQuestion).toEqual(question2);
    expect(result.current.selectedAnswer).toBeNull();
    expect(result.current.isCorrect).toBeNull();
    expect(result.current.correctAnswerForFeedback).toBeNull();
  });

  it("submitAnswer non final : phase feedback, isCorrect et correctAnswerForFeedback", async () => {
    const { result } = await startWithFirstQuestion();
    act(() => {
      result.current.setSelectedAnswer("4");
    });
    mockPost.mockResolvedValueOnce({
      is_correct: true,
      correct_answer: "4",
      session: { x: 1 },
      state_token: "tok-after-answer",
      session_complete: false,
    });
    await act(async () => {
      await result.current.submitAnswer();
    });
    expect(mockPost).toHaveBeenCalledWith("/api/diagnostic/answer", {
      state_token: "tok-q1",
      user_answer: "4",
    });
    expect(result.current.phase).toBe("feedback");
    expect(result.current.isCorrect).toBe(true);
    expect(result.current.correctAnswerForFeedback).toBe("4");
  });

  it("submitAnswer final : après 1800 ms, POST /complete puis phase results et result", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] });
    const setTimeoutSpy = vi.spyOn(globalThis, "setTimeout");
    const { result } = await startWithFirstQuestion();
    act(() => {
      result.current.setSelectedAnswer("5");
    });

    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "4",
      session: {},
      state_token: "tok-final",
      session_complete: true,
    });
    mockPost.mockResolvedValueOnce({
      success: true,
      result: mockResult,
    });

    await act(async () => {
      await result.current.submitAnswer();
    });
    expect(result.current.phase).toBe("feedback");
    expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 1800);
    setTimeoutSpy.mockRestore();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1800);
    });
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.phase).toBe("results");
    expect(mockPost).toHaveBeenCalledWith(
      "/api/diagnostic/complete",
      expect.objectContaining({
        state_token: "tok-final",
      })
    );
    expect(result.current.result).toEqual(mockResult);
    expect(result.current.error).toBeNull();
  });

  it("finalisation : success false → phase error et message serveur", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] });
    const { result } = await startWithFirstQuestion();
    act(() => {
      result.current.setSelectedAnswer("5");
    });
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "4",
      session: {},
      state_token: "tok-x",
      session_complete: true,
    });
    mockPost.mockResolvedValueOnce({
      success: false,
      error: "Session invalide",
    });

    await act(async () => {
      await result.current.submitAnswer();
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1800);
    });
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("Session invalide");
  });

  it("finalisation : exception sur /complete → phase error", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "Date"] });
    const { result } = await startWithFirstQuestion();
    act(() => {
      result.current.setSelectedAnswer("4");
    });
    mockPost.mockResolvedValueOnce({
      is_correct: true,
      session: {},
      state_token: "tok-y",
      session_complete: true,
    });
    mockPost.mockRejectedValueOnce(new Error("timeout réseau"));

    await act(async () => {
      await result.current.submitAnswer();
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1800);
    });
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("timeout réseau");
  });

  it("fetchNextQuestion : done true → finalisation immédiate puis phase results", async () => {
    const { result } = renderHook(() => useDiagnostic());
    mockPost
      .mockResolvedValueOnce(startPayload)
      .mockResolvedValueOnce({ done: true, state_token: "tok-complete" })
      .mockResolvedValueOnce({
        success: true,
        result: mockResult,
      });

    await act(async () => {
      await result.current.startDiagnostic();
    });

    expect(mockPost).toHaveBeenNthCalledWith(1, "/api/diagnostic/start", {
      triggered_from: "onboarding",
    });
    expect(mockPost).toHaveBeenNthCalledWith(2, "/api/diagnostic/question", {
      state_token: "tok-start",
    });
    expect(mockPost).toHaveBeenNthCalledWith(
      3,
      "/api/diagnostic/complete",
      expect.objectContaining({
        state_token: "tok-complete",
      })
    );
    expect(result.current.phase).toBe("results");
    expect(result.current.result).toEqual(mockResult);
  });

  it("fetchNextQuestion : réponse sans question ni done → phase error", async () => {
    mockPost
      .mockResolvedValueOnce(startPayload)
      .mockResolvedValueOnce({ done: false, state_token: "bad" });
    const { result } = renderHook(() => useDiagnostic());
    await act(async () => {
      await result.current.startDiagnostic();
    });
    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("Aucune question retournée par le serveur.");
  });

  it("fetchNextQuestion : exception sur /question → phase error", async () => {
    mockPost
      .mockResolvedValueOnce(startPayload)
      .mockRejectedValueOnce(new Error("502 Bad Gateway"));
    const { result } = renderHook(() => useDiagnostic());
    await act(async () => {
      await result.current.startDiagnostic();
    });
    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("502 Bad Gateway");
  });

  it("submitAnswer : exception sur /answer → phase error", async () => {
    const { result } = await startWithFirstQuestion();
    act(() => {
      result.current.setSelectedAnswer("4");
    });
    mockPost.mockRejectedValueOnce(new Error("answer failed"));
    await act(async () => {
      await result.current.submitAnswer();
    });
    expect(result.current.phase).toBe("error");
    expect(result.current.error).toBe("answer failed");
  });
});
