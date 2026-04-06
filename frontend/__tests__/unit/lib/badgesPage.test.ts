/**
 * Tests unitaires des helpers purs de lib/badges/badgesPage.ts
 * FFI-L12
 */

import { describe, it, expect } from "vitest";
import {
  getProgressionRankInfo,
  calcProgressPercent,
  buildProgressMap,
  filterBadges,
  countCloseBadges,
  hasActiveFilters,
  getClosestBadges,
  getLastExploits,
  getMotivationInfo,
  getInProgressWithTarget,
  getNextPinnedBadgeIds,
  sortEarnedWithPinned,
} from "@/lib/badges/badgesPage";
import type { Badge, UserBadge } from "@/types/api";
import type { BadgeProgressItem } from "@/hooks/useBadgesProgress";

// ─── Fixtures ─────────────────────────────────────────────────────────────────

function makeBadge(overrides: Partial<Badge> & { id: number }): Badge {
  return {
    id: overrides.id,
    code: overrides.code ?? `badge_${overrides.id}`,
    name: overrides.name ?? `Badge ${overrides.id}`,
    description: overrides.description ?? "",
    category: overrides.category ?? "progression",
    difficulty: overrides.difficulty ?? "bronze",
    points_reward: overrides.points_reward ?? 10,
    is_active: overrides.is_active ?? true,
    is_secret: overrides.is_secret ?? false,
    criteria_text: overrides.criteria_text ?? null,
    icon_url: overrides.icon_url ?? null,
  };
}

function makeUserBadge(id: number, earned_at: string): UserBadge {
  return {
    id,
    code: `badge_${id}`,
    name: `Badge ${id}`,
    earned_at,
    points_reward: 10,
    category: "progression",
    difficulty: "bronze",
    description: "",
    is_active: true,
    is_secret: false,
  };
}

function makeProgressItem(
  id: number,
  progress: number,
  current: number,
  target: number
): BadgeProgressItem {
  return {
    id,
    code: `badge_${id}`,
    name: `Badge ${id}`,
    progress,
    current,
    target,
  };
}

// ─── getProgressionRankInfo ───────────────────────────────────────────────────

describe("getProgressionRankInfo", () => {
  const tRank = (key: string) => `rank_${key}`;

  it("retourne le rang pour un bucket connu", () => {
    const info = getProgressionRankInfo("cadet", tRank);
    expect(info.title).toBe("rank_cadet");
  });

  it("fallback sur cadet pour un rang inconnu", () => {
    const info = getProgressionRankInfo("unknown_rank_xyz", tRank);
    expect(info.title).toBe("rank_cadet");
  });

  it("retourne une couleur non vide", () => {
    const info = getProgressionRankInfo("cadet", tRank);
    expect(info.color.length).toBeGreaterThan(0);
  });
});

// ─── calcProgressPercent ──────────────────────────────────────────────────────

describe("calcProgressPercent", () => {
  it("retourne 0 si totalCount = 0", () => {
    expect(calcProgressPercent(0, 0)).toBe(0);
  });

  it("retourne 50% si earned = 5, total = 10", () => {
    expect(calcProgressPercent(5, 10)).toBe(50);
  });

  it("retourne 100% si tous obtenus", () => {
    expect(calcProgressPercent(10, 10)).toBe(100);
  });
});

// ─── buildProgressMap ─────────────────────────────────────────────────────────

describe("buildProgressMap", () => {
  it("construit une map depuis inProgress valides", () => {
    const items = [makeProgressItem(1, 0.6, 6, 10), makeProgressItem(2, 0.3, 3, 10)];
    const map = buildProgressMap(items);
    expect(map[1]).toEqual({ current: 6, target: 10, progress: 0.6 });
    expect(map[2]).toEqual({ current: 3, target: 10, progress: 0.3 });
  });

  it("ignore les items sans target valide", () => {
    const items: BadgeProgressItem[] = [
      { id: 99, code: "b99", name: "B99", progress: 0.5, current: 5, target: 0 },
    ];
    const map = buildProgressMap(items);
    expect(map[99]).toBeUndefined();
  });
});

// ─── filterBadges ─────────────────────────────────────────────────────────────

describe("filterBadges", () => {
  const b1 = makeBadge({ id: 1, category: "progression", difficulty: "bronze" });
  const b2 = makeBadge({ id: 2, category: "mastery", difficulty: "gold" });
  const b3 = makeBadge({ id: 3, category: "progression", difficulty: "gold", is_secret: true });

  const earnedBadgeIds = new Set([1]);
  const progressMap = {};

  it("filtre status=all : tous visibles", () => {
    const result = filterBadges({
      availableBadges: [b1, b2, b3],
      earnedBadgeIds,
      filterStatus: "all",
      filterCategory: "all",
      filterDifficulty: "all",
      progressMap,
    });
    expect(result.filteredEarned).toHaveLength(1);
    expect(result.filteredLocked).toHaveLength(1); // b3 secret exclu sauf si earned
  });

  it("filtre status=earned : ne retourne que earned", () => {
    const result = filterBadges({
      availableBadges: [b1, b2],
      earnedBadgeIds,
      filterStatus: "earned",
      filterCategory: "all",
      filterDifficulty: "all",
      progressMap,
    });
    expect(result.filteredEarned).toHaveLength(1);
    expect(result.filteredLocked).toHaveLength(0);
  });

  it("filtre status=locked : ne retourne que locked", () => {
    const result = filterBadges({
      availableBadges: [b1, b2],
      earnedBadgeIds,
      filterStatus: "locked",
      filterCategory: "all",
      filterDifficulty: "all",
      progressMap,
    });
    expect(result.filteredEarned).toHaveLength(0);
    expect(result.filteredLocked).toHaveLength(1);
  });

  it("filtre status=close : locked avec progress >= 50%", () => {
    const pm = { 2: { current: 5, target: 10, progress: 0.6 } };
    const result = filterBadges({
      availableBadges: [b1, b2],
      earnedBadgeIds,
      filterStatus: "close",
      filterCategory: "all",
      filterDifficulty: "all",
      progressMap: pm,
    });
    expect(result.filteredEarned).toHaveLength(0);
    expect(result.filteredLocked).toHaveLength(1);
    expect(result.filteredLocked[0]?.id).toBe(2);
  });

  it("filtre par catégorie", () => {
    const result = filterBadges({
      availableBadges: [b1, b2],
      earnedBadgeIds,
      filterStatus: "all",
      filterCategory: "mastery",
      filterDifficulty: "all",
      progressMap,
    });
    expect(result.filteredEarned).toHaveLength(0);
    expect(result.filteredLocked).toHaveLength(1);
    expect(result.filteredLocked[0]?.id).toBe(2);
  });

  it("extrait les catégories disponibles", () => {
    const result = filterBadges({
      availableBadges: [b1, b2],
      earnedBadgeIds,
      filterStatus: "all",
      filterCategory: "all",
      filterDifficulty: "all",
      progressMap,
    });
    expect(result.categories).toContain("progression");
    expect(result.categories).toContain("mastery");
  });
});

// ─── hasActiveFilters ─────────────────────────────────────────────────────────

describe("hasActiveFilters", () => {
  it("retourne false pour les valeurs par défaut", () => {
    expect(hasActiveFilters("all", "all", "all", "category")).toBe(false);
  });

  it("retourne true si filterStatus != all", () => {
    expect(hasActiveFilters("earned", "all", "all", "category")).toBe(true);
  });

  it("retourne true si sortBy != category", () => {
    expect(hasActiveFilters("all", "all", "all", "progress")).toBe(true);
  });
});

// ─── getClosestBadges ─────────────────────────────────────────────────────────

describe("getClosestBadges", () => {
  it("retourne les badges avec progress >= 50%, triés décroissant, max 3", () => {
    const items: BadgeProgressItem[] = [
      makeProgressItem(1, 0.9, 9, 10),
      makeProgressItem(2, 0.3, 3, 10),
      makeProgressItem(3, 0.7, 7, 10),
      makeProgressItem(4, 0.8, 8, 10),
      makeProgressItem(5, 0.6, 6, 10),
    ];
    const result = getClosestBadges(items);
    expect(result).toHaveLength(3);
    expect(result[0]?.id).toBe(1); // 0.9
    expect(result[1]?.id).toBe(4); // 0.8
    expect(result[2]?.id).toBe(3); // 0.7
  });

  it("retourne [] si aucun badge >= 50%", () => {
    const items = [makeProgressItem(1, 0.2, 2, 10)];
    expect(getClosestBadges(items)).toHaveLength(0);
  });
});

// ─── getLastExploits ──────────────────────────────────────────────────────────

describe("getLastExploits", () => {
  it("retourne les 4 derniers badges par date décroissante", () => {
    const earned: UserBadge[] = [
      makeUserBadge(1, "2024-01-01"),
      makeUserBadge(2, "2024-06-01"),
      makeUserBadge(3, "2024-03-01"),
      makeUserBadge(4, "2024-12-01"),
      makeUserBadge(5, "2024-09-01"),
    ];
    const available = earned.map((eb) => makeBadge({ id: eb.id }));
    const result = getLastExploits(available, earned);
    expect(result).toHaveLength(4);
    expect(result[0]?.id).toBe(4); // dec
    expect(result[1]?.id).toBe(5); // sept
  });

  it("ignore les badges sans earned_at", () => {
    const earned: UserBadge[] = [makeUserBadge(1, "")];
    const available = [makeBadge({ id: 1 })];
    const result = getLastExploits(available, earned);
    expect(result).toHaveLength(0);
  });
});

// ─── getMotivationInfo ────────────────────────────────────────────────────────

describe("getMotivationInfo", () => {
  it("retourne null si 0 badges", () => {
    expect(getMotivationInfo(0, 50)).toBeNull();
  });

  it("retourne key=complete pour 100%", () => {
    expect(getMotivationInfo(10, 100)?.key).toBe("complete");
  });

  it("retourne key=legendary pour 75–99%", () => {
    expect(getMotivationInfo(5, 80)?.key).toBe("legendary");
  });

  it("retourne key=great pour 50–74%", () => {
    expect(getMotivationInfo(5, 60)?.key).toBe("great");
  });

  it("retourne key=good pour 25–49%", () => {
    expect(getMotivationInfo(5, 30)?.key).toBe("good");
  });

  it("retourne key=start pour < 25%", () => {
    expect(getMotivationInfo(1, 10)?.key).toBe("start");
  });
});

// ─── getInProgressWithTarget ─────────────────────────────────────────────────

describe("getInProgressWithTarget", () => {
  it("exclut les badges sans target", () => {
    const items: BadgeProgressItem[] = [
      { id: 1, code: "b1", name: "B1", progress: 0.5, current: 5, target: 0 },
      makeProgressItem(2, 0.3, 3, 10),
    ];
    const available = [makeBadge({ id: 1 }), makeBadge({ id: 2 })];
    expect(getInProgressWithTarget(items, available)).toHaveLength(1);
  });

  it("exclut les badges secrets", () => {
    const items = [makeProgressItem(1, 0.5, 5, 10)];
    const available = [makeBadge({ id: 1, is_secret: true })];
    expect(getInProgressWithTarget(items, available)).toHaveLength(0);
  });
});

// ─── countCloseBadges ─────────────────────────────────────────────────────────

describe("countCloseBadges", () => {
  it("compte les locked avec progress >= 0.5", () => {
    const locked = [makeBadge({ id: 1 }), makeBadge({ id: 2 })];
    const pm = {
      1: { current: 5, target: 10, progress: 0.5 },
      2: { current: 3, target: 10, progress: 0.3 },
    };
    expect(countCloseBadges(locked, pm)).toBe(1);
  });
});

// ─── sortEarnedWithPinned ─────────────────────────────────────────────────────

describe("sortEarnedWithPinned", () => {
  it("met les épinglés en premier", () => {
    const badges = [makeBadge({ id: 1 }), makeBadge({ id: 2 }), makeBadge({ id: 3 })];
    const result = sortEarnedWithPinned(badges, [3, 1]);
    expect(result[0]?.id).toBe(3);
    expect(result[1]?.id).toBe(1);
    expect(result[2]?.id).toBe(2);
  });

  it("retourne les non-épinglés intacts si pinnedIds vide", () => {
    const badges = [makeBadge({ id: 1 }), makeBadge({ id: 2 })];
    expect(sortEarnedWithPinned(badges, [])).toEqual(badges);
  });
});

describe("getNextPinnedBadgeIds", () => {
  it("retire un badge deja epingle", () => {
    expect(getNextPinnedBadgeIds([1, 2, 3], 2)).toEqual([1, 3]);
  });

  it("ajoute un badge non epingle", () => {
    expect(getNextPinnedBadgeIds([1, 2], 3)).toEqual([1, 2, 3]);
  });

  it("limite le total au maximum defini", () => {
    expect(getNextPinnedBadgeIds([1, 2, 3], 4)).toEqual([1, 2, 3]);
  });
});
