import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { DashboardOverviewSection } from "./DashboardOverviewSection";

vi.mock("./QuickStartActions", () => ({
  QuickStartActions: () => <div data-testid="quick-start-actions" />,
}));

vi.mock("./SpacedRepetitionSummaryWidget", () => ({
  SpacedRepetitionSummaryWidget: () => <div data-testid="spaced-repetition-summary" />,
}));

vi.mock("./DailyChallengesWidget", () => ({
  DailyChallengesWidget: () => <div data-testid="daily-challenges-widget" />,
}));

vi.mock("./StreakWidget", () => ({
  StreakWidget: () => <div data-testid="streak-widget" />,
}));

describe("DashboardOverviewSection", () => {
  it("affiche l'encart beta entre quick start et les widgets", () => {
    render(
      <DashboardOverviewSection
        betaHelp={{
          title: "Nouveau dans la beta ?",
          description: "Consulte le guide rapide pour savoir quoi tester.",
          cta: "Voir le guide beta",
        }}
        isLoadingProgress={false}
        progressStats={null}
        stats={{ spaced_repetition: null } as never}
      />
    );

    expect(screen.getByTestId("quick-start-actions")).toBeInTheDocument();
    expect(screen.getByLabelText("Nouveau dans la beta ?")).toBeInTheDocument();
    expect(
      screen.getByText("Consulte le guide rapide pour savoir quoi tester.")
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /voir le guide beta/i })).toHaveAttribute(
      "href",
      "/docs"
    );
    expect(screen.getByTestId("daily-challenges-widget")).toBeInTheDocument();
    expect(screen.getByTestId("streak-widget")).toBeInTheDocument();
  });
});
