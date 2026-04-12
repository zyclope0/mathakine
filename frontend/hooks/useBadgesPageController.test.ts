/**
 * Tests unitaires de useBadgesPageController.
 * FFI-L12
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useBadgesPageController } from "@/hooks/useBadgesPageController";
import type { Badge, UserBadge } from "@/types/api";
import type { BadgeProgressItem } from "@/hooks/useBadgesProgress";

// Mock canvas-confetti pour éviter un import dynamique réel
vi.mock("canvas-confetti", () => ({
  default: vi.fn(),
}));

Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
  value: vi.fn(),
  writable: true,
});

// ─── Fixtures ─────────────────────────────────────────────────────────────────

function makeBadge(id: number, overrides: Partial<Badge> = {}): Badge {
  return {
    id,
    code: `b${id}`,
    name: `Badge ${id}`,
    description: "",
    category: "progression",
    difficulty: "bronze",
    points_reward: 10,
    is_active: true,
    is_secret: false,
    ...overrides,
  };
}

function makeUserBadge(id: number, earned_at = "2024-01-01"): UserBadge {
  return {
    id,
    code: `b${id}`,
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

function makeProgress(
  id: number,
  progress: number,
  current: number,
  target: number
): BadgeProgressItem {
  return { id, code: `b${id}`, name: `Badge ${id}`, progress, current, target };
}

const defaultArgs = {
  earnedBadges: [] as UserBadge[],
  availableBadges: [] as Badge[],
  inProgress: [] as BadgeProgressItem[],
  earnedCount: 0,
  isLoading: false,
  rankInfo: { title: "Cadet", icon: "🌟", color: "text-slate-400" },
};

// ─── clearFilters ─────────────────────────────────────────────────────────────

describe("useBadgesPageController — clearFilters", () => {
  it("réinitialise tous les filtres", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));

    act(() => {
      result.current.setFilterStatus("earned");
      result.current.setFilterCategory("mastery");
      result.current.setFilterDifficulty("gold");
      result.current.setSortBy("progress");
    });

    expect(result.current.hasActiveFilters).toBe(true);

    act(() => {
      result.current.clearFilters();
    });

    expect(result.current.filterStatus).toBe("all");
    expect(result.current.filterCategory).toBe("all");
    expect(result.current.filterDifficulty).toBe("all");
    expect(result.current.sortBy).toBe("category");
    expect(result.current.hasActiveFilters).toBe(false);
  });
});

// ─── defaultTab sync ──────────────────────────────────────────────────────────

describe("useBadgesPageController — defaultTab", () => {
  it("defaultTab = toUnlock si aucun inProgress avec target", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.defaultTab).toBe("toUnlock");
    expect(result.current.activeTab).toBe("toUnlock");
  });

  it("defaultTab = inProgress si des badges ont une target", () => {
    const args = {
      ...defaultArgs,
      availableBadges: [makeBadge(1)],
      inProgress: [makeProgress(1, 0.3, 3, 10)],
    };
    const { result } = renderHook(() => useBadgesPageController(args));
    expect(result.current.defaultTab).toBe("inProgress");
    expect(result.current.activeTab).toBe("inProgress");
  });
});

// ─── tab switch ───────────────────────────────────────────────────────────────

describe("useBadgesPageController — bascule tab", () => {
  it("setActiveTab change l'onglet", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    act(() => {
      result.current.setActiveTab("inProgress");
    });
    expect(result.current.activeTab).toBe("inProgress");
  });

  it("isToUnlockTab est true quand activeTab = toUnlock", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.isToUnlockTab).toBe(true);
    act(() => {
      result.current.setActiveTab("inProgress");
    });
    expect(result.current.isToUnlockTab).toBe(false);
  });
});

// ─── expansions ───────────────────────────────────────────────────────────────

describe("useBadgesPageController — expansions", () => {
  it("setCollectionExpanded bascule l'expansion de la collection", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.collectionExpanded).toBe(false);
    act(() => {
      result.current.setCollectionExpanded(true);
    });
    expect(result.current.collectionExpanded).toBe(true);
  });

  it("setStatsExpanded bascule l'expansion des stats", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.statsExpanded).toBe(false);
    act(() => {
      result.current.setStatsExpanded(true);
    });
    expect(result.current.statsExpanded).toBe(true);
  });

  it("setToUnlockExpanded bascule l'expansion à débloquer", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.toUnlockExpanded).toBe(false);
    act(() => {
      result.current.setToUnlockExpanded(true);
    });
    expect(result.current.toUnlockExpanded).toBe(true);
  });
});

// ─── dérivés badges ───────────────────────────────────────────────────────────

describe("useBadgesPageController — dérivés", () => {
  it("closestBadges filtre >= 50% progress parmi inProgressWithTarget", () => {
    const args = {
      ...defaultArgs,
      availableBadges: [makeBadge(1), makeBadge(2)],
      inProgress: [makeProgress(1, 0.7, 7, 10), makeProgress(2, 0.3, 3, 10)],
    };
    const { result } = renderHook(() => useBadgesPageController(args));
    expect(result.current.closestBadges).toHaveLength(1);
    expect(result.current.closestBadges[0]?.id).toBe(1);
  });

  it("lastExploits retourne les 4 derniers badges par date", () => {
    const badges = [1, 2, 3, 4, 5].map((i) => makeBadge(i));
    const earned = [
      makeUserBadge(1, "2024-01-01"),
      makeUserBadge(2, "2024-06-01"),
      makeUserBadge(3, "2024-03-01"),
      makeUserBadge(4, "2024-12-01"),
      makeUserBadge(5, "2024-09-01"),
    ];
    const args = {
      ...defaultArgs,
      earnedBadges: earned,
      availableBadges: badges,
      earnedCount: 5,
    };
    const { result } = renderHook(() => useBadgesPageController(args));
    expect(result.current.lastExploits).toHaveLength(4);
    expect(result.current.lastExploits[0]?.id).toBe(4);
  });

  it("progressPercent = 0 si aucun badge disponible", () => {
    const { result } = renderHook(() => useBadgesPageController(defaultArgs));
    expect(result.current.progressPercent).toBe(0);
  });
});

// ─── confetti (smoke tests) ──────────────────────────────────────────────────

describe("useBadgesPageController — confetti (smoke)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("le hook s'initialise sans erreur avec earnedCount > 0", async () => {
    const args = { ...defaultArgs, earnedCount: 3, isLoading: false };
    const { result } = renderHook(() => useBadgesPageController(args));
    await act(async () => {});
    // Vérifie que le hook a bien rendu sans crash
    expect(result.current.progressPercent).toBeDefined();
    expect(result.current.hasActiveFilters).toBe(false);
  });

  it("le hook s'initialise sans erreur avec earnedCount = 0 (pas de confetti)", async () => {
    const args = { ...defaultArgs, earnedCount: 0, isLoading: false };
    const { result } = renderHook(() => useBadgesPageController(args));
    await act(async () => {});
    expect(result.current.motivationInfo).toBeNull();
  });
});
