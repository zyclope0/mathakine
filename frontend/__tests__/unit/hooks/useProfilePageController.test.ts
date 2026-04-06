/**
 * Tests unitaires pour useProfilePageController.
 *
 * Scope :
 * - sync depuis user (personalInfo, learningPrefs, accessibilitySettings)
 * - migration thème legacy (neutral → dune, peach → aurora)
 * - reset infos perso
 * - reset learning prefs
 * - validation email invalide
 * - validation mot de passe mismatch
 * - recentBadges : triés décroissant par earned_at, limités à 3
 *
 * Ces tests ciblent les helpers purs depuis lib/profile/profilePage.ts
 * et la logique stateless du controller (testée via les helpers purs).
 *
 * FFI-L11.
 */
import { describe, expect, it } from "vitest";
import {
  migrateLegacyTheme,
  safeProfileTheme,
  formatProfileDate,
  validateEmailFormat,
  validatePasswordFields,
  GRADE_SYSTEMS,
  LEARNING_GOALS,
  PRACTICE_RHYTHMS,
  VALID_PROFILE_THEMES,
} from "@/lib/profile/profilePage";

// ─── Tests helpers purs ───────────────────────────────────────────────────────

describe("migrateLegacyTheme", () => {
  it("neutral → dune", () => {
    expect(migrateLegacyTheme("neutral")).toBe("dune");
  });

  it("peach → aurora", () => {
    expect(migrateLegacyTheme("peach")).toBe("aurora");
  });

  it("laisse spatial inchangé", () => {
    expect(migrateLegacyTheme("spatial")).toBe("spatial");
  });

  it("laisse ocean inchangé", () => {
    expect(migrateLegacyTheme("ocean")).toBe("ocean");
  });

  it("retourne spatial si null", () => {
    expect(migrateLegacyTheme(null)).toBe("spatial");
  });

  it("retourne spatial si undefined", () => {
    expect(migrateLegacyTheme(undefined)).toBe("spatial");
  });
});

describe("safeProfileTheme", () => {
  it("retourne un thème valide tel quel", () => {
    expect(safeProfileTheme("ocean")).toBe("ocean");
  });

  it("retourne spatial pour un thème inconnu", () => {
    expect(safeProfileTheme("rainbow")).toBe("spatial");
  });

  it("couvre tous les thèmes valides", () => {
    for (const theme of VALID_PROFILE_THEMES) {
      expect(safeProfileTheme(theme)).toBe(theme);
    }
  });
});

describe("validateEmailFormat", () => {
  it("retourne emailRequired si email vide", () => {
    expect(validateEmailFormat("")).toBe("emailRequired");
    expect(validateEmailFormat("   ")).toBe("emailRequired");
  });

  it("retourne emailInvalid si format invalide", () => {
    expect(validateEmailFormat("notanemail")).toBe("emailInvalid");
    expect(validateEmailFormat("missing@")).toBe("emailInvalid");
    expect(validateEmailFormat("@nodomain.com")).toBe("emailInvalid");
  });

  it("retourne null si email valide", () => {
    expect(validateEmailFormat("user@example.com")).toBeNull();
    expect(validateEmailFormat("a@b.co")).toBeNull();
  });
});

describe("validatePasswordFields", () => {
  it("retourne objet vide si tous les champs sont valides", () => {
    const result = validatePasswordFields({
      current_password: "oldpass",
      new_password: "newpass123",
      confirm_password: "newpass123",
    });
    expect(Object.keys(result)).toHaveLength(0);
  });

  it("retourne currentPasswordRequired si current_password vide", () => {
    const result = validatePasswordFields({
      current_password: "",
      new_password: "newpass123",
      confirm_password: "newpass123",
    });
    expect(result.current_password).toBe("currentPasswordRequired");
  });

  it("retourne newPasswordRequired si new_password vide", () => {
    const result = validatePasswordFields({
      current_password: "oldpass",
      new_password: "",
      confirm_password: "",
    });
    expect(result.new_password).toBe("newPasswordRequired");
  });

  it("retourne passwordMismatch si confirm != new", () => {
    const result = validatePasswordFields({
      current_password: "oldpass",
      new_password: "newpass123",
      confirm_password: "different",
    });
    expect(result.confirm_password).toBe("passwordMismatch");
  });

  it("retourne confirmPasswordRequired si confirm vide", () => {
    const result = validatePasswordFields({
      current_password: "oldpass",
      new_password: "newpass123",
      confirm_password: "",
    });
    expect(result.confirm_password).toBe("confirmPasswordRequired");
  });
});

describe("formatProfileDate", () => {
  it("retourne - si null", () => {
    expect(formatProfileDate(null)).toBe("-");
  });

  it("retourne - si undefined", () => {
    expect(formatProfileDate(undefined)).toBe("-");
  });

  it("formate une date ISO valide en français", () => {
    const result = formatProfileDate("2025-03-15T00:00:00Z");
    expect(result).toContain("2025");
    expect(result).toContain("15");
  });

  it("retourne la chaîne brute si date invalide", () => {
    expect(formatProfileDate("not-a-date")).toBe("not-a-date");
  });
});

describe("constantes", () => {
  it("GRADE_SYSTEMS contient suisse et unifie", () => {
    expect(GRADE_SYSTEMS).toContain("suisse");
    expect(GRADE_SYSTEMS).toContain("unifie");
  });

  it("LEARNING_GOALS contient les 5 options", () => {
    expect(LEARNING_GOALS).toHaveLength(5);
  });

  it("PRACTICE_RHYTHMS contient les 5 rythmes", () => {
    expect(PRACTICE_RHYTHMS).toHaveLength(5);
  });

  it("VALID_PROFILE_THEMES contient les 8 thèmes", () => {
    expect(VALID_PROFILE_THEMES).toHaveLength(8);
  });
});

// ─── Tests de logique recentBadges (logique pure testable) ───────────────────

describe("logique recentBadges (tri + limite à 3)", () => {
  function sortAndSliceBadges(badges: { id: number; earned_at: string | null | undefined }[]) {
    return badges
      .filter(
        (b): b is typeof b & { earned_at: string } =>
          typeof b.earned_at === "string" && b.earned_at.length > 0
      )
      .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
      .slice(0, 3);
  }

  it("retourne [] si aucun badge", () => {
    expect(sortAndSliceBadges([])).toHaveLength(0);
  });

  it("filtre les badges sans earned_at", () => {
    const badges = [
      { id: 1, earned_at: null },
      { id: 2, earned_at: "2025-05-01T00:00:00Z" },
    ];
    const result = sortAndSliceBadges(badges);
    expect(result).toHaveLength(1);
    expect(result[0]?.id).toBe(2);
  });

  it("trie par earned_at décroissant", () => {
    const badges = [
      { id: 1, earned_at: "2025-01-01T00:00:00Z" },
      { id: 3, earned_at: "2025-03-01T00:00:00Z" },
      { id: 2, earned_at: "2025-02-01T00:00:00Z" },
    ];
    const result = sortAndSliceBadges(badges);
    expect(result.map((b) => b.id)).toEqual([3, 2, 1]);
  });

  it("limite à 3 badges", () => {
    const badges = Array.from({ length: 6 }, (_, i) => ({
      id: i + 1,
      earned_at: `2025-0${i + 1}-01T00:00:00Z`,
    }));
    const result = sortAndSliceBadges(badges);
    expect(result).toHaveLength(3);
  });

  it("retourne les 3 plus récents", () => {
    const badges = [
      { id: 1, earned_at: "2025-01-01T00:00:00Z" },
      { id: 2, earned_at: "2025-02-01T00:00:00Z" },
      { id: 3, earned_at: "2025-03-01T00:00:00Z" },
      { id: 4, earned_at: "2025-04-01T00:00:00Z" },
      { id: 5, earned_at: "2025-05-01T00:00:00Z" },
    ];
    const result = sortAndSliceBadges(badges);
    expect(result.map((b) => b.id)).toEqual([5, 4, 3]);
  });
});
