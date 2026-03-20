import { describe, expect, it } from "vitest";
import {
  buildDashboardExportSnapshot,
  deriveIncorrectAnswersForExport,
  selectExperiencePointsForExport,
} from "@/lib/dashboard/buildDashboardExportSnapshot";
import type { UserStats } from "@/lib/validation/dashboard";
import type { ProgressStats } from "@/hooks/useProgressStats";

function baseStats(over: Partial<UserStats> = {}): UserStats {
  return {
    total_exercises: 10,
    correct_answers: 8,
    success_rate: 80,
    ...over,
  };
}

describe("buildDashboardExportSnapshot", () => {
  it("utilise experience_points pour l’XP exportée (pas xp)", () => {
    const stats = baseStats({ experience_points: 1200, xp: 999 });
    const snap = buildDashboardExportSnapshot({
      username: "alice",
      timeRange: "30",
      timeRangeLabel: "30 derniers jours",
      stats,
    });
    expect(snap.summary.experience_points).toBe(1200);
  });

  it("n’utilise pas stats.xp si experience_points est absent", () => {
    const stats = baseStats({ xp: 500 });
    const snap = buildDashboardExportSnapshot({
      username: "bob",
      timeRange: "30",
      timeRangeLabel: "30 derniers jours",
      stats,
    });
    expect(snap.summary.experience_points).toBeNull();
  });

  it("expose success_rate comme KPI principal depuis les stats", () => {
    const stats = baseStats({ success_rate: 73.4 });
    const snap = buildDashboardExportSnapshot({
      username: "carol",
      timeRange: "7",
      timeRangeLabel: "7 derniers jours",
      stats,
    });
    expect(snap.summary.success_rate).toBe(73.4);
  });

  it("ne met pas incorrect_answers à 0 si absent et non dérivable", () => {
    const stats = baseStats({ incorrect_answers: undefined });
    const snap = buildDashboardExportSnapshot({
      username: "dave",
      timeRange: "all",
      timeRangeLabel: "Tout",
      stats,
      progressStats: null,
    });
    expect(snap.summary.incorrect_answers).toBeNull();
  });

  it("dérive incorrect_answers depuis total_attempts - correct_attempts si possible", () => {
    const stats = baseStats({ incorrect_answers: undefined });
    const progress: ProgressStats = {
      total_attempts: 100,
      correct_attempts: 88,
      accuracy: 0.88,
      average_time: 12,
      exercises_completed: 50,
      highest_streak: 3,
      current_streak: 1,
      by_category: {},
    };
    const snap = buildDashboardExportSnapshot({
      username: "erin",
      timeRange: "30",
      timeRangeLabel: "30 derniers jours",
      stats,
      progressStats: progress,
    });
    expect(snap.summary.incorrect_answers).toBe(12);
  });
});

describe("deriveIncorrectAnswersForExport", () => {
  it("priorise la valeur API incorrect_answers", () => {
    const v = deriveIncorrectAnswersForExport(baseStats({ incorrect_answers: 5 }), {
      total_attempts: 100,
      correct_attempts: 99,
      accuracy: 0.99,
      average_time: 1,
      exercises_completed: 1,
      highest_streak: 1,
      current_streak: 1,
      by_category: {},
    });
    expect(v).toBe(5);
  });
});

describe("selectExperiencePointsForExport", () => {
  it("retourne experience_points uniquement", () => {
    expect(selectExperiencePointsForExport(baseStats({ experience_points: 42 }))).toBe(42);
    expect(selectExperiencePointsForExport(baseStats({ xp: 99 }))).toBeNull();
  });
});
