/**
 * Tests unitaires — helpers purs challengeSolver.ts
 *
 * Couvre : normalizeChallengeChoices, getChallengeHintsArray,
 *          getChallengeVisualAnswerModel, isChallengeAnswerEmpty,
 *          getChallengeTextInputKind
 *
 * FFI-L10 — lot 1 : tests de caractérisation helpers purs
 */
import { describe, it, expect } from "vitest";
import type { Challenge } from "@/types/api";
import {
  normalizeChallengeChoices,
  getChallengeHintsArray,
  getChallengeVisualAnswerModel,
  isChallengeAnswerEmpty,
  getChallengeTextInputKind,
} from "./challengeSolver";

// ─── Fixture ──────────────────────────────────────────────────────────────────

function challenge(partial: Partial<Challenge>): Challenge {
  return {
    id: 1,
    title: "Test challenge",
    description: "Description du défi",
    challenge_type: "logic",
    age_group: "9-11",
    ...partial,
  } as Challenge;
}

// ─── normalizeChallengeChoices ────────────────────────────────────────────────

describe("normalizeChallengeChoices", () => {
  it("retourne le tableau natif tel quel", () => {
    const c = challenge({ choices: ["A", "B", "C"] });
    expect(normalizeChallengeChoices(c)).toEqual(["A", "B", "C"]);
  });

  it("parse une string JSON valide en tableau", () => {
    const c = challenge({ choices: '["x", "y"]' as unknown as string[] });
    expect(normalizeChallengeChoices(c)).toEqual(["x", "y"]);
  });

  it("retourne [] si la string JSON est invalide", () => {
    const c = challenge({ choices: "{not:valid}" as unknown as string[] });
    expect(normalizeChallengeChoices(c)).toEqual([]);
  });

  it("retourne [] si choices est null", () => {
    const c = challenge({ choices: null });
    expect(normalizeChallengeChoices(c)).toEqual([]);
  });

  it("retourne [] si choices n'est pas défini", () => {
    // Pas de choices dans le partial — exactOptionalPropertyTypes oblige à omettre le champ
    const c = challenge({});
    expect(normalizeChallengeChoices(c)).toEqual([]);
  });

  it("retourne [] si choices est un objet non-tableau", () => {
    const c = challenge({ choices: { key: "val" } as unknown as string[] });
    expect(normalizeChallengeChoices(c)).toEqual([]);
  });
});

// ─── getChallengeHintsArray ───────────────────────────────────────────────────

describe("getChallengeHintsArray", () => {
  it("retourne le tableau natif tel quel", () => {
    expect(getChallengeHintsArray(["indice 1", "indice 2"])).toEqual(["indice 1", "indice 2"]);
  });

  it("parse une string JSON valide en tableau", () => {
    expect(getChallengeHintsArray('["hint A", "hint B"]')).toEqual(["hint A", "hint B"]);
  });

  it("retourne [] si la string JSON est invalide", () => {
    expect(getChallengeHintsArray("pas du json")).toEqual([]);
  });

  it("retourne [] si la valeur est null", () => {
    expect(getChallengeHintsArray(null)).toEqual([]);
  });

  it("retourne [] si la valeur est undefined", () => {
    expect(getChallengeHintsArray(undefined)).toEqual([]);
  });

  it("retourne [] si la valeur est un nombre", () => {
    expect(getChallengeHintsArray(42)).toEqual([]);
  });

  it("retourne [] si le JSON est un objet non-tableau", () => {
    expect(getChallengeHintsArray('{"not": "array"}')).toEqual([]);
  });
});

// ─── getChallengeVisualAnswerModel ────────────────────────────────────────────

describe("getChallengeVisualAnswerModel", () => {
  describe("mode single_choice", () => {
    it("showMcq=true quand response_mode=single_choice et choices non vide", () => {
      const c = challenge({
        response_mode: "single_choice",
        choices: ["A", "B", "C"],
        challenge_type: "logic",
      });
      const model = getChallengeVisualAnswerModel(c, {});
      expect(model.showMcq).toBe(true);
      expect(model.responseMode).toBe("single_choice");
      expect(model.hasVisualButtons).toBe(false);
    });

    it("showMcq=false si choices est vide malgré response_mode=single_choice", () => {
      const c = challenge({ response_mode: "single_choice", choices: [] });
      const model = getChallengeVisualAnswerModel(c, {});
      expect(model.showMcq).toBe(false);
    });
  });

  describe("mode interactive_visual simple (une position)", () => {
    const visualData = {
      shapes: ["cercle rouge", "carré bleu", "triangle vert"],
    };

    it("hasVisualButtons=true avec deux formes et visual_data", () => {
      const c = challenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        visual_data: visualData,
        correct_answer: "cercle rouge", // pas de "Position N:" → positions = []
        choices: null,
      });
      const model = getChallengeVisualAnswerModel(c, {});
      expect(model.hasVisualButtons).toBe(true);
      expect(model.isVisual).toBe(true);
      expect(model.visualChoices.length).toBeGreaterThanOrEqual(2);
      // single position → isVisualMultiComplete=true (positions.length <= 1)
      expect(model.visualPositions.length).toBe(0);
      expect(model.isVisualMultiComplete).toBe(true);
    });
  });

  describe("mode interactive_visual multi-position", () => {
    const visualData = {
      shapes: ["cercle rouge", "carré bleu", "triangle vert"],
    };

    it("derivedUserAnswerFromSelections contient les sélections", () => {
      const c = challenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        visual_data: visualData,
        correct_answer: "Position 1: cercle rouge, Position 2: carré bleu",
        choices: null,
      });
      const selections: Record<number, string> = { 1: "cercle rouge", 2: "carré bleu" };
      const model = getChallengeVisualAnswerModel(c, selections);

      expect(model.visualPositions).toEqual([1, 2]);
      expect(model.isVisualMultiComplete).toBe(true);
      expect(model.derivedUserAnswerFromSelections).toContain("Position 1: cercle rouge");
      expect(model.derivedUserAnswerFromSelections).toContain("Position 2: carré bleu");
    });

    it("isVisualMultiComplete=false si une position manque", () => {
      const c = challenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        visual_data: visualData,
        correct_answer: "Position 1: x, Position 2: y",
        choices: null,
      });
      // Position 2 non renseignée
      const model = getChallengeVisualAnswerModel(c, { 1: "cercle rouge" });
      expect(model.isVisualMultiComplete).toBe(false);
    });

    it("derivedUserAnswerFromSelections vide si aucune sélection", () => {
      const c = challenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        visual_data: visualData,
        correct_answer: "Position 1: x, Position 2: y",
        choices: null,
      });
      const model = getChallengeVisualAnswerModel(c, {});
      expect(model.derivedUserAnswerFromSelections).toBe("");
    });
  });

  describe("fallback open_text", () => {
    it("réponse en texte libre par défaut (response_mode absent)", () => {
      // response_mode omis (exactOptionalPropertyTypes)
      const c = challenge({ challenge_type: "logic" });
      const model = getChallengeVisualAnswerModel(c, {});
      expect(model.responseMode).toBe("open_text");
      expect(model.showMcq).toBe(false);
      expect(model.hasVisualButtons).toBe(false);
    });
  });
});

// ─── isChallengeAnswerEmpty ───────────────────────────────────────────────────

describe("isChallengeAnswerEmpty", () => {
  it("texte vide → true", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: false,
        visualPositions: [],
        isVisualMultiComplete: true,
        userAnswer: "",
      })
    ).toBe(true);
  });

  it("texte rempli → false", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: false,
        visualPositions: [],
        isVisualMultiComplete: true,
        userAnswer: "42",
      })
    ).toBe(false);
  });

  it("texte avec espaces seulement → true", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: false,
        visualPositions: [],
        isVisualMultiComplete: true,
        userAnswer: "   ",
      })
    ).toBe(true);
  });

  it("visual simple sans valeur → true", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: true,
        visualPositions: [], // longueur ≤ 1 → branche simple
        isVisualMultiComplete: true,
        userAnswer: "",
      })
    ).toBe(true);
  });

  it("visual simple avec valeur → false", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: true,
        visualPositions: [1],
        isVisualMultiComplete: true,
        userAnswer: "cercle rouge",
      })
    ).toBe(false);
  });

  it("visual multi-position incomplet → true", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: true,
        visualPositions: [1, 2],
        isVisualMultiComplete: false,
        userAnswer: "Position 1: cercle rouge",
      })
    ).toBe(true);
  });

  it("visual multi-position complet → false", () => {
    expect(
      isChallengeAnswerEmpty({
        hasVisualButtons: true,
        visualPositions: [1, 2],
        isVisualMultiComplete: true,
        userAnswer: "Position 1: cercle rouge, Position 2: carré bleu",
      })
    ).toBe(false);
  });
});

// ─── getChallengeTextInputKind ────────────────────────────────────────────────

describe("getChallengeTextInputKind", () => {
  it("retourne 'chess' pour challenge_type='chess'", () => {
    expect(getChallengeTextInputKind("chess")).toBe("chess");
    expect(getChallengeTextInputKind("Chess")).toBe("chess");
    expect(getChallengeTextInputKind("CHESS")).toBe("chess");
  });

  it("retourne 'visual' pour challenge_type='visual'", () => {
    expect(getChallengeTextInputKind("visual")).toBe("visual");
    expect(getChallengeTextInputKind("Visual")).toBe("visual");
  });

  it("retourne 'default' pour les autres types", () => {
    expect(getChallengeTextInputKind("logic")).toBe("default");
    expect(getChallengeTextInputKind("sequence")).toBe("default");
    expect(getChallengeTextInputKind("puzzle")).toBe("default");
  });

  it("retourne 'default' pour null", () => {
    expect(getChallengeTextInputKind(null)).toBe("default");
  });

  it("retourne 'default' pour undefined", () => {
    expect(getChallengeTextInputKind(undefined)).toBe("default");
  });
});
