import { describe, expect, it } from "vitest";
import {
  getCommandBarInteractionModeFlags,
  parseDeductionAssociationParts,
} from "./challengeSolverCommandBar";

describe("challengeSolverCommandBar", () => {
  describe("getCommandBarInteractionModeFlags", () => {
    it("detects order puzzle branch", () => {
      expect(
        getCommandBarInteractionModeFlags({
          responseMode: "interactive_order",
          challengeType: "PUZZLE",
          userAnswer: "",
          hasVisualData: false,
          puzzleOrderLength: 2,
        })
      ).toEqual({
        isOrderPuzzle: true,
        isGridSequence: false,
        isGridPattern: false,
        isGridDeduction: false,
      });
    });

    it("does not treat puzzle as order when puzzleOrder empty", () => {
      expect(
        getCommandBarInteractionModeFlags({
          responseMode: "interactive_order",
          challengeType: "puzzle",
          userAnswer: "",
          hasVisualData: false,
          puzzleOrderLength: 0,
        }).isOrderPuzzle
      ).toBe(false);
    });

    it("detects grid sequence when answer and visual data present", () => {
      expect(
        getCommandBarInteractionModeFlags({
          responseMode: "interactive_grid",
          challengeType: "sequence",
          userAnswer: "1,2,3",
          hasVisualData: true,
          puzzleOrderLength: 0,
        })
      ).toEqual({
        isOrderPuzzle: false,
        isGridSequence: true,
        isGridPattern: false,
        isGridDeduction: false,
      });
    });

    it("detects grid pattern branch", () => {
      expect(
        getCommandBarInteractionModeFlags({
          responseMode: "interactive_grid",
          challengeType: "pattern",
          userAnswer: "x",
          hasVisualData: true,
          puzzleOrderLength: 0,
        }).isGridPattern
      ).toBe(true);
    });

    it("detects grid deduction without requiring userAnswer", () => {
      expect(
        getCommandBarInteractionModeFlags({
          responseMode: "interactive_grid",
          challengeType: "deduction",
          userAnswer: "",
          hasVisualData: true,
          puzzleOrderLength: 0,
        }).isGridDeduction
      ).toBe(true);
    });
  });

  describe("parseDeductionAssociationParts", () => {
    it("splits colon-separated association", () => {
      expect(parseDeductionAssociationParts("A:B:C")).toEqual({
        left: "A",
        rights: ["B", "C"],
      });
    });

    it("handles empty rights", () => {
      expect(parseDeductionAssociationParts("solo")).toEqual({
        left: "solo",
        rights: [],
      });
    });
  });
});
