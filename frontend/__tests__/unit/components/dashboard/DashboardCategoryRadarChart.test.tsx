import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DashboardCategoryRadarPlot } from "@/components/dashboard/DashboardCategoryRadarChart";

const mockUseAccessibleAnimation = vi.fn();

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: (...args: unknown[]) => mockUseAccessibleAnimation(...args),
}));

vi.mock("recharts", () => {
  const Passthrough = ({ children }: { children?: React.ReactNode }) => <div>{children}</div>;

  return {
    ResponsiveContainer: Passthrough,
    RadarChart: ({ children }: { children?: React.ReactNode }) => <div>{children}</div>,
    PolarGrid: Passthrough,
    PolarAngleAxis: Passthrough,
    PolarRadiusAxis: Passthrough,
    Tooltip: Passthrough,
    Radar: ({ isAnimationActive }: { isAnimationActive?: boolean }) => (
      <div data-testid="radar" data-animation-active={String(Boolean(isAnimationActive))} />
    ),
  };
});

describe("DashboardCategoryRadarPlot", () => {
  it("ignore le focusMode et garde les animations actives par défaut sur le dashboard", () => {
    mockUseAccessibleAnimation.mockReturnValue({ shouldReduceMotion: false });

    render(
      <DashboardCategoryRadarPlot
        rows={[{ category: "Algèbre", accuracy: 85 }]}
        tooltipSeriesLabel="Exercices"
        ariaLabel="Radar"
      />
    );

    expect(mockUseAccessibleAnimation).toHaveBeenCalledWith({ respectFocusMode: false });
    expect(screen.getByTestId("radar")).toHaveAttribute("data-animation-active", "true");
  });

  it("désactive les animations si reduced motion est réellement actif", () => {
    mockUseAccessibleAnimation.mockReturnValue({ shouldReduceMotion: true });

    render(
      <DashboardCategoryRadarPlot
        rows={[{ category: "Algèbre", accuracy: 85 }]}
        tooltipSeriesLabel="Exercices"
        ariaLabel="Radar"
      />
    );

    expect(screen.getByTestId("radar")).toHaveAttribute("data-animation-active", "false");
  });
});
