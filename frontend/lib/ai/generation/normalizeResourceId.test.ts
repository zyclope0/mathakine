import { describe, it, expect } from "vitest";
import { normalizeCreatedResourceId } from "./normalizeResourceId";

describe("normalizeCreatedResourceId", () => {
  it("accepte un entier positif", () => {
    expect(normalizeCreatedResourceId(7)).toBe(7);
  });

  it("rejette 0 et les négatifs", () => {
    expect(normalizeCreatedResourceId(0)).toBeUndefined();
    expect(normalizeCreatedResourceId(-1)).toBeUndefined();
  });

  it("parse une chaîne numérique", () => {
    expect(normalizeCreatedResourceId("  42  ")).toBe(42);
  });

  it("rejette les valeurs non numériques", () => {
    expect(normalizeCreatedResourceId("abc")).toBeUndefined();
    expect(normalizeCreatedResourceId(null)).toBeUndefined();
  });
});
