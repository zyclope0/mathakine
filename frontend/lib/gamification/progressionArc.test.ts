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
  cartographer: "Cartographe",
  commander: "Commandant",
  stellar_archivist: "Archiviste stellaire",
  cosmic_legend: "Légende cosmique",
};

describe("progressionArc", () => {
  it("expose 8 paliers alignés sur le ladder public complet", () => {
    expect(PROGRESSION_ARC_NODE_COUNT).toBe(8);
    expect(PROGRESSION_ARC_VISIBLE_BUCKETS).toEqual([
      "cadet",
      "scout",
      "explorer",
      "navigator",
      "cartographer",
      "commander",
      "stellar_archivist",
      "cosmic_legend",
    ]);
  });

  it("rang vide → cadet canonique", () => {
    expect(canonicalRankFromGamificationLevelPayload("")).toBe("cadet");
  });

  it("mappe explorer → nœud explorer courant, suivants à venir", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "explorer",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes).toHaveLength(8);
    expect(nodes.map((n) => n.state)).toEqual([
      "completed",
      "completed",
      "current",
      "upcoming",
      "upcoming",
      "upcoming",
      "upcoming",
      "upcoming",
    ]);
    expect(progressionArcAriaStepNumber(nodes)).toBe(3);
  });

  it("commander → cinquième palier courant", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "commander",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes[5]?.state).toBe("current");
    expect(progressionArcAriaStepNumber(nodes)).toBe(6);
  });

  it("cosmic_legend → dernier palier courant, rangs précédents complétés", () => {
    const nodes = buildProgressionArcNodes({
      canonicalUserRank: "cosmic_legend",
      labelForBucket: (id) => labels[id] ?? id,
    });
    expect(nodes.slice(0, 7).every((n) => n.state === "completed")).toBe(true);
    expect(nodes[7]?.state).toBe("current");
    expect(progressionArcAriaStepNumber(nodes)).toBe(8);
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
