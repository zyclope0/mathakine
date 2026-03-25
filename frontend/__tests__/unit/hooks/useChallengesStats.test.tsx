import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useChallengesStats } from "@/hooks/useChallengesStats";
import type { ReactNode } from "react";

vi.mock("@/lib/api/client", () => ({
  api: {
    get: vi.fn(),
  },
  ApiClientError: class ApiClientError extends Error {
    status: number;
    constructor(message: string, status: number) {
      super(message);
      this.status = status;
    }
  },
}));

const mockStats = {
  total: 12,
  total_archived: 1,
  by_type: { sequence: { count: 4, percentage: 33.3 } },
  by_difficulty: { EASY: { count: 6, percentage: 50 } },
  by_age_group: { "9-11": { count: 12, percentage: 100 } },
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useChallengesStats", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("appelle GET /api/challenges/stats", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue(mockStats);

    const { result } = renderHook(() => useChallengesStats(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(api.get).toHaveBeenCalledWith("/api/challenges/stats");
    expect(result.current.data?.total).toBe(12);
  });
});
