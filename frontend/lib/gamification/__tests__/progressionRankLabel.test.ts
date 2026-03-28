import { describe, expect, it } from "vitest";
import { readPublicProgressionRankRaw } from "@/lib/gamification/progressionRankLabel";

describe("readPublicProgressionRankRaw (F43-A3)", () => {
  it("prefers progression_rank over jedi_rank", () => {
    expect(
      readPublicProgressionRankRaw({
        progression_rank: "explorer",
        jedi_rank: "cadet",
      })
    ).toBe("explorer");
  });

  it("falls back to jedi_rank", () => {
    expect(readPublicProgressionRankRaw({ jedi_rank: "navigator" })).toBe("navigator");
  });

  it("returns empty string when both missing", () => {
    expect(readPublicProgressionRankRaw({})).toBe("");
  });
});
