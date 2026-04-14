import { describe, expect, it } from "vitest";
import {
  buildPatchWhenGradeSystemChanges,
  formatGradeLevelReadValue,
  gradeLevelSelectOptionCount,
  isKnownLearningGoal,
  isKnownPracticeRhythm,
  resolvePreferredDifficultyReadLabel,
} from "./profileLearningPreferences";

describe("profileLearningPreferences", () => {
  describe("buildPatchWhenGradeSystemChanges", () => {
    it("clears age_group when switching to suisse", () => {
      expect(
        buildPatchWhenGradeSystemChanges(
          {
            grade_system: "unifie",
            grade_level: "5",
            age_group: "9-11",
          },
          "suisse"
        )
      ).toEqual({
        grade_system: "suisse",
        age_group: "",
        grade_level: "5",
      });
    });

    it("preserves age_group when switching to unifie", () => {
      expect(
        buildPatchWhenGradeSystemChanges(
          {
            grade_system: "suisse",
            grade_level: "5",
            age_group: "",
          },
          "unifie"
        )
      ).toEqual({
        grade_system: "unifie",
        age_group: "",
        grade_level: "5",
      });
    });

    it("clears grade_level when it exceeds new max (12 -> suisse max 11)", () => {
      expect(
        buildPatchWhenGradeSystemChanges(
          {
            grade_system: "unifie",
            grade_level: "12",
            age_group: "9-11",
          },
          "suisse"
        )
      ).toEqual({
        grade_system: "suisse",
        age_group: "",
        grade_level: "",
      });
    });

    it("keeps grade_level when within new max", () => {
      expect(
        buildPatchWhenGradeSystemChanges(
          {
            grade_system: "unifie",
            grade_level: "5",
            age_group: "9-11",
          },
          "suisse"
        )
      ).toEqual({
        grade_system: "suisse",
        age_group: "",
        grade_level: "5",
      });
    });
  });

  describe("gradeLevelSelectOptionCount", () => {
    it("returns 11 for suisse and 12 for unifie", () => {
      expect(gradeLevelSelectOptionCount("suisse")).toBe(11);
      expect(gradeLevelSelectOptionCount("unifie")).toBe(12);
    });
  });

  describe("formatGradeLevelReadValue", () => {
    it("formats suisse with H suffix", () => {
      expect(formatGradeLevelReadValue("suisse", 7)).toBe("7H");
    });

    it("formats unifie as plain number", () => {
      expect(formatGradeLevelReadValue("unifie", 5)).toBe("5");
    });

    it("returns dash when level missing", () => {
      expect(formatGradeLevelReadValue("unifie", undefined)).toBe("-");
      expect(formatGradeLevelReadValue("unifie", 0)).toBe("-");
    });
  });

  describe("resolvePreferredDifficultyReadLabel", () => {
    it("uses getAgeDisplay for known age groups", () => {
      expect(resolvePreferredDifficultyReadLabel("9-11", (g) => `lbl:${g}`)).toBe("lbl:9-11");
    });

    it("returns raw value for unknown codes", () => {
      expect(resolvePreferredDifficultyReadLabel("custom", () => "")).toBe("custom");
    });

    it("returns dash when empty", () => {
      expect(resolvePreferredDifficultyReadLabel("", () => "")).toBe("-");
      expect(resolvePreferredDifficultyReadLabel(undefined, () => "")).toBe("-");
    });
  });

  describe("isKnownLearningGoal / isKnownPracticeRhythm", () => {
    it("recognises canonical goal and rhythm codes", () => {
      expect(isKnownLearningGoal("progresser")).toBe(true);
      expect(isKnownLearningGoal("unknown")).toBe(false);
      expect(isKnownPracticeRhythm("20min_jour")).toBe(true);
      expect(isKnownPracticeRhythm("nope")).toBe(false);
    });
  });
});
