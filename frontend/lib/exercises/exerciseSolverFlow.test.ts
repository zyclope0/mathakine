import { describe, expect, it } from "vitest";
import type { Exercise } from "@/types/api";
import type { ReviewSafeExercisePayload } from "../validation/spacedRepetitionNextReview";
import {
  buildInterleavedSessionStorageJson,
  filterExerciseChoices,
  isInterleavedSessionEndScreen,
  mergeInterleavedAnalyticsForNextStep,
  resolveDisplayExercise,
  resolveSolverExplanationText,
  spacedReviewApplyPlanFromApi,
} from "./exerciseSolverFlow";

const baseExercise: Exercise = {
  id: 10,
  title: "Std",
  question: "Q?",
  exercise_type: "ADDITION",
  difficulty: "INITIE",
  age_group: "6-8",
  difficulty_tier: null,
  choices: ["a", "b"],
  image_url: null,
  audio_url: null,
  hint: "h",
  explanation: "exp",
  correct_answer: "b",
  is_open_answer: false,
};

const reviewExercise: ReviewSafeExercisePayload = {
  id: 99,
  title: "Rev",
  question: "R?",
  exercise_type: "ADDITION",
  difficulty: "INITIE",
  age_group: "6-8",
  difficulty_tier: null,
  choices: ["1", "2"],
  image_url: null,
  audio_url: null,
};

describe("exerciseSolverFlow", () => {
  describe("resolveDisplayExercise", () => {
    it("returns review exercise in spaced-review mode", () => {
      expect(resolveDisplayExercise("spaced-review", baseExercise, reviewExercise)).toEqual(
        reviewExercise
      );
    });

    it("returns standard exercise outside spaced-review", () => {
      expect(resolveDisplayExercise(null, baseExercise, reviewExercise)).toEqual(baseExercise);
      expect(resolveDisplayExercise("interleaved", baseExercise, reviewExercise)).toEqual(
        baseExercise
      );
    });

    it("returns null when standard exercise missing", () => {
      expect(resolveDisplayExercise(null, null, null)).toBeNull();
    });
  });

  describe("filterExerciseChoices", () => {
    it("filters string choices only", () => {
      expect(filterExerciseChoices(["x", 1, "y"])).toEqual(["x", "y"]);
      expect(filterExerciseChoices(null)).toEqual([]);
    });
  });

  describe("isInterleavedSessionEndScreen", () => {
    it("is true when interleaved session completes after submit", () => {
      expect(
        isInterleavedSessionEndScreen(
          "interleaved",
          { plan: ["A", "B"], completedCount: 1, length: 2 },
          true
        )
      ).toBe(true);
      expect(
        isInterleavedSessionEndScreen(
          "interleaved",
          { plan: ["A"], completedCount: 0, length: 1 },
          true
        )
      ).toBe(true);
    });

    it("is false when not submitted or wrong mode", () => {
      expect(
        isInterleavedSessionEndScreen(
          "interleaved",
          { plan: ["A", "B"], completedCount: 0, length: 2 },
          false
        )
      ).toBe(false);
      expect(
        isInterleavedSessionEndScreen(null, { plan: ["A"], completedCount: 0, length: 1 }, true)
      ).toBe(false);
    });
  });

  describe("spacedReviewApplyPlanFromApi", () => {
    it("maps has_next with next_review", () => {
      const nr = {
        review_item_id: 1,
        exercise_id: 2,
        due_status: "due_today" as const,
        next_review_date: "2026-01-01",
        exercise: reviewExercise,
      };
      const summary = {
        f04_initialized: true,
        active_cards_count: 1,
        due_today_count: 0,
        overdue_count: 0,
        next_review_date: "2026-01-01" as const,
      };
      expect(
        spacedReviewApplyPlanFromApi({
          has_due_review: true,
          summary,
          next_review: nr,
        })
      ).toEqual({ kind: "has_next", nextReview: nr });
    });

    it("maps complete when no next review", () => {
      const summary = {
        f04_initialized: false,
        active_cards_count: 0,
        due_today_count: 0,
        overdue_count: 0,
        next_review_date: null,
      };
      expect(
        spacedReviewApplyPlanFromApi({
          has_due_review: false,
          summary,
          next_review: null,
        })
      ).toEqual({ kind: "complete" });
    });

    it("maps error on null payload", () => {
      expect(spacedReviewApplyPlanFromApi(null)).toEqual({ kind: "error" });
    });
  });

  describe("buildInterleavedSessionStorageJson", () => {
    it("serializes session fields", () => {
      const json = buildInterleavedSessionStorageJson({
        plan: ["X"],
        completedCount: 1,
        length: 3,
        analytics: { firstAttemptTracked: true },
      });
      expect(JSON.parse(json)).toEqual({
        plan: ["X"],
        completedCount: 1,
        length: 3,
        analytics: { firstAttemptTracked: true },
      });
    });
  });

  describe("mergeInterleavedAnalyticsForNextStep", () => {
    it("merges firstAttemptTracked from current storage", () => {
      const merged = mergeInterleavedAnalyticsForNextStep(
        { plan: ["a"], completedCount: 0, length: 1, analytics: {} },
        JSON.stringify({
          plan: ["a"],
          completedCount: 0,
          length: 1,
          analytics: { firstAttemptTracked: true },
        })
      );
      expect(merged.firstAttemptTracked).toBe(true);
    });
  });

  describe("resolveSolverExplanationText", () => {
    it("prefers submit explanation then exercise explanation", () => {
      expect(resolveSolverExplanationText("from submit", "from ex")).toBe("from submit");
      expect(resolveSolverExplanationText(undefined, "from ex")).toBe("from ex");
      expect(resolveSolverExplanationText(undefined, undefined)).toBe("");
    });
  });
});
