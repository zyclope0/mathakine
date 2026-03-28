import { describe, it, expect } from "vitest";
import { readBadgeThematicTitleRaw } from "@/lib/gamification/badgeThematicTitle";

describe("readBadgeThematicTitleRaw", () => {
  it("priorise thematic_title", () => {
    expect(
      readBadgeThematicTitleRaw({
        thematic_title: " A ",
        star_wars_title: "B",
      })
    ).toBe("A");
  });

  it("retombe sur star_wars_title", () => {
    expect(readBadgeThematicTitleRaw({ star_wars_title: " Legacy " })).toBe("Legacy");
  });

  it("retourne chaîne vide si absent", () => {
    expect(readBadgeThematicTitleRaw({})).toBe("");
  });
});
