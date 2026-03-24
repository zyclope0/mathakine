import type { ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { Recommendations } from "@/components/dashboard/Recommendations";
import type { Recommendation } from "@/hooks/useRecommendations";

vi.mock("next/link", () => ({
  default: function MockLink({
    children,
    href,
    ...rest
  }: {
    children: ReactNode;
    href: string;
    className?: string;
    "aria-label"?: string;
    onClick?: () => void;
  }) {
    return (
      <a href={href} {...rest}>
        {children}
      </a>
    );
  },
}));

vi.mock("@/hooks/useRecommendations", () => ({
  useRecommendations: vi.fn(),
  formatRecommendationReasonDisplay: () => "Raison de test",
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useExerciseTranslations: () => ({
    getTypeDisplay: (type: string) => type,
    getAgeDisplay: () => "8-10",
  }),
}));

import { useRecommendations } from "@/hooks/useRecommendations";

function buildRecommendations(count: number): Recommendation[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    exercise_type: "geometry",
    difficulty: "padawan",
    reason: "r",
    exercise_title: `Reco ${i + 1}`,
    exercise_id: 100 + i,
  }));
}

function renderWithFr() {
  return render(
    <NextIntlClientProvider locale="fr" messages={fr}>
      <Recommendations />
    </NextIntlClientProvider>
  );
}

describe("Recommendations", () => {
  beforeEach(() => {
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: buildRecommendations(7),
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen: vi.fn(),
      isRecordingOpen: false,
    });
  });

  it("n’affiche que 6 cartes tant que la liste dépasse le seuil et show more n’a pas été activé", () => {
    renderWithFr();

    expect(screen.getAllByRole("article")).toHaveLength(6);
    expect(screen.queryByText("Reco 7")).not.toBeInTheDocument();
  });

  it("affiche toutes les cartes après Voir plus puis revient à 6 après Voir moins", async () => {
    const user = userEvent.setup();
    renderWithFr();

    await user.click(screen.getByRole("button", { name: /Voir plus/i }));
    expect(screen.getAllByRole("article")).toHaveLength(7);
    expect(screen.getByText("Reco 7")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Voir moins/i }));
    expect(screen.getAllByRole("article")).toHaveLength(6);
    expect(screen.queryByText("Reco 7")).not.toBeInTheDocument();
  });
});
