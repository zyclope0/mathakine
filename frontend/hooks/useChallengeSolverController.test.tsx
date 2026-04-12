import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useChallengeSolverController } from "@/hooks/useChallengeSolverController";
import type { Challenge, ChallengeAttemptResponse } from "@/types/api";

function baseChallenge(partial: Partial<Challenge> = {}): Challenge {
  return {
    id: 42,
    title: "Defi de test",
    description: "Une description",
    challenge_type: "visual",
    age_group: "9-11",
    response_mode: "interactive_visual",
    choices: null,
    hints: null,
    visual_data: {
      shapes: ["cercle rouge", "carre bleu", "triangle vert"],
    },
    correct_answer: "Position 1: cercle rouge, Position 2: carre bleu",
    ...partial,
  } as Challenge;
}

function createSubmitResult(
  overrides: Partial<ChallengeAttemptResponse> = {}
): ChallengeAttemptResponse {
  return {
    is_correct: false,
    points_earned: 0,
    total_points: 0,
    current_streak: 0,
    correct_answer: "",
    explanation: "",
    performance_stats: undefined,
    badge_unlocked: undefined,
    ...overrides,
  } as ChallengeAttemptResponse;
}

describe("useChallengeSolverController", () => {
  it("resets visual selections and retry key on retry for multi-position visual challenges", async () => {
    const challenge = baseChallenge();
    const submitAnswer = vi.fn(async () => createSubmitResult());
    const getHint = vi.fn(async () => []);
    const setHints = vi.fn();

    const { result } = renderHook(() =>
      useChallengeSolverController({
        challengeId: challenge.id,
        challenge,
        submitAnswer,
        isSubmitting: false,
        submitResult: undefined,
        getHint,
        setHints,
      })
    );

    expect(result.current.retryKey).toBe(0);

    act(() => {
      result.current.setVisualSelections({
        1: "cercle rouge",
        2: "carre bleu",
      });
    });

    await waitFor(() => {
      expect(result.current.userAnswer).toContain("Position 1");
      expect(result.current.userAnswer).toContain("Position 2");
    });

    act(() => {
      result.current.handleRetry();
    });

    await waitFor(() => {
      expect(result.current.userAnswer).toBe("");
      expect(result.current.visualSelections).toEqual({});
      expect(result.current.retryKey).toBe(1);
    });
  });
});
