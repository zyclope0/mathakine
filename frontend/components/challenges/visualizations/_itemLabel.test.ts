import { describe, it, expect } from "vitest";

import {
  itemDescriptiveText,
  itemDisplayLabel,
  itemLabel,
  itemLabelWithExtras,
  itemOrderKey,
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

describe("itemDescriptiveText — enrichissement visible", () => {
  it("paire left/right : joint avec ↔", () => {
    expect(itemDescriptiveText({ id: "P1", left: "11", right: "13" })).toBe("11 ↔ 13");
  });

  it("paire from/to : joint avec →", () => {
    expect(itemDescriptiveText({ name: "Arête", from: "A", to: "B" })).toBe("A → B");
  });

  it("champs libres : format k: v · k: v", () => {
    expect(itemDescriptiveText({ id: "X", poids: 5, couleur: "rouge" })).toBe(
      "poids: 5 · couleur: rouge"
    );
  });

  it("array plate : jointure virgule", () => {
    expect(
      itemDescriptiveText({
        id: "A",
        pattern: ["NW: rouge", "NE: vide", "SW: rouge", "SE: rouge"],
      })
    ).toBe("pattern: NW: rouge, NE: vide, SW: rouge, SE: rouge");
  });

  it("ignore les objets imbriqués (pas de JSON.stringify silencieux)", () => {
    const out = itemDescriptiveText({
      id: "X",
      nested: { deep: { value: "bury" } },
    });
    expect(out).not.toContain("[object Object]");
    expect(out).not.toContain("{");
  });

  it("string plate : retourne chaîne vide (rien à décrire)", () => {
    expect(itemDescriptiveText("just a string")).toBe("");
  });

  it("limite maxFields pour éviter les libellés trop longs", () => {
    const raw = { a: 1, b: 2, c: 3, d: 4, e: 5 };
    const out = itemDescriptiveText(raw, { maxFields: 2 });
    expect(out).toBe("a: 1 · b: 2");
  });
});

describe("itemDisplayLabel — label + descriptif", () => {
  it("puzzle piece (id + left/right) : id · 11 ↔ 13", () => {
    expect(itemDisplayLabel({ id: "P1", left: "11", right: "13" })).toBe("P1 · 11 ↔ 13");
  });

  it("puzzle piece avec pattern : id · pattern: …", () => {
    expect(
      itemDisplayLabel({
        id: "A",
        pattern: ["NW: rouge", "NE: vide"],
      })
    ).toBe("A · pattern: NW: rouge, NE: vide");
  });

  it("string plate : renvoyée telle quelle (pas de descriptif à ajouter)", () => {
    expect(itemDisplayLabel("cercle rouge")).toBe("cercle rouge");
  });

  it("label seul sans champs descriptifs : retourne juste le label", () => {
    expect(itemDisplayLabel({ id: "P1" })).toBe("P1");
  });

  it("fallback explicite quand rien de lisible", () => {
    expect(itemDisplayLabel({ foo: { bar: 1 } }, { fallback: "#1" })).toBe("#1");
  });

  it("jamais de repr brute dans la sortie", () => {
    const samples: unknown[] = [
      { id: "A", pattern: ["x"] },
      { id: "P1", left: "11", right: "13" },
      { id: "X", nested: { deep: "no leak" } },
      "{'id': 'Y'}",
    ];
    for (const s of samples) {
      const out = itemDisplayLabel(s, { fallback: "" });
      expect(out).not.toContain("{'id'");
      expect(out).not.toContain('{"id"');
      expect(out).not.toContain("[object Object]");
    }
  });
});

describe("itemOrderKey — clé d'ordre stable pour correct_answer", () => {
  it("priorité stricte au champ 'id' même si 'name' est présent (anti-#4071 miroir)", () => {
    // Régression : itemLabel classique renverrait "paire première" (name gagne
    // avant id dans DEFAULT_ITEM_LABEL_FIELDS). itemOrderKey doit renvoyer "P1"
    // pour que correct_answer = "P1, P2, …" reste matchable côté backend.
    expect(itemOrderKey({ id: "P1", name: "paire première", label: "aussi éditorial" })).toBe("P1");
  });

  it("accepte piece_id comme alias de id", () => {
    expect(itemOrderKey({ piece_id: "P7", name: "n'importe quoi" })).toBe("P7");
  });

  it("fallback sur itemLabel si id absent", () => {
    expect(itemOrderKey({ label: "Alpha" })).toBe("Alpha");
    expect(itemOrderKey("Beta")).toBe("Beta");
  });

  it("fallback explicite si rien de lisible", () => {
    expect(itemOrderKey({ foo: "bar" }, { fallback: "#1" })).toBe("#1");
  });

  it("preferField custom", () => {
    // Contrat futur : un renderer peut imposer un autre champ-clé si besoin.
    expect(itemOrderKey({ token: "T1", id: "fallback" }, { preferField: "token" })).toBe("T1");
  });

  it("numérique accepté comme id", () => {
    expect(itemOrderKey({ id: 42 })).toBe("42");
  });

  it("jamais de repr brute", () => {
    const samples: unknown[] = [
      { id: "P1", nested: { deep: "x" } },
      { label: "{pas un dict}" },
      "{'id': 'Y'}",
    ];
    for (const s of samples) {
      const out = itemOrderKey(s);
      expect(out).not.toContain("{'id'");
      expect(out).not.toContain('{"id"');
      expect(out).not.toContain("[object Object]");
    }
  });
});
