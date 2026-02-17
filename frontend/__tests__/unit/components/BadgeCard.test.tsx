import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BadgeCard } from "@/components/badges/BadgeCard";
import type { Badge, UserBadge } from "@/types/api";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({
    createVariants: (v: object) => v,
    createTransition: (t: object) => t,
    shouldReduceMotion: false,
  }),
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("BadgeCard", () => {
  const mockBadge: Badge & { criteria_text?: string | null } = {
    id: 1,
    code: "first_steps",
    name: "Premiers Pas",
    description: "Compléter votre premier exercice",
    category: "progression",
    difficulty: "bronze",
    points_reward: 10,
    star_wars_title: "Éveil de la Force",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
  };

  it("affiche le nom du badge", () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />, { wrapper: TestWrapper });
    expect(screen.getByText("Premiers Pas")).toBeInTheDocument();
  });

  it("affiche le titre Star Wars si disponible", () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />, { wrapper: TestWrapper });
    expect(screen.getByText("Éveil de la Force")).toBeInTheDocument();
  });

  it("affiche l'icône de verrouillage si le badge n'est pas obtenu", () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />, { wrapper: TestWrapper });
    // L'icône Lock devrait être présente (vérification via aria-hidden car c'est décoratif)
    const lockIcon = document.querySelector('[aria-hidden="true"]');
    expect(lockIcon).toBeInTheDocument();
  });

  it("affiche l'icône de succès si le badge est obtenu", () => {
    const userBadge: UserBadge = {
      ...mockBadge,
      earned_at: "2025-01-01T00:00:00Z",
    };
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />, { wrapper: TestWrapper });
    // L'icône CheckCircle devrait être présente
    const checkIcon = document.querySelector('[class*="text-green-500"]');
    expect(checkIcon).toBeInTheDocument();
  });

  it("affiche les points de récompense", () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />, { wrapper: TestWrapper });
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("pts")).toBeInTheDocument();
  });

  it("affiche la date d'obtention si le badge est obtenu", () => {
    const userBadge: UserBadge = {
      ...mockBadge,
      earned_at: "2025-01-15T00:00:00Z",
    };
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />, { wrapper: TestWrapper });
    expect(screen.getByText(/obtenu le/i)).toBeInTheDocument();
  });
});
