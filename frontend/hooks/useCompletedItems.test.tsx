import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCompletedChallenges, useCompletedExercises } from "@/hooks/useCompletedItems";
import type { ReactNode } from "react";

vi.mock("@/lib/api/client", () => ({
  api: {
    get: vi.fn(),
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

vi.mock("@/lib/utils/debug", () => ({
  debugLog: vi.fn(),
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useCompletedExercises", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("expose isCompleted via lookup O(1) aligné sur completed_ids", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({ completed_ids: [10, 20, 30] });

    const { result } = renderHook(() => useCompletedExercises(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.completedIds).toEqual([10, 20, 30]));
    expect(result.current.isCompleted(20)).toBe(true);
    expect(result.current.isCompleted(99)).toBe(false);
  });
});

describe("useCompletedChallenges", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("expose isCompleted via lookup O(1) aligné sur completed_ids", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({ completed_ids: [7, 8] });

    const { result } = renderHook(() => useCompletedChallenges(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.completedIds).toEqual([7, 8]));
    expect(result.current.isCompleted(7)).toBe(true);
    expect(result.current.isCompleted(0)).toBe(false);
  });
});
