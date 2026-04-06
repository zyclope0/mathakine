/**
 * Characterization tests for app/badges/page.tsx.
 * FFI-L12
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import BadgesPage from "@/app/badges/page";

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, params?: Record<string, unknown>) => {
    if (params) return `${key}(${JSON.stringify(params)})`;
    return key;
  },
  NextIntlClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("canvas-confetti", () => ({ default: vi.fn() }));

const mockUseBadges = vi.fn();
const mockUseBadgesProgress = vi.fn();

vi.mock("@/hooks/useBadges", () => ({ useBadges: () => mockUseBadges() }));
vi.mock("@/hooks/useBadgesProgress", () => ({
  useBadgesProgress: () => mockUseBadgesProgress(),
}));

function makeDefaultBadgesData(overrides = {}) {
  return {
    earnedBadges: [],
    availableBadges: [],
    userStats: null,
    gamificationStats: null,
    rarityMap: {},
    pinnedBadgeIds: [],
    pinBadges: vi.fn(),
    isLoading: false,
    error: null,
    checkBadges: vi.fn(),
    isChecking: false,
    ...overrides,
  };
}

function makeDefaultProgressData(overrides = {}) {
  return {
    inProgress: [],
    isLoading: false,
    error: null,
    ...overrides,
  };
}

describe("BadgesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockUseBadges.mockReturnValue(makeDefaultBadgesData());
    mockUseBadgesProgress.mockReturnValue(makeDefaultProgressData());
  });

  it("affiche LoadingState pendant le chargement", () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ isLoading: true }));
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("loading");
  });

  it("affiche EmptyState si une erreur survient", () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ error: new Error("Connexion echouee") }));
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("error.title");
  });

  it("affiche le PageHeader avec le titre", () => {
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("title");
  });

  it("affiche BadgesHeaderStats si userStats est present", () => {
    mockUseBadges.mockReturnValue(
      makeDefaultBadgesData({
        userStats: {
          total_points: 250,
          current_level: 3,
          progression_rank: "cadet",
        },
      })
    );
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("250");
  });

  it("affiche les onglets progression et a debloquer quand des donnees existent", () => {
    const badge = {
      id: 1,
      code: "b1",
      name: "Badge Test",
      description: "",
      category: "progression",
      difficulty: "bronze",
      points_reward: 10,
      is_active: true,
      is_secret: false,
    };

    mockUseBadgesProgress.mockReturnValue(
      makeDefaultProgressData({
        inProgress: [
          { id: 1, code: "b1", name: "Badge Test", progress: 0.3, current: 3, target: 10 },
        ],
      })
    );
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ availableBadges: [badge] }));

    render(<BadgesPage />);
    expect(document.body.textContent).toContain("tabs.inProgressWithCount");
    expect(document.body.textContent).toContain("tabs.toUnlockWithCount");
  });

  it("n'affiche pas le bouton reset par defaut", () => {
    render(<BadgesPage />);
    expect(screen.queryByText("filters.reset")).toBeNull();
  });

  it("n'affiche pas les stats compactes sans userStats", () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ userStats: null }));
    render(<BadgesPage />);
    expect(document.querySelector('[aria-label="statsCompact"]')).toBeNull();
  });

  it("n'affiche pas la section derniers exploits sans badges obtenus", () => {
    render(<BadgesPage />);
    expect(screen.queryByText("lastExploits")).toBeNull();
  });

  it("n'affiche pas la section closest sans badges proches", () => {
    render(<BadgesPage />);
    expect(screen.queryByText("closestTitle")).toBeNull();
  });
});
