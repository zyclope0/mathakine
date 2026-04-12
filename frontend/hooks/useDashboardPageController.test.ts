import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useDashboardPageController } from "@/hooks/useDashboardPageController";
import { useAuth } from "@/hooks/useAuth";
import { useChallengesProgress } from "@/hooks/useChallengesProgress";
import { useDailyChallenges } from "@/hooks/useDailyChallenges";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useUserStats } from "@/hooks/useUserStats";
import { buildDashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import { useLocaleStore } from "@/lib/stores/localeStore";

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/hooks/useChallengesProgress", () => ({
  useChallengesProgress: vi.fn(),
}));

vi.mock("@/hooks/useDailyChallenges", () => ({
  useDailyChallenges: vi.fn(),
}));

vi.mock("@/hooks/useProgressStats", () => ({
  useProgressStats: vi.fn(),
}));

vi.mock("@/hooks/useUserStats", () => ({
  useUserStats: vi.fn(),
}));

vi.mock("@/lib/dashboard/buildDashboardExportSnapshot", () => ({
  buildDashboardExportSnapshot: vi.fn(),
}));

vi.mock("@/lib/stores/localeStore", () => ({
  useLocaleStore: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

const invalidateQueries = vi.fn().mockResolvedValue(undefined);
const refetch = vi.fn().mockResolvedValue(undefined);

function buildUser(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    username: "padawan",
    total_points: 420,
    gamification_level: { current: 4, current_xp: 120, next_level_xp: 200 },
    ...overrides,
  };
}

function buildStats(overrides: Record<string, unknown> = {}) {
  return {
    total_exercises: 12,
    success_rate: 83,
    total_challenges: 3,
    spaced_repetition: {
      due_today: 2,
      mastered: 5,
      learning: 4,
      reviewed_today: 1,
      overdue: 0,
      success_rate: 90,
      retention_rate: 88,
      total_cards: 9,
    },
    recent_activity: [{ time: "2026-04-08T10:00:00Z", description: "Activité", type: "generic" }],
    ...overrides,
  };
}

function buildProgressStats(overrides: Record<string, unknown> = {}) {
  return {
    total_attempts: 20,
    correct_attempts: 16,
    accuracy: 80,
    average_time: 42,
    exercises_completed: 12,
    highest_streak: 5,
    current_streak: 3,
    by_category: { calcul: { completed: 4, accuracy: 80, attempts: 5 } },
    ...overrides,
  };
}

function buildChallengesProgress(overrides: Record<string, unknown> = {}) {
  return {
    completed_challenges: 3,
    total_challenges: 10,
    success_rate: 30,
    average_time: 55,
    challenges: [],
    ...overrides,
  };
}

function renderDashboardController() {
  return renderHook(() =>
    useDashboardPageController({
      tDashboard: (key, values) =>
        values ? `${key}:${JSON.stringify(values)}` : `dashboard:${key}`,
      tDashboardToasts: (key) => `toast:${key}`,
    })
  );
}

describe("useDashboardPageController", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    vi.mocked(useQueryClient).mockReturnValue({
      invalidateQueries,
    } as unknown as ReturnType<typeof useQueryClient>);

    vi.mocked(useAuth).mockReturnValue({
      user: buildUser(),
    } as unknown as ReturnType<typeof useAuth>);

    vi.mocked(useLocaleStore).mockReturnValue({
      locale: "fr",
    } as unknown as ReturnType<typeof useLocaleStore>);

    vi.mocked(useUserStats).mockReturnValue({
      stats: buildStats(),
      isLoading: false,
      error: null,
      refetch,
    } as unknown as ReturnType<typeof useUserStats>);

    vi.mocked(useProgressStats).mockReturnValue({
      data: buildProgressStats(),
      isLoading: false,
    } as unknown as ReturnType<typeof useProgressStats>);

    vi.mocked(useChallengesProgress).mockReturnValue({
      data: buildChallengesProgress(),
      isLoading: false,
    } as unknown as ReturnType<typeof useChallengesProgress>);

    vi.mocked(useDailyChallenges).mockReturnValue({
      challenges: [{ id: 1, challenge_type: "logic_challenge" }],
    } as unknown as ReturnType<typeof useDailyChallenges>);

    vi.mocked(buildDashboardExportSnapshot).mockReturnValue({
      generatedAt: "2026-04-08T12:00:00.000Z",
    } as unknown as ReturnType<typeof buildDashboardExportSnapshot>);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("builds derived dashboard state and toggles the dashboard document marker", async () => {
    const { result, unmount } = renderDashboardController();

    expect(result.current.timeRange).toBe("30");
    expect(result.current.activeTab).toBe("overview");
    expect(result.current.timelinePeriod).toBe("7d");
    expect(result.current.timeRangeLabel).toBe("dashboard:timeRange.30days");
    expect(result.current.locale).toBe("fr");
    expect(result.current.exportSnapshot).toEqual({ generatedAt: "2026-04-08T12:00:00.000Z" });

    expect(buildDashboardExportSnapshot).toHaveBeenCalledWith(
      expect.objectContaining({
        username: "padawan",
        timeRange: "30",
        timeRangeLabel: "dashboard:timeRange.30days",
      }),
      expect.any(Date)
    );
    expect(document.documentElement.getAttribute("data-mathakine-dashboard")).toBe("");

    unmount();

    expect(document.documentElement.hasAttribute("data-mathakine-dashboard")).toBe(false);
  });

  it("refreshes dashboard queries and emits a success toast", async () => {
    const { result } = renderDashboardController();

    await act(async () => {
      await result.current.handleRefresh();
    });

    expect(refetch).toHaveBeenCalledTimes(1);
    expect(invalidateQueries).toHaveBeenCalledTimes(8);
    expect(toast.success).toHaveBeenCalledWith("toast:statsUpdated");

    act(() => {
      vi.runAllTimers();
    });

    expect(result.current.isRefreshing).toBe(false);
  });

  it("keeps auth-safe behavior when refresh fails", async () => {
    refetch.mockRejectedValueOnce(new Error("boom"));

    const { result } = renderDashboardController();

    await act(async () => {
      await result.current.handleRefresh();
    });

    expect(invalidateQueries).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalledWith("dashboard:error.title");

    act(() => {
      vi.runAllTimers();
    });

    expect(result.current.isRefreshing).toBe(false);
  });
});
