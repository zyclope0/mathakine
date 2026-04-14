import { describe, it, expect } from "vitest";
import { hasAiTag, formatSuccessRate } from "./format";

describe("hasAiTag", () => {
  describe("valeurs nulles / vides", () => {
    it("retourne false pour null", () => {
      expect(hasAiTag(null)).toBe(false);
    });

    it("retourne false pour undefined", () => {
      expect(hasAiTag(undefined)).toBe(false);
    });

    it("retourne false pour chaîne vide", () => {
      expect(hasAiTag("")).toBe(false);
    });

    it("retourne false pour tableau vide", () => {
      expect(hasAiTag([])).toBe(false);
    });
  });

  describe("format tableau", () => {
    it("retourne true si le tableau contient 'ai'", () => {
      expect(hasAiTag(["ai"])).toBe(true);
      expect(hasAiTag(["math", "ai", "hard"])).toBe(true);
    });

    it("retourne false si le tableau ne contient pas 'ai'", () => {
      expect(hasAiTag(["math", "hard"])).toBe(false);
    });

    it("est sensible à la casse — 'AI' ne compte pas", () => {
      expect(hasAiTag(["AI"])).toBe(false);
      expect(hasAiTag(["Ai"])).toBe(false);
    });
  });

  describe("format chaîne", () => {
    it("retourne true pour la chaîne exacte 'ai'", () => {
      expect(hasAiTag("ai")).toBe(true);
    });

    it("retourne true si 'ai' est dans une chaîne CSV", () => {
      expect(hasAiTag("math,ai,hard")).toBe(true);
      expect(hasAiTag("ai,math")).toBe(true);
      expect(hasAiTag("math,ai")).toBe(true);
    });

    it("gère les espaces autour des virgules", () => {
      expect(hasAiTag("math, ai, hard")).toBe(true);
      // Les segments sont trimés : " ai " est normalisé en "ai" → true
      expect(hasAiTag(" ai ")).toBe(true);
    });

    it("retourne false si 'ai' absent de la chaîne CSV", () => {
      expect(hasAiTag("math,hard")).toBe(false);
      expect(hasAiTag("aimer,hard")).toBe(false);
    });

    it("est sensible à la casse — 'AI' ne compte pas", () => {
      expect(hasAiTag("AI")).toBe(false);
      expect(hasAiTag("math,AI")).toBe(false);
    });
  });
});

describe("formatSuccessRate", () => {
  describe("valeurs invalides", () => {
    it("retourne null pour null", () => {
      expect(formatSuccessRate(null)).toBe(null);
    });

    it("retourne null pour undefined", () => {
      expect(formatSuccessRate(undefined)).toBe(null);
    });

    it("retourne null pour valeur négative", () => {
      expect(formatSuccessRate(-1)).toBe(null);
    });
  });

  describe("format ratio (0-1)", () => {
    it("convertit 0 en '0%'", () => {
      expect(formatSuccessRate(0)).toBe("0%");
    });

    it("convertit 0.75 en '75%'", () => {
      expect(formatSuccessRate(0.75)).toBe("75%");
    });

    it("arrondit correctement (0.756 → '76%')", () => {
      expect(formatSuccessRate(0.756)).toBe("76%");
    });

    it("convertit 1 en '100%'", () => {
      expect(formatSuccessRate(1)).toBe("100%");
    });
  });

  describe("format pourcentage (> 1)", () => {
    it("retourne '75%' pour 75", () => {
      expect(formatSuccessRate(75)).toBe("75%");
    });

    it("retourne '100%' pour 100", () => {
      expect(formatSuccessRate(100)).toBe("100%");
    });

    it("arrondit correctement (75.6 → '76%')", () => {
      expect(formatSuccessRate(75.6)).toBe("76%");
    });
  });
});
