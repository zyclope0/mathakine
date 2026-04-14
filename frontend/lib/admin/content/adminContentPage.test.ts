import { describe, it, expect } from "vitest";
import {
  parseAdminContentEditIdParam,
  parseAdminContentTabParam,
  buildExerciseTypeFilterOptions,
} from "./adminContentPage";

describe("adminContentPage", () => {
  describe("parseAdminContentTabParam", () => {
    it("default exercises", () => {
      expect(parseAdminContentTabParam(null)).toBe("exercises");
      expect(parseAdminContentTabParam("")).toBe("exercises");
      expect(parseAdminContentTabParam("nope")).toBe("exercises");
    });
    it("challenges and badges", () => {
      expect(parseAdminContentTabParam("challenges")).toBe("challenges");
      expect(parseAdminContentTabParam("badges")).toBe("badges");
    });
  });

  describe("parseAdminContentEditIdParam", () => {
    it("null and invalid", () => {
      expect(parseAdminContentEditIdParam(null)).toBeNull();
      expect(parseAdminContentEditIdParam("")).toBeNull();
      expect(parseAdminContentEditIdParam("abc")).toBeNull();
      expect(parseAdminContentEditIdParam("0")).toBeNull();
      expect(parseAdminContentEditIdParam("-3")).toBeNull();
    });
    it("positive integer", () => {
      expect(parseAdminContentEditIdParam("42")).toBe(42);
    });
  });

  describe("buildExerciseTypeFilterOptions", () => {
    it("includes all sentinel and at least one mapped type label", () => {
      const opts = buildExerciseTypeFilterOptions();
      expect(opts[0]).toEqual({ value: "all", label: "Tous les types" });
      const addition = opts.find((o) => o.value === "ADDITION");
      expect(addition?.label).toBe("Addition");
    });
  });
});
