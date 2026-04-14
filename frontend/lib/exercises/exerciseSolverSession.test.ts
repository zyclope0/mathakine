import { describe, expect, it } from "vitest";
import {
  INTERLEAVED_STORAGE_KEY,
  parseInterleavedSessionFromStorage,
  readSessionMode,
} from "./exerciseSolverSession";
import { STORAGE_KEYS } from "../storage";

describe("exerciseSolverSession", () => {
  it("readSessionMode maps query param", () => {
    expect(readSessionMode(new URLSearchParams("session=interleaved"))).toBe("interleaved");
    expect(readSessionMode(new URLSearchParams("session=spaced-review"))).toBe("spaced-review");
    expect(readSessionMode(new URLSearchParams(""))).toBeNull();
    expect(readSessionMode(null)).toBeNull();
  });

  it("INTERLEAVED_STORAGE_KEY stays aligned with the shared storage key source of truth", () => {
    expect(INTERLEAVED_STORAGE_KEY).toBe(STORAGE_KEYS.edtechInterleavedSession);
  });

  it("parseInterleavedSessionFromStorage returns null on invalid JSON", () => {
    expect(parseInterleavedSessionFromStorage("")).toBeNull();
    expect(parseInterleavedSessionFromStorage("{")).toBeNull();
  });

  it("parseInterleavedSessionFromStorage returns null without plan array", () => {
    expect(parseInterleavedSessionFromStorage("{}")).toBeNull();
    expect(parseInterleavedSessionFromStorage(JSON.stringify({ plan: "x" }))).toBeNull();
  });

  it("parseInterleavedSessionFromStorage normalizes counts and analytics", () => {
    const raw = JSON.stringify({
      plan: ["addition", "fractions"],
      completedCount: 1,
      length: 5,
      analytics: { firstAttemptTracked: true },
    });
    expect(parseInterleavedSessionFromStorage(raw)).toEqual({
      plan: ["addition", "fractions"],
      completedCount: 1,
      length: 5,
      analytics: { firstAttemptTracked: true },
    });
  });

  it("parseInterleavedSessionFromStorage defaults completedCount and length", () => {
    const raw = JSON.stringify({ plan: ["a"] });
    expect(parseInterleavedSessionFromStorage(raw)).toEqual({
      plan: ["a"],
      completedCount: 0,
      length: 1,
    });
  });
});
