import { describe, expect, it } from "vitest";
import {
  GRADE_SYSTEMS,
  LEARNING_GOALS,
  PRACTICE_RHYTHMS,
  VALID_PROFILE_THEMES,
  formatProfileDate,
  migrateLegacyTheme,
  safeProfileTheme,
  validateEmailFormat,
  validatePasswordFields,
} from "./profilePage";

describe("profilePage helpers", () => {
  describe("migrateLegacyTheme", () => {
    it("maps neutral to dune", () => {
      expect(migrateLegacyTheme("neutral")).toBe("dune");
    });

    it("maps peach to aurora", () => {
      expect(migrateLegacyTheme("peach")).toBe("aurora");
    });

    it("keeps current themes unchanged", () => {
      expect(migrateLegacyTheme("spatial")).toBe("spatial");
      expect(migrateLegacyTheme("ocean")).toBe("ocean");
    });

    it("falls back to spatial for nullish values", () => {
      expect(migrateLegacyTheme(null)).toBe("spatial");
      expect(migrateLegacyTheme(undefined)).toBe("spatial");
    });
  });

  describe("safeProfileTheme", () => {
    it("returns valid themes unchanged", () => {
      for (const theme of VALID_PROFILE_THEMES) {
        expect(safeProfileTheme(theme)).toBe(theme);
      }
    });

    it("falls back to spatial for unknown themes", () => {
      expect(safeProfileTheme("rainbow")).toBe("spatial");
    });
  });

  describe("validateEmailFormat", () => {
    it("requires a non-empty email", () => {
      expect(validateEmailFormat("")).toBe("emailRequired");
      expect(validateEmailFormat("   ")).toBe("emailRequired");
    });

    it("rejects malformed emails", () => {
      expect(validateEmailFormat("notanemail")).toBe("emailInvalid");
      expect(validateEmailFormat("missing@")).toBe("emailInvalid");
      expect(validateEmailFormat("@nodomain.com")).toBe("emailInvalid");
    });

    it("accepts valid emails", () => {
      expect(validateEmailFormat("user@example.com")).toBeNull();
      expect(validateEmailFormat("a@b.co")).toBeNull();
    });
  });

  describe("validatePasswordFields", () => {
    it("returns no errors for valid values", () => {
      expect(
        validatePasswordFields({
          current_password: "oldpass123",
          new_password: "newpass123",
          confirm_password: "newpass123",
        })
      ).toEqual({});
    });

    it("requires current password", () => {
      expect(
        validatePasswordFields({
          current_password: "",
          new_password: "newpass123",
          confirm_password: "newpass123",
        }).current_password
      ).toBe("currentPasswordRequired");
    });

    it("requires new password", () => {
      expect(
        validatePasswordFields({
          current_password: "oldpass123",
          new_password: "",
          confirm_password: "",
        }).new_password
      ).toBe("newPasswordRequired");
    });

    it("enforces a minimum length of 8 characters", () => {
      expect(
        validatePasswordFields({
          current_password: "oldpass123",
          new_password: "short",
          confirm_password: "short",
        }).new_password
      ).toBe("passwordMinLength");
    });

    it("requires password confirmation", () => {
      expect(
        validatePasswordFields({
          current_password: "oldpass123",
          new_password: "newpass123",
          confirm_password: "",
        }).confirm_password
      ).toBe("confirmPasswordRequired");
    });

    it("rejects mismatched confirmation", () => {
      expect(
        validatePasswordFields({
          current_password: "oldpass123",
          new_password: "newpass123",
          confirm_password: "different",
        }).confirm_password
      ).toBe("passwordMismatch");
    });
  });

  describe("formatProfileDate", () => {
    it("returns '-' for nullish values", () => {
      expect(formatProfileDate(null)).toBe("-");
      expect(formatProfileDate(undefined)).toBe("-");
    });

    it("formats valid ISO dates", () => {
      const result = formatProfileDate("2025-03-15T00:00:00Z");
      expect(result).toContain("15");
      expect(result).toContain("2025");
    });

    it("returns the raw value for invalid dates", () => {
      expect(formatProfileDate("not-a-date")).toBe("not-a-date");
    });
  });

  describe("domain constants", () => {
    it("keeps the expected grade systems", () => {
      expect(GRADE_SYSTEMS).toEqual(["suisse", "unifie"]);
    });

    it("keeps the expected learning goals and rhythms", () => {
      expect(LEARNING_GOALS).toHaveLength(5);
      expect(PRACTICE_RHYTHMS).toHaveLength(5);
      expect(VALID_PROFILE_THEMES).toHaveLength(8);
    });
  });
});
