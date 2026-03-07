import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useProgressTimeline, PROGRESS_TIMELINE_QUERY_KEY } from "@/hooks/useProgressTimeline";
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

const mockTimelineResponse = {
  period: "7d",
  from: "2026-03-01",
  to: "2026-03-07",
  points: [
    {
      date: "2026-03-01",
      attempts: 7,
      correct: 5,
      success_rate_pct: 71.4,
      avg_time_spent_s: 32.1,
      by_type: { addition: { attempts: 7, correct: 5, success_rate_pct: 71.4 } },
    },
  ],
  summary: {
    total_attempts: 7,
    total_correct: 5,
    overall_success_rate_pct: 71.4,
  },
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useProgressTimeline", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("a une query key stable incluant la période", () => {
    expect(PROGRESS_TIMELINE_QUERY_KEY).toEqual(["user", "progress", "timeline"]);
  });

  it("appelle l'API avec la période correcte", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue(mockTimelineResponse);

    const { result } = renderHook(() => useProgressTimeline("7d"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(api.get).toHaveBeenCalledWith("/api/users/me/progress/timeline?period=7d");
  });

  it("retourne les données mappées correctement", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue(mockTimelineResponse);

    const { result } = renderHook(() => useProgressTimeline("7d"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockTimelineResponse);
    expect(result.current.data?.period).toBe("7d");
    expect(result.current.data?.points).toHaveLength(1);
    expect(result.current.data?.points?.[0]?.success_rate_pct).toBe(71.4);
    expect(result.current.data?.summary.overall_success_rate_pct).toBe(71.4);
  });

  it("retourne isLoading true pendant le chargement", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockImplementation(() => new Promise(() => {})); // Jamais résolu

    const { result } = renderHook(() => useProgressTimeline("30d"), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);
  });

  it("retourne isError true en cas d'erreur API", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useProgressTimeline("7d"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });
});
