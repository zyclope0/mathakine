import { describe, it, expect } from "vitest";
import {
  partitionSymmetryLayoutBySide,
  stableSortSymmetryLayoutCells,
} from "@/components/challenges/visualizations/VisualRenderer";

describe("VisualRenderer symmetry layout (IA9b)", () => {
  it("partitionne N cellules par côté (plus de plafond 5/5)", () => {
    const left = Array.from({ length: 7 }, (_, i) => ({
      side: "left",
      position: i,
      shape: "cercle",
    }));
    const right = Array.from({ length: 7 }, (_, i) => ({
      side: "right",
      position: i,
      shape: i === 6 ? "?" : "triangle",
      question: i === 6,
    }));
    const layout = [...left, ...right];
    const { left: L, right: R } = partitionSymmetryLayoutBySide(layout);
    expect(L.length).toBe(7);
    expect(R.length).toBe(7);
  });

  it("stableSortSymmetryLayoutCells respecte position puis ordre d'origine", () => {
    const items = [
      { side: "left", position: 2, shape: "b" },
      { side: "left", position: 0, shape: "a" },
      { side: "left", shape: "c" },
    ];
    const sorted = stableSortSymmetryLayoutCells(items);
    expect(sorted.map((x) => x.shape)).toEqual(["a", "b", "c"]);
  });
});
