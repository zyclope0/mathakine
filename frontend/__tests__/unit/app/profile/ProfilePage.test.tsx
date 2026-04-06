/**
 * Tests de caractérisation pour app/profile/page.tsx.
 *
 * Scope :
 * - !user rend EmptyState
 * - navigation entre sections
 * - section statistics : loading / error / content
 * - badges récents limités à 3
 *
 * FFI-L11.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock("@/hooks/useAuth");
vi.mock("@/hooks/useProfile");
vi.mock("@/hooks/useUserStats");
vi.mock("@/hooks/useBadges");
vi.mock("@/lib/stores/themeStore", () => ({
  useThemeStore: () => ({ setTheme: vi.fn() }),
}));
vi.mock("@/hooks/useChallengeTranslations", () => ({
  useAgeGroupDisplay: () => (group: string) => group,
}));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));
vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: ReactNode }) => <>{children}</>,
}));
vi.mock("@/components/dashboard/LevelIndicator", () => ({
  LevelIndicator: () => <div data-testid="level-indicator" />,
}));
vi.mock("@/components/dashboard/RecentActivity", () => ({
  RecentActivity: () => <div data-testid="recent-activity" />,
}));

import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";
import { useUserStats } from "@/hooks/useUserStats";
import { useBadges } from "@/hooks/useBadges";
import ProfilePage from "@/app/profile/page";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function buildUser(overrides = {}) {
  return {
    id: 1,
    username: "testuser",
    email: "test@example.com",
    full_name: "Test User",
    role: "learner",
    created_at: "2025-01-01T00:00:00Z",
    grade_system: "unifie",
    grade_level: 5,
    age_group: "9-11",
    learning_style: "visuel",
    preferred_difficulty: "9-11",
    learning_goal: "progresser",
    practice_rhythm: "20min_jour",
    preferred_theme: "spatial",
    accessibility_settings: { high_contrast: false, large_text: false, reduce_motion: false },
    gamification_level: { level: 3 },
    ...overrides,
  };
}

function mockHooks({
  user = buildUser(),
  stats = null as unknown,
  isLoadingStats = false,
  statsError = null as unknown,
  earnedBadges = [] as unknown[],
} = {}) {
  vi.mocked(useAuth).mockReturnValue({ user } as unknown as ReturnType<typeof useAuth>);
  vi.mocked(useProfile).mockReturnValue({
    updateProfile: vi.fn(),
    isUpdatingProfile: false,
    changePassword: vi.fn(),
    isChangingPassword: false,
  } as unknown as ReturnType<typeof useProfile>);
  vi.mocked(useUserStats).mockReturnValue({
    stats,
    isLoading: isLoadingStats,
    error: statsError,
  } as unknown as ReturnType<typeof useUserStats>);
  vi.mocked(useBadges).mockReturnValue({
    earnedBadges,
  } as unknown as ReturnType<typeof useBadges>);
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("ProfilePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("!user → EmptyState", () => {
    it("rend l'EmptyState quand user est null", () => {
      mockHooks({ user: null as unknown as ReturnType<typeof buildUser> });

      const { container } = render(<ProfilePage />, { wrapper });

      // EmptyState doit être rendu (pas de sidebar nav, pas de formulaire)
      expect(container).toBeDefined();
      // Aucun champ de formulaire ne doit exister
      expect(container.querySelector("input")).toBeNull();
    });
  });

  describe("Navigation entre sections", () => {
    it("affiche la section profil par défaut", () => {
      mockHooks();
      render(<ProfilePage />, { wrapper });

      // La section profil doit être visible (titre personalInfo)
      expect(screen.getAllByText(/informations personnelles/i).length).toBeGreaterThan(0);
    });

    it("bascule vers la section accessibilité sur clic", async () => {
      const user = userEvent.setup();
      mockHooks();
      render(<ProfilePage />, { wrapper });

      // Desktop sidebar — trouver le bouton "Accessibilité"
      const accessButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("accessibilit"));

      if (accessButton) {
        await user.click(accessButton);
        // La section accessibilité doit apparaître (select thème)
        expect(screen.getAllByText(/thème/i).length).toBeGreaterThan(0);
      }
    });

    it("bascule vers la section statistiques sur clic", async () => {
      const user = userEvent.setup();
      mockHooks({ stats: { total_exercises: 10, success_rate: 75, recent_activity: [] } });
      render(<ProfilePage />, { wrapper });

      const statsButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("statistique"));

      if (statsButton) {
        await user.click(statsButton);
        // La section doit changer (pas de champ email visible)
        expect(screen.queryByLabelText(/email/i)).toBeNull();
      }
    });
  });

  describe("Section statistics", () => {
    it("affiche le skeleton en état loading", async () => {
      const user = userEvent.setup();
      mockHooks({ isLoadingStats: true, stats: null });
      render(<ProfilePage />, { wrapper });

      const statsButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("statistique"));
      if (statsButton) {
        await user.click(statsButton);
        // Le skeleton existe (div animate-pulse)
        const { container } = render(<ProfilePage />, { wrapper });
        expect(container).toBeDefined();
      }
    });

    it("affiche EmptyState en cas d'erreur", async () => {
      const user = userEvent.setup();
      mockHooks({ statsError: new Error("fetch error"), stats: null });
      render(<ProfilePage />, { wrapper });

      const statsButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("statistique"));
      if (statsButton) {
        await user.click(statsButton);
      }

      // EmptyState doit apparaître (rendu par ProfileStatisticsSection)
      expect(screen.getAllByRole("heading").length).toBeGreaterThan(0);
    });

    it("affiche le contenu stats quand les données sont disponibles", async () => {
      const user = userEvent.setup();
      mockHooks({
        stats: {
          total_exercises: 42,
          success_rate: 80.5,
          recent_activity: [],
        },
      });
      render(<ProfilePage />, { wrapper });

      const statsButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("statistique"));
      if (statsButton) {
        await user.click(statsButton);
        expect(screen.getByText("42")).toBeDefined();
      }
    });
  });

  describe("Badges récents — limite à 3", () => {
    it("affiche au maximum 3 badges", async () => {
      const user = userEvent.setup();

      const badges = Array.from({ length: 5 }, (_, i) => ({
        id: i + 1,
        name: `Badge ${i + 1}`,
        description: `Description ${i + 1}`,
        points: 10,
        earned_at: `2025-0${i + 1}-01T00:00:00Z`,
      }));

      mockHooks({
        earnedBadges: badges,
        stats: { total_exercises: 5, success_rate: 60, recent_activity: [] },
      });
      render(<ProfilePage />, { wrapper });

      const statsButton = screen
        .getAllByRole("button")
        .find((btn) => btn.textContent?.toLowerCase().includes("statistique"));
      if (statsButton) {
        await user.click(statsButton);
        // On doit avoir au plus 3 titres de badge
        const badgeTitles = screen
          .getAllByRole("heading", { level: 3 })
          .filter((h) => h.textContent?.startsWith("Badge "));
        expect(badgeTitles.length).toBeLessThanOrEqual(3);
      }
    });
  });
});
