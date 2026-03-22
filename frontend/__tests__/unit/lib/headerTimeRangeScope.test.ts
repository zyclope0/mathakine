import { describe, expect, it } from "vitest";
import { shouldShowHeaderTimeRange } from "@/lib/dashboard/headerTimeRangeScope";

describe("shouldShowHeaderTimeRange", () => {
  it("shows selector on overview and profile only", () => {
    expect(shouldShowHeaderTimeRange("overview")).toBe(true);
    expect(shouldShowHeaderTimeRange("profile")).toBe(false);
    expect(shouldShowHeaderTimeRange("progress")).toBe(false);
    expect(shouldShowHeaderTimeRange("recommendations")).toBe(false);
  });

  it("hides on unknown tab values", () => {
    expect(shouldShowHeaderTimeRange("")).toBe(false);
    expect(shouldShowHeaderTimeRange("settings")).toBe(false);
  });
});
