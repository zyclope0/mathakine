import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";

vi.mock("@/hooks/useDashboardPageController", () => ({
  useDashboardPageController: vi.fn(),
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

vi.mock("@/components/layout", () => ({
  PageLayout: ({ children }: { children: ReactNode }) => (
    <div data-testid="page-layout">{children}</div>
  ),
  PageHeader: ({
    title,
    description,
    actions,
  }: {
    title: string;
    description?: string;
    actions?: ReactNode;
  }) => (
    <header>
      <h1>{title}</h1>
      {description ? <p>{description}</p> : null}
      <div>{actions}</div>
    </header>
  ),
  PageSection: ({ children }: { children: ReactNode }) => <section>{children}</section>,
  EmptyState: ({ title, action }: { title: string; action?: ReactNode }) => (
    <div>
      <p>{title}</p>
      {action}
    </div>
  ),
}));

vi.mock("@/components/dashboard/DashboardSkeletons", () => ({
  StatsCardSkeleton: () => <div data-testid="stats-skeleton" />,
  ChartSkeleton: () => <div data-testid="chart-skeleton" />,
}));

vi.mock("@/components/dashboard/ExportButton", () => ({
  ExportButton: ({ snapshot }: { snapshot: unknown }) => (
    <div data-testid="export-button">{snapshot ? "has-snapshot" : "no-snapshot"}</div>
  ),
}));

vi.mock("@/components/dashboard/TimeRangeSelector", () => ({
  TimeRangeSelector: ({ value }: { value: string }) => <div data-testid="time-range">{value}</div>,
}));

vi.mock("@/components/dashboard/DashboardTabsNav", () => ({
  DashboardTabsNav: () => <div data-testid="dashboard-tabs-nav" />,
}));

vi.mock("@/components/dashboard/DashboardOverviewSection", () => ({
  DashboardOverviewSection: () => <div data-testid="overview-section" />,
}));

vi.mock("@/components/dashboard/DashboardRecommendationsSection", () => ({
  DashboardRecommendationsSection: () => <div data-testid="recommendations-section" />,
}));

vi.mock("@/components/dashboard/DashboardProgressSection", () => ({
  DashboardProgressSection: () => <div data-testid="progress-section" />,
}));

vi.mock("@/components/dashboard/DashboardProfileSection", () => ({
  DashboardProfileSection: () => <div data-testid="profile-section" />,
}));

import { useDashboardPageController } from "@/hooks/useDashboardPageController";
import DashboardPage from "@/app/dashboard/page";

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function buildControllerState(overrides: Record<string, unknown> = {}) {
  return {
    activeTab: "overview",
    challengesProgress: null,
    error: null,
    exportSnapshot: { generatedAt: "2026-04-08T12:00:00.000Z" },
    handleRefresh: vi.fn(),
    isLoading: false,
    isLoadingChallenges: false,
    isLoadingProgress: false,
    isRefreshing: false,
    locale: "fr",
    progressStats: null,
    refetch: vi.fn(),
    setActiveTab: vi.fn(),
    setTimeRange: vi.fn(),
    setTimelinePeriod: vi.fn(),
    stats: {
      total_exercises: 10,
      success_rate: 80,
      total_challenges: 2,
      spaced_repetition: {
        due_today: 1,
        mastered: 2,
        learning: 3,
        reviewed_today: 1,
        overdue: 0,
        success_rate: 90,
        retention_rate: 91,
        total_cards: 5,
      },
      recent_activity: [],
    },
    timeRange: "30",
    timeRangeLabel: "30 derniers jours",
    timelinePeriod: "7d",
    user: {
      id: 1,
      username: "padawan",
      role: "learner",
    },
    ...overrides,
  };
}

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders dashboard skeletons while data is loading", () => {
    vi.mocked(useDashboardPageController).mockReturnValue(
      buildControllerState({ isLoading: true, stats: null }) as unknown as ReturnType<
        typeof useDashboardPageController
      >
    );

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/bienvenue/i)).toBeDefined();
    expect(screen.getAllByTestId("stats-skeleton")).toHaveLength(3);
    expect(screen.getAllByTestId("chart-skeleton")).toHaveLength(3);
  });

  it("retries dashboard loading when the error CTA is clicked", async () => {
    const user = userEvent.setup();
    const refetch = vi.fn();

    vi.mocked(useDashboardPageController).mockReturnValue(
      buildControllerState({
        error: new Error("network"),
        refetch,
        stats: null,
      }) as unknown as ReturnType<typeof useDashboardPageController>
    );

    render(<DashboardPage />, { wrapper });

    await user.click(screen.getByRole("button", { name: fr.dashboard.error.retry }));

    expect(refetch).toHaveBeenCalledTimes(1);
  });

  it("renders the active tab section and preserves header actions", async () => {
    const user = userEvent.setup();
    const handleRefresh = vi.fn();

    vi.mocked(useDashboardPageController).mockReturnValue(
      buildControllerState({
        activeTab: "progress",
        handleRefresh,
      }) as unknown as ReturnType<typeof useDashboardPageController>
    );

    render(<DashboardPage />, { wrapper });

    expect(screen.getByTestId("dashboard-tabs-nav")).toBeDefined();
    expect(screen.getByTestId("progress-section")).toBeDefined();
    expect(screen.queryByTestId("overview-section")).toBeNull();
    expect(screen.getByTestId("export-button")).toHaveTextContent("has-snapshot");

    await user.click(screen.getByRole("button", { name: fr.dashboard.refresh }));

    expect(handleRefresh).toHaveBeenCalledTimes(1);
  });
});
