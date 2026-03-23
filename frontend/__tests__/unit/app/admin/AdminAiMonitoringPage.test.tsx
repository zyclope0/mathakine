import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AdminAiMonitoringPage from "@/app/admin/ai-monitoring/page";

import {
  useAdminAiEvalHarnessRuns,
  useAdminAiStats,
  useAdminGenerationMetrics,
} from "@/hooks/useAdminAiStats";

vi.mock("@/components/layout", () => ({
  PageHeader: ({ title, description }: { title: string; description: string }) => (
    <div>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  ),
  PageSection: ({ children }: { children: React.ReactNode }) => <section>{children}</section>,
  LoadingState: ({ message }: { message: string }) => <div>{message}</div>,
}));

vi.mock("@/components/ui/card", () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardTitle: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/components/ui/select", () => ({
  Select: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SelectContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SelectItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SelectTrigger: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SelectValue: () => <div />,
}));

vi.mock("@/hooks/useAdminAiStats", () => ({
  useAdminAiStats: vi.fn(),
  useAdminGenerationMetrics: vi.fn(),
  useAdminAiEvalHarnessRuns: vi.fn(),
}));

describe("AdminAiMonitoringPage", () => {
  it("affiche les sections workload et erreurs quand les metriques existent", () => {
    vi.mocked(useAdminAiStats).mockReturnValue({
      data: {
        days: 7,
        stats: {
          total_tokens: 1000,
          total_cost: 0.5,
          average_tokens: 250,
          count: 4,
          by_type: {
            "assistant_chat:simple": {
              total_tokens: 100,
              total_cost: 0.01,
              count: 1,
              average_tokens: 100,
            },
          },
          by_model: {
            "gpt-5-mini": { total_tokens: 100, total_cost: 0.01, count: 1 },
          },
          by_workload: {
            assistant_chat: {
              total_tokens: 100,
              total_cost: 0.01,
              count: 1,
              average_tokens: 100,
            },
          },
        },
        daily_summary: {},
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminAiStats>);

    vi.mocked(useAdminGenerationMetrics).mockReturnValue({
      data: {
        days: 7,
        summary: {
          success_rate: 75,
          validation_failure_rate: 25,
          auto_correction_rate: 10,
          average_duration: 1.5,
          by_type: {
            "assistant_chat:simple": {
              success_rate: 50,
              validation_failure_rate: 50,
              auto_correction_rate: 0,
              average_duration: 1.2,
              total_generations: 2,
            },
          },
          by_workload: {
            assistant_chat: {
              success_rate: 50,
              validation_failure_rate: 50,
              auto_correction_rate: 0,
              average_duration: 1.2,
              total_generations: 2,
            },
          },
          error_types: { RateLimitError: 1 },
        },
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminGenerationMetrics>);

    vi.mocked(useAdminAiEvalHarnessRuns).mockReturnValue({
      data: {
        runs: [],
        limit: 25,
        disclaimer_fr: "Lecture seule — runs persistés.",
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminAiEvalHarnessRuns>);

    render(<AdminAiMonitoringPage />);

    expect(screen.getAllByText(/Assistant chat/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Erreurs observees")).toBeInTheDocument();
    expect(screen.getByText("RateLimitError")).toBeInTheDocument();
  });
});
