import { describe, it, expect } from "vitest";
import {
  normalizeAdminExerciseAgeGroup,
  getAdminExerciseDifficultyDisplay,
  getAdminExerciseTypeDisplay,
  getAdminExerciseAgeGroupListDisplay,
  ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL,
  ADMIN_EXERCISE_DIFFICULTY_UNKNOWN_PREFIX,
  DEFAULT_ADMIN_EXERCISE_AGE_GROUP,
} from "./adminExerciseCoherence";

describe("adminExerciseCoherence", () => {
  describe("normalizeAdminExerciseAgeGroup", () => {
    it("maps legacy underscore form to canonical option value", () => {
      expect(normalizeAdminExerciseAgeGroup("6_8")).toBe("6-8");
      expect(normalizeAdminExerciseAgeGroup("9_11")).toBe("9-11");
    });
    it("trims and preserves canonical values", () => {
      expect(normalizeAdminExerciseAgeGroup("  12-14  ")).toBe("12-14");
    });
    it("maps adult alias", () => {
      expect(normalizeAdminExerciseAgeGroup("adult")).toBe("adulte");
    });
    it("defaults when empty", () => {
      expect(normalizeAdminExerciseAgeGroup(null)).toBe(DEFAULT_ADMIN_EXERCISE_AGE_GROUP);
      expect(normalizeAdminExerciseAgeGroup("   ")).toBe(DEFAULT_ADMIN_EXERCISE_AGE_GROUP);
    });
    it("returns unknown raw for non-canonical legacy (edit UI adds hérité item)", () => {
      expect(normalizeAdminExerciseAgeGroup("8-10")).toBe("8-10");
    });
  });

  describe("getAdminExerciseDifficultyDisplay", () => {
    it("maps legacy API codes to neutral transitional levels (not Star Wars product labels)", () => {
      expect(getAdminExerciseDifficultyDisplay("PADAWAN")).toBe("Niveau 2");
      expect(getAdminExerciseDifficultyDisplay("INITIE")).toBe("Niveau 1");
      expect(getAdminExerciseDifficultyDisplay("GRAND_MAITRE")).toBe("Niveau 5");
    });
    it("case-insensitive canonical legacy codes", () => {
      expect(getAdminExerciseDifficultyDisplay("padawan")).toBe("Niveau 2");
    });
    it("prefers difficulty_tier when provided (F42 palier)", () => {
      expect(getAdminExerciseDifficultyDisplay("PADAWAN", { difficultyTier: 7 })).toBe("Palier 7");
    });
    it("ignores out-of-range tier and falls back to legacy mapping", () => {
      expect(getAdminExerciseDifficultyDisplay("PADAWAN", { difficultyTier: 99 })).toBe("Niveau 2");
    });
    it("empty", () => {
      expect(getAdminExerciseDifficultyDisplay(null)).toBe(ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL);
    });
    it("unknown uses controlled fallback with raw", () => {
      expect(getAdminExerciseDifficultyDisplay("LEGACY_X")).toContain(
        ADMIN_EXERCISE_DIFFICULTY_UNKNOWN_PREFIX
      );
      expect(getAdminExerciseDifficultyDisplay("LEGACY_X")).toContain("LEGACY_X");
    });
  });

  describe("getAdminExerciseTypeDisplay", () => {
    it("canonical admin type", () => {
      expect(getAdminExerciseTypeDisplay("ADDITION")).toBe("Addition");
    });
    it("unknown", () => {
      expect(getAdminExerciseTypeDisplay("ZZ_UNKNOWN")).toContain("Non répertorié");
      expect(getAdminExerciseTypeDisplay("ZZ_UNKNOWN")).toContain("ZZ_UNKNOWN");
    });
  });

  describe("getAdminExerciseAgeGroupListDisplay", () => {
    it("uses option label for canonical values", () => {
      expect(getAdminExerciseAgeGroupListDisplay("9-11")).toBe("9-11 ans");
    });
    it("normalizes legacy underscore values before display", () => {
      expect(getAdminExerciseAgeGroupListDisplay("6_8")).toBe("6-8 ans");
      expect(getAdminExerciseAgeGroupListDisplay("9_11")).toBe("9-11 ans");
    });
    it("preserves unknown raw values instead of using the misleading default label", () => {
      expect(getAdminExerciseAgeGroupListDisplay("8-10")).toBe("8-10");
    });
    it("empty cell", () => {
      expect(getAdminExerciseAgeGroupListDisplay(null)).toBe(ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL);
    });
  });
});
