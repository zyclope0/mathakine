import { describe, expect, it, vi } from "vitest";
import { formatRecommendationReasonDisplay } from "@/hooks/useRecommendations";

describe("formatRecommendationReasonDisplay (R5)", () => {
  it("uses i18n when reason_code is set", () => {
    const t = vi.fn((key: string, values?: Record<string, string | number>) => {
      if (key === "challengeTypes.sequence") return "Suite FR";
      if (key === "codes.reco_challenge_onboarding") return `OK ${values?.challengeType ?? ""}`;
      return key;
    });
    const text = formatRecommendationReasonDisplay(
      {
        reason_code: "reco.challenge.onboarding",
        reason_params: { challenge_type: "sequence" },
        reason: "Fallback EN",
      },
      t
    );
    expect(text).toBe("OK Suite FR");
    expect(t).toHaveBeenCalledWith("challengeTypes.sequence", { default: "sequence" });
    expect(t).toHaveBeenCalledWith("codes.reco_challenge_onboarding", {
      challengeType: "Suite FR",
      default: "Fallback EN",
    });
  });

  it("falls back to reason when reason_code absent", () => {
    const t = vi.fn();
    expect(
      formatRecommendationReasonDisplay({ reason: "Legacy phrase", reason_code: undefined }, t)
    ).toBe("Legacy phrase");
    expect(t).not.toHaveBeenCalled();
  });

  it("R6 — uses i18n for reco.exercise.discovery with exerciseType + difficulty", () => {
    const t = vi.fn((key: string, values?: Record<string, unknown>) => {
      if (key === "difficulties.initie") return "Initié FR";
      if (key === "codes.reco_exercise_discovery")
        return `Découverte ${values?.exerciseType}-${values?.targetDifficulty}`;
      return key;
    });
    const getExerciseTypeLabel = vi.fn((k: string) => `LBL_${k}`);
    const text = formatRecommendationReasonDisplay(
      {
        reason_code: "reco.exercise.discovery",
        reason_params: { exercise_type: "division", target_difficulty: "initie" },
        reason: "EN fallback",
      },
      t,
      getExerciseTypeLabel
    );
    expect(text).toBe("Découverte LBL_division-Initié FR");
    expect(getExerciseTypeLabel).toHaveBeenCalledWith("division");
  });
});
