import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";

const mockSetTheme = vi.fn();

vi.mock("@/hooks/useAuth");
vi.mock("@/hooks/useProfile");
vi.mock("@/hooks/useUserStats");
vi.mock("@/hooks/useBadges");
vi.mock("@/lib/stores/themeStore", () => ({
  useThemeStore: () => ({ setTheme: mockSetTheme }),
}));
vi.mock("@/hooks/useChallengeTranslations", () => ({
  useAgeGroupDisplay: () => (group: string | null | undefined) => group ?? "",
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
import { useBadges } from "@/hooks/useBadges";
import { useProfile } from "@/hooks/useProfile";
import { useUserStats } from "@/hooks/useUserStats";
import ProfilePage from "@/app/profile/page";

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function buildUser(overrides: Record<string, unknown> = {}) {
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
    updateProfileAsync: vi.fn(),
    isUpdatingProfile: false,
    changePassword: vi.fn(),
    changePasswordAsync: vi.fn(),
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

describe("ProfilePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders an EmptyState when user is null", () => {
    mockHooks({ user: null as unknown as ReturnType<typeof buildUser> });

    const { container } = render(<ProfilePage />, { wrapper });

    expect(container.querySelector("input")).toBeNull();
    expect(screen.getAllByText(fr.profile.error.title).length).toBeGreaterThan(0);
  });

  it("shows the profile section by default", async () => {
    mockHooks();
    render(<ProfilePage />, { wrapper });

    await waitFor(() => {
      expect(screen.getAllByText(fr.profile.personalInfo.title).length).toBeGreaterThan(0);
    });
  });

  it("switches to the accessibility section on click", async () => {
    const user = userEvent.setup();
    mockHooks();
    render(<ProfilePage />, { wrapper });

    const accessButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent?.toLowerCase().includes("accessibilit"));

    expect(accessButton).toBeDefined();

    if (!accessButton) return;

    await user.click(accessButton);

    await waitFor(() => {
      expect(screen.getAllByText(fr.profile.accessibility.theme).length).toBeGreaterThan(0);
    });
  });

  it("switches to the statistics section on click", async () => {
    const user = userEvent.setup();
    mockHooks({ stats: { total_exercises: 10, success_rate: 75, recent_activity: [] } });
    render(<ProfilePage />, { wrapper });

    const statsButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent?.toLowerCase().includes("statistique"));

    expect(statsButton).toBeDefined();

    if (!statsButton) return;

    await user.click(statsButton);

    await waitFor(() => {
      expect(screen.queryByLabelText(/email/i)).toBeNull();
    });
  });

  it("shows skeleton cards while statistics are loading", async () => {
    const user = userEvent.setup();
    mockHooks({ isLoadingStats: true, stats: null });
    const { container } = render(<ProfilePage />, { wrapper });

    const statsButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent?.toLowerCase().includes("statistique"));

    expect(statsButton).toBeDefined();

    if (!statsButton) return;

    await user.click(statsButton);

    await waitFor(() => {
      expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
    });
  });

  it("shows an EmptyState when statistics loading fails", async () => {
    const user = userEvent.setup();
    mockHooks({ statsError: new Error("fetch error"), stats: null });
    render(<ProfilePage />, { wrapper });

    const statsButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent?.toLowerCase().includes("statistique"));

    expect(statsButton).toBeDefined();

    if (!statsButton) return;

    await user.click(statsButton);

    await waitFor(() => {
      expect(screen.getAllByText(fr.profile.error.title).length).toBeGreaterThan(0);
    });
  });

  it("shows statistics content when data is available", async () => {
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
      .find((button) => button.textContent?.toLowerCase().includes("statistique"));

    expect(statsButton).toBeDefined();

    if (!statsButton) return;

    await user.click(statsButton);

    await waitFor(() => {
      expect(screen.getByText("42")).toBeDefined();
    });
  });

  it("limits recent badges to 3 items", async () => {
    const user = userEvent.setup();
    const badges = Array.from({ length: 5 }, (_, index) => ({
      id: index + 1,
      code: `badge-${index + 1}`,
      name: `Badge ${index + 1}`,
      description: `Description ${index + 1}`,
      points: 10,
      earned_at: `2025-0${index + 1}-01T00:00:00Z`,
    }));

    mockHooks({
      earnedBadges: badges,
      stats: { total_exercises: 5, success_rate: 60, recent_activity: [] },
    });
    render(<ProfilePage />, { wrapper });

    const statsButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent?.toLowerCase().includes("statistique"));

    expect(statsButton).toBeDefined();

    if (!statsButton) return;

    await user.click(statsButton);

    await waitFor(() => {
      const badgeTitles = screen
        .getAllByRole("heading", { level: 3 })
        .filter((heading) => heading.textContent?.startsWith("Badge "));
      expect(badgeTitles.length).toBeLessThanOrEqual(3);
    });
  });
});
