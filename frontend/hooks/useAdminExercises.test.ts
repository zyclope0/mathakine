import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import { useAdminExercises } from "@/hooks/useAdminExercises";

const { mockGet, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPatch: vi.fn(),
}));

vi.mock("@/lib/api/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api/client")>("@/lib/api/client");
  return {
    ...actual,
    api: {
      ...actual.api,
      get: mockGet,
      patch: mockPatch,
    },
  };
});

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
  return function W({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

const item = {
  id: 1,
  title: "t",
  exercise_type: "addition",
  difficulty: "easy",
  age_group: "6-8",
  is_archived: false,
  attempt_count: 0,
  success_rate: 0,
  created_at: null,
};

describe("useAdminExercises", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPatch.mockReset();
  });

  it("loads list with defaults", async () => {
    mockGet.mockResolvedValueOnce({ items: [item], total: 1 });

    const { result } = renderHook(() => useAdminExercises(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/exercises?skip=0&limit=20");
    expect(result.current.exercises).toHaveLength(1);
    expect(result.current.total).toBe(1);
  });

  it("passes filters in query string", async () => {
    mockGet.mockResolvedValueOnce({ items: [], total: 0 });

    renderHook(
      () =>
        useAdminExercises({
          archived: false,
          type: "addition",
          search: "q",
          sort: "title",
          order: "asc",
          skip: 0,
          limit: 10,
        }),
      { wrapper: wrapper() }
    );

    await waitFor(() => expect(mockGet).toHaveBeenCalled());
    expect(mockGet).toHaveBeenCalledWith(
      "/api/admin/exercises?archived=false&type=addition&search=q&sort=title&order=asc&skip=0&limit=10"
    );
  });

  it("query error", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("fail", 500));

    const { result } = renderHook(() => useAdminExercises(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
  });

  it("updateArchived calls patch", async () => {
    mockGet.mockResolvedValue({ items: [], total: 0 });
    mockPatch.mockResolvedValueOnce({ id: 1, title: "t", is_archived: true });

    const { result } = renderHook(() => useAdminExercises(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.updateArchived({ exerciseId: 1, isArchived: true });
    });

    expect(mockPatch).toHaveBeenCalledWith("/api/admin/exercises/1", { is_archived: true });
  });
});
