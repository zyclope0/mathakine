import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
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
  it("affiche le message discret si F04 non initialisé", () => {
    render(<SpacedRepetitionSummaryWidget summary={base} />, { wrapper });
    expect(screen.getByText("Révisions du jour")).toBeInTheDocument();
    expect(
      screen.getByText("Les révisions apparaîtront après quelques exercices.")
    ).toBeInTheDocument();
  });

  it("affiche aucune révision aujourd'hui quand initialisé et rien dû", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 4,
      due_today_count: 0,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper });
    expect(screen.getByText("Aucune révision prévue aujourd'hui.")).toBeInTheDocument();
    expect(screen.getByText("4 cartes suivies")).toBeInTheDocument();
  });

  it("met en avant le nombre de révisions dues aujourd'hui", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 3,
      due_today_count: 2,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper });
    expect(screen.getByText("2 révisions aujourd'hui")).toBeInTheDocument();
  });

  it("affiche le retard en secondaire", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 2,
      due_today_count: 0,
      overdue_count: 1,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper });
    expect(screen.getByText("1 carte en retard")).toBeInTheDocument();
  });

  it("affiche l'état erreur localisé", () => {
    render(<SpacedRepetitionSummaryWidget summary={base} hasError />, { wrapper });
    expect(screen.getByText("Impossible d'afficher le résumé des révisions.")).toBeInTheDocument();
  });

  it("affiche le skeleton en chargement", () => {
    const { container } = render(<SpacedRepetitionSummaryWidget summary={base} isLoading />, {
      wrapper,
    });
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });
});
