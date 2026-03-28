import { describe, expect, it } from "vitest";
import {
  buildDashboardExportSnapshot,
  deriveIncorrectAnswersForExport,
} from "@/lib/dashboard/buildDashboardExportSnapshot";
import { type UserStats, parseSpacedRepetitionUserSummary } from "@/lib/validation/dashboard";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { GamificationLevelIndicator } from "@/types/api";

function baseStats(over: Partial<UserStats> = {}): UserStats {
  return {
    total_exercises: 10,
    correct_answers: 8,
    success_rate: 80,
    spaced_repetition: parseSpacedRepetitionUserSummary(null),
    ...over,
  };
}

describe("buildDashboardExportSnapshot", () => {
  it("expose account_total_points depuis accountTotalPoints (GET /me), pas depuis les stats période", () => {
    const snap = buildDashboardExportSnapshot({
      username: "alice",
      timeRange: "30",
      timeRangeLabel: "30 derniers jours",
      stats: baseStats(),
      accountTotalPoints: 1250,
    });
    expect(snap.summary.account_total_points).toBe(1250);
    expect(snap.gamification_level).toBeNull();
  });

  it("met account_total_points à null si accountTotalPoints absent", () => {
    const snap = buildDashboardExportSnapshot({
      username: "bob",
      timeRange: "30",
      timeRangeLabel: "30 derniers jours",
      stats: baseStats(),
    });
    expect(snap.summary.account_total_points).toBeNull();
  });

  it("expose account_xp_in_level depuis gamification_level.current_xp", () => {
    const gl: GamificationLevelIndicator = {
      current: 2,
      current_xp: 37,
      next_level_xp: 100,
      jedi_rank: "explorer",
    };
    const snap = buildDashboardExportSnapshot({
      username: "carol",
      timeRange: "7",
      timeRangeLabel: "7 derniers jours",
      stats: baseStats(),
      gamificationLevel: gl,
      accountTotalPoints: 100,
    });
    expect(snap.summary.account_xp_in_level).toBe(37);
  });

  it("met account_xp_in_level à null sans gamification_level", () => {
    const snap = buildDashboardExportSnapshot({
      username: "dave",
      timeRange: "all",
      timeRangeLabel: "Tout",
      stats: baseStats(),
    });
    expect(snap.summary.account_xp_in_level).toBeNull();
  });

  it("expose success_rate comme KPI principal depuis les stats", () => {
    const stats = baseStats({ success_rate: 73.4 });
    const snap = buildDashboardExportSnapshot({
      username: "erin",
      timeRange: "7",
      timeRangeLabel: "7 derniers jours",
      stats,
    });
    expect(snap.summary.success_rate).toBe(73.4);
  });

  it("ne met pas incorrect_answers à 0 si absent et non dérivable", () => {
    const stats = baseStats();
    const snap = buildDashboardExportSnapshot({
      username: "frank",
      timeRange: "all",
      timeRangeLabel: "Tout",
      stats,
      progressStats: null,
    });
    expect(snap.summary.incorrect_answers).toBeNull();
  });

  it("propage gamification_level (persistant) dans l’export", () => {
    const gl: GamificationLevelIndicator = {
      current: 3,
      current_xp: 20,
      next_level_xp: 100,
      jedi_rank: "scout",
    };
    const snap = buildDashboardExportSnapshot({
      username: "gl_user",
      timeRange: "30",
      timeRangeLabel: "30 jours",
      stats: baseStats(),
      gamificationLevel: gl,
    });
    expect(snap.gamification_level).toEqual(gl);
  });

  it("dérive incorrect_answers depuis total_attempts - correct_attempts si possible", () => {
    const stats = baseStats();
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
      username: "grace",
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
