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
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />, {
      wrapper: TestWrapper,
    });
    // La carte a l'aria-label "obtenu" et le CheckCircle vert est présent
    const card = screen.getByRole("article", { name: /obtenu/i });
    expect(card).toBeInTheDocument();
    const checkIcon = document.querySelector('[class*="text-green-400"]');
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
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />, {
      wrapper: TestWrapper,
    });
    const dateElements = screen.getAllByText(/obtenu le/i);
    expect(dateElements.length).toBeGreaterThanOrEqual(1);
    expect(dateElements[0]).toBeInTheDocument();
  });

  it("rend l'icône de badge HTTP comme élément décoratif (aria-hidden)", () => {
    const badgeWithUrl: Badge = {
      ...mockBadge,
      icon_url: "https://cdn.example.com/badges/first-steps.png",
    };
    render(<BadgeCard badge={badgeWithUrl} isEarned={false} />, { wrapper: TestWrapper });
    // BadgeIcon est aria-hidden : l'image est décorative, alt="" intentionnel
    // L'accessibilité est portée par l'aria-label de la carte parente
    const card = screen.getByRole("article", { name: /Premiers Pas/i });
    expect(card).toBeInTheDocument();
    // Le conteneur de l'icône est masqué des lecteurs d'écran
    const iconContainer = document.querySelector('[aria-hidden="true"]');
    expect(iconContainer).toBeInTheDocument();
  });

  it("affiche le nom du badge même si le nom est absent (fallback sur le code)", () => {
    const badgeNoName: Badge = {
      ...mockBadge,
      name: "",
    };
    render(<BadgeCard badge={badgeNoName} isEarned={false} />, { wrapper: TestWrapper });
    // Le code est affiché comme texte de secours
    expect(screen.getByText("first_steps")).toBeInTheDocument();
  });
});
