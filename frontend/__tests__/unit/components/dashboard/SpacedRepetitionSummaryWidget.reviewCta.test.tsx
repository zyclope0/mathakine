import type { ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";

const mockPush = vi.fn();
const mockFetchNextReview = vi.fn();
const mockUseNextReviewState = {
  isLoading: false,
  error: null as string | null,
};

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({
    invalidateQueries: vi.fn().mockResolvedValue(undefined),
  }),
}));

vi.mock("@/hooks/useNextReview", () => ({
  useNextReview: () => ({
    fetchNextReview: mockFetchNextReview,
    isLoading: mockUseNextReviewState.isLoading,
    error: mockUseNextReviewState.error,
    clearError: vi.fn(),
  }),
}));

import { SpacedRepetitionSummaryWidget } from "@/components/dashboard/SpacedRepetitionSummaryWidget";

function Wrapper({ children }: { children: ReactNode }) {
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

describe("SpacedRepetitionSummaryWidget — CTA Réviser maintenant", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseNextReviewState.isLoading = false;
    mockUseNextReviewState.error = null;
  });

  it("affiche le bouton lorsque des révisions sont dues", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 3,
      due_today_count: 1,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    expect(screen.getByRole("button", { name: /Réviser maintenant/i })).toBeInTheDocument();
  });

  it("affiche le bouton lorsqu’il y a des cartes en retard", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 2,
      due_today_count: 0,
      overdue_count: 1,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    expect(screen.getByRole("button", { name: /Réviser maintenant/i })).toBeInTheDocument();
  });

  it("n’affiche pas le CTA sans révision due", () => {
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 4,
      due_today_count: 0,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    expect(screen.queryByRole("button", { name: /Réviser maintenant/i })).not.toBeInTheDocument();
  });

  it("désactive le bouton pendant le chargement", () => {
    mockUseNextReviewState.isLoading = true;
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 1,
      due_today_count: 1,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    expect(screen.getByRole("button", { name: /Préparation/i })).toBeDisabled();
  });

  it("affiche une erreur locale lorsque le hook signale une erreur", () => {
    mockUseNextReviewState.error = "network";
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 1,
      due_today_count: 1,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    expect(
      screen.getByText(/Impossible de lancer la révision pour le moment/i)
    ).toBeInTheDocument();
  });

  it("navigue vers l’exercice quand l’API confirme une carte", async () => {
    const user = userEvent.setup();
    mockFetchNextReview.mockResolvedValue({
      has_due_review: true,
      summary: base,
      next_review: {
        review_item_id: 1,
        exercise_id: 99,
        due_status: "due_today" as const,
        next_review_date: "2026-03-27",
        exercise: {
          id: 99,
          title: "x",
          question: "q",
          exercise_type: "ADDITION",
          difficulty: "INITIE",
          age_group: "6-8",
          difficulty_tier: null,
          choices: [],
          image_url: null,
          audio_url: null,
        },
      },
    });
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 1,
      due_today_count: 1,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    await user.click(screen.getByRole("button", { name: /Réviser maintenant/i }));
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/exercises/99?session=spaced-review");
    });
  });

  it("affiche un message neutre si le résumé annonce des dues mais l’API n’en a pas", async () => {
    const user = userEvent.setup();
    mockFetchNextReview.mockResolvedValue({
      has_due_review: false,
      summary: base,
      next_review: null,
    });
    const s: SpacedRepetitionUserSummary = {
      ...base,
      f04_initialized: true,
      active_cards_count: 1,
      due_today_count: 1,
      overdue_count: 0,
    };
    render(<SpacedRepetitionSummaryWidget summary={s} />, { wrapper: Wrapper });
    await user.click(screen.getByRole("button", { name: /Réviser maintenant/i }));
    await waitFor(() => {
      expect(screen.getByText(/Aucune carte due/i)).toBeInTheDocument();
    });
    expect(mockPush).not.toHaveBeenCalled();
  });
});
