/**
 * Unit tests for useAdminAiMonitoringPageController (ACTIF-06-AI-MONITORING-01) —
 * days wiring, aggregated loading/error, harness limit, formatWorkloadLabel; mocks admin IA hooks.
 */

import type { ReactNode } from "react";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import {
  useAdminAiEvalHarnessRuns,
  useAdminAiStats,
  useAdminGenerationMetrics,
} from "@/hooks/useAdminAiStats";
import {
  HARNESS_RUNS_LIMIT,
  useAdminAiMonitoringPageController,
} from "@/hooks/useAdminAiMonitoringPageController";

vi.mock("@/hooks/useAdminAiStats", () => ({
  useAdminAiStats: vi.fn(),
  useAdminGenerationMetrics: vi.fn(),
  useAdminAiEvalHarnessRuns: vi.fn(),
}));

function createWrapper() {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <NextIntlClientProvider locale="fr" messages={fr}>
        {children}
      </NextIntlClientProvider>
    );
  }
  return Wrapper;
}

const emptyStats = {
  data: {
    days: 1,
    stats: {
      total_tokens: 0,
      total_cost: 0,
      average_tokens: 0,
      count: 0,
      by_type: {},
      by_model: {},
      by_workload: {},
      retention: {
        max_age_days: 7,
        max_events_per_key: 1000,
        disclaimer_fr: "",
      },
    },
    daily_summary: {},
  },
  isLoading: false,
  error: null,
  refetch: vi.fn(),
} as ReturnType<typeof useAdminAiStats>;

const emptyMetrics = {
  data: {
    days: 1,
    summary: {
      success_rate: 0,
      validation_failure_rate: 0,
      auto_correction_rate: 0,
      average_duration: 0,
      by_type: {},
      by_workload: {},
      error_types: {},
    },
  },
  isLoading: false,
  error: null,
  refetch: vi.fn(),
} as ReturnType<typeof useAdminGenerationMetrics>;

const emptyHarness = {
  data: { runs: [], limit: HARNESS_RUNS_LIMIT, disclaimer_fr: "" },
  isLoading: false,
  error: null,
  refetch: vi.fn(),
} as ReturnType<typeof useAdminAiEvalHarnessRuns>;

describe("useAdminAiMonitoringPageController", () => {
  beforeEach(() => {
    vi.mocked(useAdminAiStats).mockReturnValue(emptyStats);
    vi.mocked(useAdminGenerationMetrics).mockReturnValue(emptyMetrics);
    vi.mocked(useAdminAiEvalHarnessRuns).mockReturnValue(emptyHarness);
  });

  it("initializes days to 1 and passes it to stats and metrics hooks", () => {
    renderHook(() => useAdminAiMonitoringPageController(), { wrapper: createWrapper() });
    expect(useAdminAiStats).toHaveBeenCalledWith(1);
    expect(useAdminGenerationMetrics).toHaveBeenCalledWith(1);
  });

  it(`calls harness hook with limit ${HARNESS_RUNS_LIMIT}`, () => {
    renderHook(() => useAdminAiMonitoringPageController(), { wrapper: createWrapper() });
    expect(useAdminAiEvalHarnessRuns).toHaveBeenCalledWith(HARNESS_RUNS_LIMIT);
  });

  it("updates days when handleDaysChange is called", () => {
    const { result } = renderHook(() => useAdminAiMonitoringPageController(), {
      wrapper: createWrapper(),
    });
    act(() => {
      result.current.handleDaysChange("7");
    });
    expect(result.current.days).toBe(7);
    expect(useAdminAiStats).toHaveBeenLastCalledWith(7);
    expect(useAdminGenerationMetrics).toHaveBeenLastCalledWith(7);
  });

  it("aggregates isLoading when any hook is loading", () => {
    vi.mocked(useAdminAiStats).mockReturnValue({ ...emptyStats, isLoading: true });
    const { result } = renderHook(() => useAdminAiMonitoringPageController(), {
      wrapper: createWrapper(),
    });
    expect(result.current.isLoading).toBe(true);
  });

  it("aggregates error when any hook has an error", () => {
    const err = new Error("fail");
    vi.mocked(useAdminGenerationMetrics).mockReturnValue({ ...emptyMetrics, error: err });
    const { result } = renderHook(() => useAdminAiMonitoringPageController(), {
      wrapper: createWrapper(),
    });
    expect(result.current.error).toBe(err);
  });

  it("formatWorkloadLabel translates known workload keys and falls back to raw string", () => {
    const { result } = renderHook(() => useAdminAiMonitoringPageController(), {
      wrapper: createWrapper(),
    });
    const workloads = fr.adminPages.aiMonitoring.workloads;
    expect(result.current.formatWorkloadLabel("assistant_chat")).toBe(workloads.assistant_chat);
    expect(result.current.formatWorkloadLabel("exercises_ai")).toBe(workloads.exercises_ai);
    expect(result.current.formatWorkloadLabel("challenges_ai")).toBe(workloads.challenges_ai);
    expect(result.current.formatWorkloadLabel("unknown")).toBe(workloads.unknown);
    expect(result.current.formatWorkloadLabel("custom_runtime_key")).toBe("custom_runtime_key");
  });
});
