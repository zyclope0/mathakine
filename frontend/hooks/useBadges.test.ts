import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useBadges } from "@/hooks/useBadges";

const mockRouterPush = vi.hoisted(() => vi.fn());

const { mockGet, mockPost, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      post: mockPost,
      patch: mockPatch,
    },
  };
});

vi.mock("@/lib/stores/localeStore", () => ({
  useLocaleStore: () => ({ locale: "fr" as const }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockRouterPush }),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("@/lib/gamification/badgeThematicTitle", () => ({
  readBadgeThematicTitleRaw: vi.fn(() => ""),
}));

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

function defaultGets() {
  mockGet.mockImplementation((url: string) => {
    if (url.includes("/api/badges/user")) {
      return Promise.resolve({
        success: true,
        data: {
          earned_badges: [],
          user_stats: { pinned_badge_ids: [] as number[], total_points: 0 },
        },
      });
    }
    if (url.includes("/api/badges/available")) {
      return Promise.resolve({ success: true, data: [] });
    }
    if (url.includes("/api/badges/stats")) {
      return Promise.resolve({
        success: true,
        data: { total_badges: 0, total_points: 0 },
      });
    }
    if (url.includes("/api/badges/rarity")) {
      return Promise.resolve({
        success: true,
        data: { total_users: 1, by_badge: {} },
      });
    }
    return Promise.reject(new Error(`unmocked GET ${url}`));
  });
}

describe("useBadges", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPost.mockReset();
    mockPatch.mockReset();
    mockRouterPush.mockClear();
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
    vi.mocked(toast.info).mockClear();
    defaultGets();
  });

  it("resolves loading and exposes empty lists", async () => {
    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.earnedBadges).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.rarityMap).toEqual({});
  });

  it("surfaces query error when user badges fail", async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes("/api/badges/user")) {
        return Promise.reject(new ApiClientError("nope", 500));
      }
      if (url.includes("/api/badges/available")) {
        return Promise.resolve({ success: true, data: [] });
      }
      if (url.includes("/api/badges/stats")) {
        return Promise.resolve({
          success: true,
          data: { total_badges: 0, total_points: 0 },
        });
      }
      if (url.includes("/api/badges/rarity")) {
        return Promise.resolve({
          success: true,
          data: { total_users: 1, by_badge: {} },
        });
      }
      return Promise.reject(new Error(`unmocked ${url}`));
    });

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
  });

  it("checkBadges with new badges shows success toasts", async () => {
    mockPost.mockResolvedValueOnce({
      success: true,
      new_badges: [{ id: 1, code: "c", name: "N" }],
      badges_earned: 1,
      message: "ok",
    });

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.checkBadges();
    });

    expect(toast.success).toHaveBeenCalledWith("badges.newBadgeUnlocked", expect.any(Object));
  });

  it("checkBadges with no new badges shows info toast", async () => {
    mockPost.mockResolvedValueOnce({
      success: true,
      new_badges: [],
      badges_earned: 0,
      message: "none",
    });

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.checkBadges();
    });

    expect(toast.info).toHaveBeenCalledWith("badges.noBadge", expect.any(Object));
  });

  it("checkBadges 401 redirects to login", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("auth", 401));

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await expect(result.current.checkBadges()).rejects.toBeDefined();
    });

    expect(mockRouterPush).toHaveBeenCalledWith("/login");
  });

  it("checkBadges other error shows toast.error", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("fail", 503));

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await expect(result.current.checkBadges()).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalledWith("badges.checkError", expect.any(Object));
  });

  it("pinBadges calls patch endpoint", async () => {
    mockPatch.mockResolvedValueOnce({ success: true, data: { pinned_badge_ids: [1, 2] } });

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.pinBadges([1, 2]);
    });

    expect(mockPatch).toHaveBeenCalledWith("/api/badges/pin", { badge_ids: [1, 2] });
  });

  it("merges earned-only badge into available list", async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes("/api/badges/user")) {
        return Promise.resolve({
          success: true,
          data: {
            earned_badges: [
              {
                id: 42,
                code: "solo",
                name: "Solo",
                category: null,
                difficulty: null,
                points_reward: 1,
                earned_at: "2020-01-01",
              },
            ],
            user_stats: {},
          },
        });
      }
      if (url.includes("/api/badges/available")) {
        return Promise.resolve({ success: true, data: [] });
      }
      if (url.includes("/api/badges/stats")) {
        return Promise.resolve({ success: true, data: { total_badges: 1, total_points: 1 } });
      }
      if (url.includes("/api/badges/rarity")) {
        return Promise.resolve({ success: true, data: { total_users: 1, by_badge: {} } });
      }
      return Promise.reject(new Error(url));
    });

    const { result } = renderHook(() => useBadges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.availableBadges.some((b) => b.id === 42)).toBe(true);
  });
});
