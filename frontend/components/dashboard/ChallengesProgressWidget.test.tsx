import { describe, it, expect, vi, beforeEach } from "vitest";
import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { ChallengesProgressWidget } from "./ChallengesProgressWidget";
import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import fr from "@/messages/fr.json";

vi.mock("@/hooks/useChallengesProgress", () => ({
  useChallengesDetailedProgress: vi.fn(),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function TestWrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </NextIntlClientProvider>
  );
}

const sampleItem = {
  id: 1,
  user_id: 1,
  challenge_type: "sequence",
  total_attempts: 4,
  correct_attempts: 3,
  completion_rate: 75,
  mastery_level: "apprentice",
  last_attempted_at: null,
};

describe("ChallengesProgressWidget", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    const { useChallengesDetailedProgress } = await import("@/hooks/useChallengesProgress");
    vi.mocked(useChallengesDetailedProgress).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof useChallengesDetailedProgress>);
  });

  it("sans breakdown : affiche les KPI sans liste par type", async () => {
    const { useChallengesDetailedProgress } = await import("@/hooks/useChallengesProgress");
    vi.mocked(useChallengesDetailedProgress).mockReturnValue({
      data: { items: [] },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof useChallengesDetailedProgress>);

    render(
      <ChallengesProgressWidget
        completedChallenges={2}
        totalChallenges={10}
        successRate={0.5}
        averageTime={30}
        isLoading={false}
      />,
      { wrapper: TestWrapper }
    );

    expect(screen.getByText(/2.*\/.*10/)).toBeInTheDocument();
    expect(screen.queryByText(/Par type de défi/i)).not.toBeInTheDocument();
  });

  it("avec items detailed-progress : affiche maîtrise, taux 0–100 et tentatives", async () => {
    const { useChallengesDetailedProgress } = await import("@/hooks/useChallengesProgress");
    vi.mocked(useChallengesDetailedProgress).mockReturnValue({
      data: { items: [sampleItem] },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof useChallengesDetailedProgress>);

    render(
      <ChallengesProgressWidget
        completedChallenges={2}
        totalChallenges={10}
        successRate={0.5}
        averageTime={30}
        isLoading={false}
      />,
      { wrapper: TestWrapper }
    );

    expect(screen.getByText(/Par type de défi/i)).toBeInTheDocument();
    expect(screen.getByText("Apprenti")).toBeInTheDocument();
    expect(screen.getByText("75%")).toBeInTheDocument();
    expect(screen.getByText(/3\/4/)).toBeInTheDocument();
  });

  it("0 défi complété mais tentatives par type : pas de message noChallengesYet contradictoire", async () => {
    const { useChallengesDetailedProgress } = await import("@/hooks/useChallengesProgress");
    vi.mocked(useChallengesDetailedProgress).mockReturnValue({
      data: { items: [sampleItem] },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof useChallengesDetailedProgress>);

    render(
      <ChallengesProgressWidget
        completedChallenges={0}
        totalChallenges={10}
        successRate={0}
        averageTime={0}
        isLoading={false}
      />,
      { wrapper: TestWrapper }
    );

    expect(screen.getByText(/Par type de défi/i)).toBeInTheDocument();
    expect(screen.queryByText(/Commence par relever ton premier défi/i)).not.toBeInTheDocument();
  });
});
