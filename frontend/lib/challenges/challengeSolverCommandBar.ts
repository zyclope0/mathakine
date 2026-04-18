/**
 * Pure helpers for ChallengeSolver command bar branch selection (FFI-L18B).
 * No React; mirrors previous inline derivations in ChallengeSolverCommandBar.
 */

import type { ChallengeResponseMode } from "@/types/api";

export interface CommandBarModeInput {
  responseMode: ChallengeResponseMode;
  challengeType: string;
  userAnswer: string;
  hasVisualData: boolean;
  puzzleOrderLength: number;
}

export interface CommandBarModeFlags {
  isOrderPuzzle: boolean;
  isGridSequence: boolean;
  isGridPattern: boolean;
  isGridDeduction: boolean;
}

export function getCommandBarInteractionModeFlags(input: CommandBarModeInput): CommandBarModeFlags {
  const type = input.challengeType.toLowerCase();
  return {
    isOrderPuzzle:
      input.responseMode === "interactive_order" &&
      type === "puzzle" &&
      input.puzzleOrderLength > 0,
    isGridSequence:
      input.responseMode === "interactive_grid" &&
      type === "sequence" &&
      Boolean(input.userAnswer) &&
      input.hasVisualData,
    isGridPattern:
      input.responseMode === "interactive_grid" && type === "pattern" && input.hasVisualData,
    isGridDeduction:
      input.responseMode === "interactive_grid" && type === "deduction" && input.hasVisualData,
  };
}

/** Split "a:b:c" style deduction row for display (left badge + right badges). */
export function parseDeductionAssociationParts(association: string): {
  left: string;
  rights: string[];
} {
  const parts = association.split(":");
  return {
    left: parts[0] ?? "",
    rights: parts.slice(1),
  };
}
