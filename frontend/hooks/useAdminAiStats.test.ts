import { createElement, type ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import {
  useAdminAiEvalHarnessRuns,
  useAdminAiStats,
  useAdminGenerationMetrics,
} from "@/hooks/useAdminAiStats";

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

const emptyAiStats = {
  days: 7,
  stats: { total_tokens: 0, total_cost: 0, average_tokens: 0, count: 0 },
  daily_summary: {},
};

const emptyGenMetrics = {
  days: 7,
  summary: {
    success_rate: 1,
    validation_failure_rate: 0,
    auto_correction_rate: 0,
    average_duration: 0,
    by_type: {},
  },
};

const emptyHarness = { runs: [], limit: 20, disclaimer_fr: "" };

describe("useAdminAiStats", () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it("fetches ai-stats with days only (no challenge_type)", async () => {
    mockGet.mockResolvedValueOnce(emptyAiStats);

    const { result } = renderHook(() => useAdminAiStats(7), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/ai-stats?days=7");
    expect(result.current.data).toEqual(emptyAiStats);
    expect(result.current.error).toBeNull();
  });

  it("includes challenge_type when metricKey is set", async () => {
    mockGet.mockResolvedValueOnce(emptyAiStats);

    const { result } = renderHook(() => useAdminAiStats(3, "sequence"), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/ai-stats?days=3&challenge_type=sequence");
    expect(result.current.data).toEqual(emptyAiStats);
  });

  it("exposes error on failure", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("nope", 502));

    const { result } = renderHook(() => useAdminAiStats(1), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.data).toBeNull();
  });
});

describe("useAdminGenerationMetrics", () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it("fetches generation-metrics for given days", async () => {
    mockGet.mockResolvedValueOnce(emptyGenMetrics);

    const { result } = renderHook(() => useAdminGenerationMetrics(14), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/generation-metrics?days=14");
    expect(result.current.data).toEqual(emptyGenMetrics);
  });

  it("exposes error on failure", async () => {
    mockGet.mockRejectedValueOnce(new ApiClientError("nope", 500));

    const { result } = renderHook(() => useAdminGenerationMetrics(1), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.data).toBeNull();
  });
});

describe("useAdminAiEvalHarnessRuns", () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it("fetches harness runs with default limit", async () => {
    mockGet.mockResolvedValueOnce(emptyHarness);

    const { result } = renderHook(() => useAdminAiEvalHarnessRuns(), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/ai-eval-harness-runs?limit=20");
    expect(result.current.data).toEqual(emptyHarness);
  });

  it("uses custom limit", async () => {
    mockGet.mockResolvedValueOnce({ ...emptyHarness, limit: 5 });

    const { result } = renderHook(() => useAdminAiEvalHarnessRuns(5), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(mockGet).toHaveBeenCalledWith("/api/admin/ai-eval-harness-runs?limit=5");
  });
});
