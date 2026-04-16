import { createElement, type ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { useAdminModeration } from "@/hooks/useAdminModeration";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
    },
  };
});

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

const sampleData = {
  exercises: [
    {
      id: 1,
      title: "E",
      exercise_type: "a",
      age_group: "6-8",
      is_archived: false,
      created_at: null,
    },
  ],
  challenges: [
    {
      id: 2,
      title: "C",
      challenge_type: "x",
      age_group: "6-8",
      is_archived: false,
      created_at: null,
    },
  ],
  total_exercises: 1,
  total_challenges: 1,
};

describe("useAdminModeration", () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it("default type=all requests encoded type", async () => {
    mockGet.mockResolvedValueOnce(sampleData);

    const { result } = renderHook(() => useAdminModeration(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/moderation?type=all");
    expect(result.current.exercises).toHaveLength(1);
    expect(result.current.challenges).toHaveLength(1);
    expect(result.current.totalExercises).toBe(1);
    expect(result.current.totalChallenges).toBe(1);
    expect(result.current.data).toEqual(sampleData);
  });

  it("type=exercises", async () => {
    mockGet.mockResolvedValueOnce({ ...sampleData, challenges: [], total_challenges: 0 });

    const { result } = renderHook(() => useAdminModeration("exercises"), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/moderation?type=exercises");
  });

  it("type=challenges", async () => {
    mockGet.mockResolvedValueOnce({ ...sampleData, exercises: [], total_exercises: 0 });

    const { result } = renderHook(() => useAdminModeration("challenges"), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/moderation?type=challenges");
  });

  it("exposes error when request fails", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("fail", 500));

    const { result } = renderHook(() => useAdminModeration("all"), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.data).toBeNull();
  });
});
