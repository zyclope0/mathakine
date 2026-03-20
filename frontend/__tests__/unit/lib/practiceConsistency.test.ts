import { describe, expect, it } from "vitest";
import type { TimelinePoint } from "@/hooks/useProgressTimeline";
import {
  buildDailyPresenceFlags,
  computePracticeConsistency,
  listUtcDateKeysInclusive,
  normalizeTimelineDateKey,
} from "@/lib/dashboard/practiceConsistency";

describe("normalizeTimelineDateKey", () => {
  it("returns YYYY-MM-DD prefix", () => {
    expect(normalizeTimelineDateKey("2025-03-06T12:00:00.000Z")).toBe("2025-03-06");
    expect(normalizeTimelineDateKey("2025-03-06")).toBe("2025-03-06");
  });
});

describe("listUtcDateKeysInclusive", () => {
  it("returns one day when from equals to", () => {
    expect(
      listUtcDateKeysInclusive("2025-03-01T00:00:00.000Z", "2025-03-01T00:00:00.000Z")
    ).toEqual(["2025-03-01"]);
  });

  it("lists consecutive UTC days inclusive", () => {
    const keys = listUtcDateKeysInclusive("2025-03-01T00:00:00.000Z", "2025-03-03T00:00:00.000Z");
    expect(keys).toEqual(["2025-03-01", "2025-03-02", "2025-03-03"]);
  });
});

describe("buildDailyPresenceFlags", () => {
  it("marks active days from attempts", () => {
    const flags = buildDailyPresenceFlags("2025-03-01T00:00:00.000Z", "2025-03-03T00:00:00.000Z", [
      { date: "2025-03-01", attempts: 2 },
      { date: "2025-03-03", attempts: 1 },
    ]);
    expect(flags).toEqual([true, false, true]);
  });
});

describe("computePracticeConsistency", () => {
  it("computes metrics from timeline-shaped data", () => {
    const points: TimelinePoint[] = [
      {
        date: "2025-03-01",
        attempts: 4,
        correct: 3,
        success_rate_pct: 75,
        avg_time_spent_s: null,
        by_type: {},
      },
      {
        date: "2025-03-02",
        attempts: 0,
        correct: 0,
        success_rate_pct: 0,
        avg_time_spent_s: null,
        by_type: {},
      },
      {
        date: "2025-03-03",
        attempts: 2,
        correct: 2,
        success_rate_pct: 100,
        avg_time_spent_s: null,
        by_type: {},
      },
    ];
    const m = computePracticeConsistency(
      "2025-03-01T00:00:00.000Z",
      "2025-03-03T00:00:00.000Z",
      points,
      6
    );
    expect(m.totalDaysInPeriod).toBe(3);
    expect(m.activeDays).toBe(2);
    expect(m.regularityPercent).toBe(67);
    expect(m.avgAttemptsPerActiveDay).toBe(3);
    expect(m.mostActiveDay).toEqual({ date: "2025-03-01", attempts: 4 });
  });
});
