import { describe, it, expect } from "vitest";
import {
  resolveChallengeResponseMode,
  isChallengeResponseMode,
} from "./resolveChallengeResponseMode";
import type { Challenge } from "@/types/api";

function minimalChallenge(partial: Partial<Challenge>): Challenge {
  return {
    id: 1,
    title: "t",
    description: "d".repeat(12),
    challenge_type: "visual",
    age_group: "9-11",
    ...partial,
  } as Challenge;
}

describe("resolveChallengeResponseMode (IA9)", () => {
  it("utilise response_mode API quand valide", () => {
    expect(
      resolveChallengeResponseMode(minimalChallenge({ response_mode: "interactive_visual" }))
    ).toBe("interactive_visual");
  });

  it("retombe sur open_text si valeur inconnue", () => {
    expect(resolveChallengeResponseMode(minimalChallenge({ response_mode: "bogus" }))).toBe(
      "open_text"
    );
  });

  it("open_text si absent (legacy)", () => {
    expect(resolveChallengeResponseMode(minimalChallenge({}))).toBe("open_text");
  });

  it("isChallengeResponseMode", () => {
    expect(isChallengeResponseMode("single_choice")).toBe(true);
    expect(isChallengeResponseMode(null)).toBe(false);
  });
});
