import { describe, expect, it } from "vitest";
import type { Badge, UserBadge } from "@/types/api";
import {
  buildEarnedUserBadgeMap,
  filterBadgesWithNameOrCode,
  getDifficultyPresentationClasses,
  hasPresentationMedal,
  isRareRarityInfo,
  resolveCompactHighProgressMotivation,
  resolveIconGlowClass,
  resolveMedalSvgPath,
  shouldShowLockedMidMotivationLine,
  shouldShowLockedZeroMotivationLine,
  sortBadgesForGrid,
  successRateRemainingCorrectNeeded,
} from "./badgePresentation";

const baseBadge = (overrides: Partial<Badge> = {}): Badge =>
  ({
    id: 1,
    name: "B",
    code: "b1",
    exercise_type: "ADDITION",
    difficulty: "bronze",
    category: "progression",
    points_reward: 10,
    ...overrides,
  }) as Badge;

describe("badgePresentation", () => {
  it("getDifficultyPresentationClasses falls back for unknown difficulty", () => {
    const d = getDifficultyPresentationClasses("weird");
    expect(d.bg).toContain("amber");
  });

  it("resolveIconGlowClass and resolveMedalSvgPath", () => {
    expect(resolveIconGlowClass("gold")).toContain("yellow");
    expect(resolveMedalSvgPath("gold")).toContain("medal.svg");
    expect(resolveMedalSvgPath(null)).toBe("/badges/svg/medal-bronze.svg");
  });

  it("hasPresentationMedal is false for unknown difficulty", () => {
    expect(hasPresentationMedal("bronze")).toBe(true);
    expect(hasPresentationMedal("unknown")).toBe(false);
  });

  it("isRareRarityInfo", () => {
    expect(isRareRarityInfo({ unlock_count: 1, unlock_percent: 1, rarity: "rare" })).toBe(true);
    expect(isRareRarityInfo({ unlock_count: 1, unlock_percent: 1, rarity: "common" })).toBe(false);
  });

  it("filterBadgesWithNameOrCode", () => {
    const empty = { ...baseBadge({ id: 2 }), name: "", code: "" } as Badge;
    expect(filterBadgesWithNameOrCode([baseBadge(), empty])).toHaveLength(1);
  });

  it("buildEarnedUserBadgeMap", () => {
    const ub = { id: 1 } as UserBadge;
    expect(buildEarnedUserBadgeMap([ub]).get(1)).toBe(ub);
  });

  it("sortBadgesForGrid orders earned first for category", () => {
    const earned = baseBadge({ id: 1 });
    const locked = baseBadge({ id: 2, name: "L" });
    const map = buildEarnedUserBadgeMap([{ id: 1 } as UserBadge]);
    const sorted = sortBadgesForGrid([locked, earned], map, {}, "category");
    expect(sorted[0]?.id).toBe(1);
  });

  it("successRateRemainingCorrectNeeded matches ceil formula", () => {
    const need = successRateRemainingCorrectNeeded({
      type: "success_rate",
      total: 10,
      correct: 3,
      rate_pct: 30,
      min_attempts: 5,
      required_rate_pct: 80,
    });
    expect(need).toBe(Math.ceil(8) - 3);
  });

  it("resolveCompactHighProgressMotivation branches", () => {
    const sr: Parameters<typeof resolveCompactHighProgressMotivation>[3] = {
      type: "success_rate",
      total: 10,
      correct: 9,
      rate_pct: 90,
      min_attempts: 1,
      required_rate_pct: 80,
    };
    expect(resolveCompactHighProgressMotivation(0, 5, 0.6, sr)?.kind).toBe("tuApproches");
    expect(
      resolveCompactHighProgressMotivation(0, 5, 0.6, { ...sr, correct: 3, rate_pct: 30 })?.kind
    ).toBe("plusQueCorrect");
    expect(resolveCompactHighProgressMotivation(4, 5, 0.9, undefined)?.kind).toBe("plusQue");
    expect(resolveCompactHighProgressMotivation(5, 5, 0.9, undefined)?.kind).toBe("tuApproches");
    expect(resolveCompactHighProgressMotivation(0, 5, 0.3, sr)).toBeNull();
  });

  it("shouldShowLockedMidMotivationLine", () => {
    expect(shouldShowLockedMidMotivationLine(1, 10, 0.3, undefined)).toBe(true);
    const sr = {
      type: "success_rate" as const,
      total: 10,
      correct: 1,
      rate_pct: 10,
      min_attempts: 1,
      required_rate_pct: 80,
    };
    expect(shouldShowLockedMidMotivationLine(1, 10, 0.3, sr)).toBe(false);
  });

  it("shouldShowLockedZeroMotivationLine", () => {
    expect(shouldShowLockedZeroMotivationLine(0, 5)).toBe(true);
    expect(shouldShowLockedZeroMotivationLine(0.1, 5)).toBe(false);
  });
});
