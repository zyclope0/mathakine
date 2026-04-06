/**
 * Tests de caractérisation de app/badges/page.tsx (BadgesPage).
 * FFI-L12
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// ─── Mocks ────────────────────────────────────────────────────────────────────

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

// ─── Helpers ──────────────────────────────────────────────────────────────────

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

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("BadgesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockUseBadges.mockReturnValue(makeDefaultBadgesData());
    mockUseBadgesProgress.mockReturnValue(makeDefaultProgressData());
  });

  it("affiche LoadingState pendant le chargement", async () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ isLoading: true }));
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    // La section collection affiche un LoadingState
    expect(document.body.textContent).toContain("loading");
  });

  it("affiche EmptyState si une erreur survient", async () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ error: new Error("Connexion échouée") }));
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("error.title");
  });

  it("affiche le PageHeader avec le titre", async () => {
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("title");
  });

  it("affiche BadgesHeaderStats si userStats présent", async () => {
    mockUseBadges.mockReturnValue(
      makeDefaultBadgesData({
        userStats: {
          total_points: 250,
          current_level: 3,
          progression_rank: "cadet",
        },
      })
    );
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("250");
  });

  it("affiche les onglets progression et à débloquer quand données présentes", async () => {
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
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(document.body.textContent).toContain("tabs.inProgressWithCount");
    expect(document.body.textContent).toContain("tabs.toUnlockWithCount");
  });

  it("bouton reset filtres absent par défaut (aucun filtre actif)", async () => {
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    const resetBtn = screen.queryByText("filters.reset");
    expect(resetBtn).toBeNull();
  });

  it("badgesHeaderStats absent si userStats null", async () => {
    mockUseBadges.mockReturnValue(makeDefaultBadgesData({ userStats: null }));
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    // statsCompact est le aria-label de la div stats — ne doit pas apparaître
    const statsRegion = document.querySelector('[aria-label="statsCompact"]');
    expect(statsRegion).toBeNull();
  });

  it("section derniers exploits absente si pas de badges earned", async () => {
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(screen.queryByText("lastExploits")).toBeNull();
  });

  it("section closest absente si pas de closestBadges", async () => {
    const { default: BadgesPage } = await import("@/app/badges/page");
    render(<BadgesPage />);
    expect(screen.queryByText("closestTitle")).toBeNull();
  });
});
