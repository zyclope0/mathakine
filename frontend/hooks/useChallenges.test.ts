import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useChallenges } from "@/hooks/useChallenges";

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      post: mockPost,
    },
  };
});

vi.mock("@/lib/stores/localeStore", () => ({
  useLocaleStore: () => ({ locale: "fr" as const }),
}));

vi.mock("@/lib/analytics/edtech", () => ({
  trackFirstAttempt: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, values?: Record<string, string | number>) => {
    if (values && key === "badges.progressNotificationDesc") {
      return `${values.name}:${values.count}`;
    }
    return key;
  },
}));

vi.mock("@/lib/gamification/badgeThematicTitle", () => ({
  readBadgeThematicTitleRaw: () => "",
}));

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

function mockListResponse() {
  mockGet.mockImplementation((url: string) => {
    if (url.includes("/api/challenges") && !url.includes("/attempt") && !url.includes("/hint")) {
      return Promise.resolve({ items: [], total: 0, hasMore: false });
    }
    return Promise.reject(new ApiClientError(`unexpected GET ${url}`, 500));
  });
}

describe("useChallenges", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPost.mockReset();
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
    vi.mocked(toast.info).mockClear();
    mockListResponse();
  });

  it("loads paginated challenges", async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes("/api/challenges") && !url.includes("/attempt") && !url.includes("/hint")) {
        return Promise.resolve({
          items: [{ id: 1, title: "C", challenge_type: "sequence", age_group: "6-8" } as never],
          total: 1,
          hasMore: false,
        });
      }
      return Promise.reject(new ApiClientError(`unexpected ${url}`, 500));
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.challenges).toHaveLength(1);
    expect(result.current.total).toBe(1);
    expect(result.current.error).toBeNull();
  });

  it("query error from list endpoint", async () => {
    mockGet.mockImplementation(() => Promise.reject(new ApiClientError("fail", 500)));

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull(), {
      timeout: 10_000,
    });
  });

  it("submitAnswer success with new_badges shows toast.success", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: true,
      new_badges: [{ id: 1, name: "B", thematic_title: null, star_wars_title: null }],
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.submitAnswer({ challenge_id: 5, answer: "x" });
    });

    expect(mockPost).toHaveBeenCalledWith("/api/challenges/5/attempt", {
      user_solution: "x",
      time_spent: undefined,
      hints_used: [],
    });
    expect(toast.success).toHaveBeenCalled();
  });

  it("submitAnswer when correct invalidates extended queries (no extra toasts)", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: true,
      new_badges: [],
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.submitAnswer({ challenge_id: 7, answer: "ok" });
    });

    expect(mockPost).toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
    expect(toast.info).not.toHaveBeenCalled();
  });

  it("submitAnswer success with progress_notification shows info toast", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      progress_notification: { name: "N", remaining: 2 },
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.submitAnswer({ challenge_id: 1, answer: "y" });
    });

    expect(toast.info).toHaveBeenCalled();
  });

  it("submitAnswer error shows toast.error", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("bad", 400));

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await expect(
        result.current.submitAnswer({ challenge_id: 1, answer: "z" })
      ).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalled();
  });

  it("getHint accumulates hint string", async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes("/hint?level=1")) {
        return Promise.resolve({ hint: "first" });
      }
      if (url.includes("/api/challenges") && !url.includes("/attempt")) {
        return Promise.resolve({ items: [], total: 0, hasMore: false });
      }
      return Promise.reject(new ApiClientError(`unexpected ${url}`, 500));
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.getHint(10);
    });

    expect(result.current.hints).toEqual(["first"]);
  });

  it("getHint error toasts", async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes("/hint")) {
        return Promise.reject(new ApiClientError("nope", 500));
      }
      if (url.includes("/api/challenges") && !url.includes("/attempt")) {
        return Promise.resolve({ items: [], total: 0, hasMore: false });
      }
      return Promise.reject(new ApiClientError(`unexpected ${url}`, 500));
    });

    const { result } = renderHook(() => useChallenges(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await expect(result.current.getHint(2)).rejects.toBeDefined();
    });

    expect(toast.error).toHaveBeenCalled();
  });
});
