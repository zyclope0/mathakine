/**
 * Unit tests for useSubmitAnswer (TEST-SUBMIT-ANSWER-01) — API, React Query, toasts mocked; no UI.
 */

import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { trackFirstAttempt } from "@/lib/analytics/edtech";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";

vi.mock("@/lib/api/client", () => ({
  api: {
    post: vi.fn(),
  },
  ApiClientError: class ApiClientError extends Error {
    status: number;
    constructor(message: string, status: number) {
      super(message);
      this.name = "ApiClientError";
      this.status = status;
    }
  },
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    info: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("@/lib/analytics/edtech", () => ({
  trackFirstAttempt: vi.fn(),
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, values?: Record<string, string | number | boolean>) => {
    if (key === "badges.progressNotificationDesc" && values) {
      return `desc:${String(values.name)}:${String(values.count)}`;
    }
    return key;
  },
}));

const mockPost = vi.mocked(api.post);
const mockToastSuccess = vi.mocked(toast.success);
const mockToastInfo = vi.mocked(toast.info);
const mockToastError = vi.mocked(toast.error);
const mockTrackFirstAttempt = vi.mocked(trackFirstAttempt);

function refetchCalledForQueryKey(
  refetchSpy: { mock: { calls: ReadonlyArray<readonly unknown[]> } },
  queryKey: readonly unknown[]
): boolean {
  return refetchSpy.mock.calls.some((call) => {
    const arg0 = call[0];
    if (arg0 == null || typeof arg0 !== "object" || !("queryKey" in arg0)) {
      return false;
    }
    const key = (arg0 as { queryKey: unknown }).queryKey;
    return (
      Array.isArray(key) && key.length === queryKey.length && key.every((k, i) => k === queryKey[i])
    );
  });
}

function createTestContext() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
  const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
  const refetchSpy = vi.spyOn(queryClient, "refetchQueries");
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return { invalidateSpy, refetchSpy, Wrapper };
}

describe("useSubmitAnswer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("expose submitAnswer, isSubmitting et submitResult", () => {
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });
    expect(typeof result.current.submitAnswer).toBe("function");
    expect(result.current.isSubmitting).toBe(false);
    expect(result.current.submitResult).toBeUndefined();
  });

  it("succès générique : POST attempt sans exercise_id dans le body, invalidations exercise + user stats, trackFirstAttempt exercise par défaut", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "x",
    });
    const { invalidateSpy, refetchSpy, Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({ exercise_id: 99, answer: "a" });
    });

    expect(mockPost).toHaveBeenCalledTimes(1);
    expect(mockPost).toHaveBeenCalledWith("/api/exercises/99/attempt", { answer: "a" });
    expect(mockTrackFirstAttempt).toHaveBeenCalledWith("exercise", 99);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["exercise", 99] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["user", "stats"] });
    expect(refetchCalledForQueryKey(refetchSpy, ["completed-exercises"])).toBe(false);
    expect(invalidateSpy).not.toHaveBeenCalledWith({ queryKey: ["completed-exercises"] });
    await waitFor(() => {
      expect(result.current.submitResult).toEqual({
        is_correct: false,
        correct_answer: "x",
      });
    });
  });

  it("succès générique : analytics_type transmis à trackFirstAttempt", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "n",
    });
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({
        exercise_id: 7,
        answer: "1",
        analytics_type: "challenge",
      });
    });

    expect(mockTrackFirstAttempt).toHaveBeenCalledWith("challenge", 7);
  });

  it("succès générique : corps inclut time_spent sans exercise_id", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "ok",
    });
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({
        exercise_id: 5,
        answer: "42",
        time_spent: 12,
        analytics_type: "interleaved",
      });
    });

    expect(mockPost).toHaveBeenCalledWith("/api/exercises/5/attempt", {
      answer: "42",
      time_spent: 12,
      analytics_type: "interleaved",
    });
    expect(mockTrackFirstAttempt).toHaveBeenCalledWith("interleaved", 5);
  });

  it("succès correct : invalidations et refetch completed-exercises, badges, progress, recommendations, daily-challenges", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: true,
      correct_answer: "ok",
    });
    const { invalidateSpy, refetchSpy, Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({ exercise_id: 3, answer: "ok" });
    });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["exercise", 3] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["user", "stats"] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["completed-exercises"] });
    expect(refetchCalledForQueryKey(refetchSpy, ["completed-exercises"])).toBe(true);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["badges"] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["user", "progress"] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["recommendations"] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["daily-challenges"] });
  });

  it("badges gagnés : toast succès par badge avec nom et sous-titre thématique si présent", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "x",
      new_badges: [
        { id: 1, name: "Alpha", points_reward: 10, thematic_title: "  Orbit  " },
        { id: 2, name: "Beta", points_reward: 5 },
      ],
    });
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({ exercise_id: 1, answer: "a" });
    });

    expect(mockToastSuccess).toHaveBeenCalledTimes(2);
    expect(mockToastSuccess).toHaveBeenNthCalledWith(
      1,
      "badges.badgeUnlocked",
      expect.objectContaining({
        description: "Alpha - Orbit",
        duration: 5000,
      })
    );
    expect(mockToastSuccess).toHaveBeenNthCalledWith(
      2,
      "badges.badgeUnlocked",
      expect.objectContaining({
        description: "Beta",
        duration: 5000,
      })
    );
    expect(mockToastInfo).not.toHaveBeenCalled();
  });

  it("progression sans nouveau badge : toast info avec interpolation name / remaining", async () => {
    mockPost.mockResolvedValueOnce({
      is_correct: false,
      correct_answer: "x",
      progress_notification: { name: "Galaxy", remaining: 4 },
    });
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.submitAnswer({ exercise_id: 2, answer: "b" });
    });

    expect(mockToastSuccess).not.toHaveBeenCalled();
    expect(mockToastInfo).toHaveBeenCalledTimes(1);
    expect(mockToastInfo).toHaveBeenCalledWith(
      "badges.progressNotification",
      expect.objectContaining({
        description: "desc:Galaxy:4",
        duration: 4000,
      })
    );
  });

  it("erreur API : toast erreur avec message quand présent", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("save failed", 500));
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await expect(result.current.submitAnswer({ exercise_id: 8, answer: "z" })).rejects.toThrow(
        "save failed"
      );
    });

    expect(mockToastError).toHaveBeenCalledWith(
      "generic.submitError",
      expect.objectContaining({ description: "save failed" })
    );
  });

  it("erreur API : toast erreur avec clé de fallback si message vide", async () => {
    mockPost.mockRejectedValueOnce(new ApiClientError("", 400));
    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    await act(async () => {
      await expect(result.current.submitAnswer({ exercise_id: 8, answer: "z" })).rejects.toThrow();
    });

    expect(mockToastError).toHaveBeenCalledWith(
      "generic.submitError",
      expect.objectContaining({ description: "generic.submitErrorDescription" })
    );
  });

  it("isSubmitting true pendant la mutation puis false après résolution", async () => {
    let resolvePost!: (value: unknown) => void;
    const postPromise = new Promise<unknown>((resolve) => {
      resolvePost = resolve;
    });
    mockPost.mockImplementationOnce(() => postPromise as Promise<unknown>);

    const { Wrapper } = createTestContext();
    const { result } = renderHook(() => useSubmitAnswer(), { wrapper: Wrapper });

    void act(() => {
      void result.current.submitAnswer({ exercise_id: 11, answer: "p" });
    });

    await waitFor(() => {
      expect(result.current.isSubmitting).toBe(true);
    });

    await act(async () => {
      resolvePost({ is_correct: false, correct_answer: "p" });
    });

    await waitFor(() => {
      expect(result.current.isSubmitting).toBe(false);
    });
    expect(result.current.submitResult).toEqual({ is_correct: false, correct_answer: "p" });
  });
});
