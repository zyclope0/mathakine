import { describe, expect, it } from "vitest";

import {
  VISUALIZATION_COLOR_MAP,
  findVisualizationColorInText,
  resolveVisualizationColor,
} from "@/components/challenges/visualizations/_colorMap";

describe("_colorMap (ACTIF-07)", () => {
  it("exposes brown and marron with the same hex", () => {
    expect(VISUALIZATION_COLOR_MAP.brown).toBe("#92400e");
    expect(VISUALIZATION_COLOR_MAP.marron).toBe(VISUALIZATION_COLOR_MAP.brown);
  });

  it("resolveVisualizationColor returns hex for known keys (FR/EN)", () => {
    expect(resolveVisualizationColor("bleu")).toBe("#3b82f6");
    expect(resolveVisualizationColor("Blue")).toBe("#3b82f6");
    expect(resolveVisualizationColor("brown")).toBe("#92400e");
  });

  it("resolveVisualizationColor returns null for unknown or empty", () => {
    expect(resolveVisualizationColor(undefined)).toBeNull();
    expect(resolveVisualizationColor(null)).toBeNull();
    expect(resolveVisualizationColor("")).toBeNull();
    expect(resolveVisualizationColor("?")).toBeNull();
    expect(resolveVisualizationColor("notacolor")).toBeNull();
  });

  it("findVisualizationColorInText picks first map key present in lowercased text", () => {
    expect(findVisualizationColorInText("triangle rouge")).toBe("#ef4444");
    expect(findVisualizationColorInText("cercle marron")).toBe("#92400e");
  });
});
