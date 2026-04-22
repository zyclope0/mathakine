import { describe, it, expect } from "vitest";

import {
  itemLabel,
  itemLabelWithExtras,
  parseDictLikeLabel,
} from "@/components/challenges/visualizations/_itemLabel";

describe("itemLabel — contrat d'affichage unifié", () => {
  it("chaîne plate : trim et renvoi direct", () => {
    expect(itemLabel("  cercle rouge  ")).toBe("cercle rouge");
  });

  it("chaîne dict Python-like : extrait le champ label prioritaire", () => {
    expect(itemLabel("{'name': 'cercle rouge', 'size': 'petit'}")).toBe("cercle rouge");
  });

  it("chaîne dict JSON-like : extrait aussi", () => {
    expect(itemLabel('{"id":"P1","left":"11","right":"13"}')).toBe("P1");
  });

  it("dict avec label : priorité au champ officiel", () => {
    expect(itemLabel({ label: "Alpha", id: "A" })).toBe("Alpha");
  });

  it("dict avec id seul : accepté (contrat LLM puzzle)", () => {
    expect(itemLabel({ id: "P1", left: "11", right: "13" })).toBe("P1");
  });

  it("dict avec value numérique : stringification canonique", () => {
    expect(itemLabel({ value: 42 })).toBe("42");
  });

  it("numérique direct : toString", () => {
    expect(itemLabel(7)).toBe("7");
  });

  it("null / undefined : fallback vide", () => {
    expect(itemLabel(null)).toBe("");
    expect(itemLabel(undefined)).toBe("");
  });

  it("fallback personnalisé", () => {
    expect(itemLabel(null, { fallback: "#1" })).toBe("#1");
    expect(itemLabel({ foo: "bar" }, { fallback: "?" })).toBe("?");
  });

  it("jamais de [object Object] ni de repr Python dans la sortie", () => {
    const samples: unknown[] = [
      { id: "A", pattern: ["x"] },
      { foo: "bar" },
      "{'id': 'X', 'bidule': 'y'}",
      '{"id":"Y","left":"1"}',
      [1, 2, 3],
      { nested: { label: "deep" } },
    ];
    for (const s of samples) {
      const out = itemLabel(s, { fallback: "" });
      expect(out).not.toContain("{'id'");
      expect(out).not.toContain('{"id"');
      expect(out).not.toContain("[object Object]");
    }
  });

  it("parseDictLikeLabel : fail-open sur vraies chaînes", () => {
    expect(parseDictLikeLabel("cercle rouge")).toBeNull();
    expect(parseDictLikeLabel("")).toBeNull();
    expect(parseDictLikeLabel("{pas un dict}")).toBeNull();
  });

  it("itemLabelWithExtras : récupère size/orientation/color", () => {
    const { label, extras } = itemLabelWithExtras({
      name: "triangle jaune",
      size: "petit",
      orientation: "sommet vers la gauche",
    });
    expect(label).toBe("triangle jaune");
    expect(extras.size).toBe("petit");
    expect(extras.orientation).toBe("sommet vers la gauche");
  });

  it("fields override : priorise un champ non standard", () => {
    const raw = { token: "T1", id: "fallback" };
    expect(itemLabel(raw, { fields: ["token", "id"] })).toBe("T1");
    // sans override : ``token`` n'est pas dans la liste officielle → id gagne.
    expect(itemLabel(raw)).toBe("fallback");
  });
});
