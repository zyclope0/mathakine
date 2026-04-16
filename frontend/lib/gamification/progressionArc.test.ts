import { describe, expect, it } from "vitest";
import {
  buildProgressionArcNodes,
  canonicalRankFromGamificationLevelPayload,
  PROGRESSION_ARC_NODE_COUNT,
  PROGRESSION_ARC_VISIBLE_BUCKETS,
  progressionArcAriaStepNumber,
} from "@/lib/gamification/progressionArc";

const labels: Record<string, string> = {
  cadet: "Cadet",
  scout: "Scout",
  explorer: "Explorateur",
  navigator: "Navigateur",
};

describe("progressionArc", () => {
  it("expose 4 paliers MVP alignés sur le ladder public", () => {
    expect(PROGRESSION_ARC_NODE_COUNT).toBe(4);
    expect(PROGRESSION_ARC_VISIBLE_BUCKETS).toEqual(["cadet", "scout", "explorer", "navigator"]);
  });

  it("rang vide → cadet canonique", () => {
    expect(canonicalRankFromGamificationLevelPayload("")).toBe("cadet");
  });

  it("mappe explorer → nœud explorer courant, suivants à venir", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "explorer",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes.map((n) => n.state)).toEqual(["completed", "completed", "current", "upcoming"]);
    expect(progressionArcAriaStepNumber(nodes)).toBe(3);
  });

  it("rang au-delà du dernier nœud visible → tout complété", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "commander",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes.every((n) => n.state === "completed")).toBe(true);
    expect(progressionArcAriaStepNumber(nodes)).toBe(4);
  });

  it("cadet → premier palier courant", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "cadet",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes[0]?.state).toBe("current");
    expect(progressionArcAriaStepNumber(nodes)).toBe(1);
  });
});
