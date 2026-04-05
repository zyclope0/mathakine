import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NextIntlClientProvider } from "next-intl";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";
import fr from "@/messages/fr.json";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/hooks/useNextReview", () => ({
  useNextReview: () => ({
    fetchNextReview: vi.fn(),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  }),
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={client}>
      <NextIntlClientProvider locale="fr" messages={fr}>
        {children}
      </NextIntlClientProvider>
    </QueryClientProvider>
  );
}

const base: SpacedRepetitionUserSummary = {
  f04_initialized: false,
  active_cards_count: 0,
  due_today_count: 0,
  overdue_count: 0,
  next_review_date: null,
};

describe("SpacedRepetitionSummaryWidget", () => {
  it("affiche le message discret si F04 non initialise", () => {
    render(<SpacedRepetitionSummaryWidget summary={base} />, { wrapper });
    expect(screen.getByText("Révisions du jour")).toBeInTheDocument();
    expect(
      screen.getByText("Tes révisions apparaîtront ici après quelques exercices.")
    ).toBeInTheDocument();
  });

  it("affiche aucune revision aujourd'hui quand initialise et rien du", () => {
    const summary: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 4,
      due_today_count: 0,
      overdue_count: 0,
    };

    render(<SpacedRepetitionSummaryWidget summary={summary} />, { wrapper });

    expect(
      screen.getByText("Tout est à jour ! Aucune révision prévue aujourd'hui.")
    ).toBeInTheDocument();
    expect(screen.getByText("4 exercices dans le suivi")).toBeInTheDocument();
  });

  it("met en avant le nombre de revisions dues aujourd'hui", () => {
    const summary: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 3,
      due_today_count: 2,
      overdue_count: 0,
    };

    render(<SpacedRepetitionSummaryWidget summary={summary} />, { wrapper });
    expect(screen.getByText("2 exercices à réviser aujourd'hui")).toBeInTheDocument();
  });

  it("affiche le retard en secondaire", () => {
    const summary: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 2,
      due_today_count: 0,
      overdue_count: 1,
    };

    render(<SpacedRepetitionSummaryWidget summary={summary} />, { wrapper });
    expect(screen.getByText("1 en retard")).toBeInTheDocument();
  });

  it("affiche l'etat erreur localise", () => {
    render(<SpacedRepetitionSummaryWidget summary={base} hasError />, { wrapper });
    expect(
      screen.getByText("Impossible d'afficher tes révisions pour le moment.")
    ).toBeInTheDocument();
  });

  it("affiche le skeleton en chargement", () => {
    const { container } = render(<SpacedRepetitionSummaryWidget summary={base} isLoading />, {
      wrapper,
    });
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });
});
