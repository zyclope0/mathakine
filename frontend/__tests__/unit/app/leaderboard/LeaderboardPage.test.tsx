import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import LeaderboardPage from "@/app/leaderboard/page";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";

vi.mock("@/hooks/useLeaderboard", () => ({
  useLeaderboard: vi.fn(),
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/hooks/useMyLeaderboardRank", () => ({
  useMyLeaderboardRank: vi.fn(),
}));

import { useAuth } from "@/hooks/useAuth";
import { useLeaderboard } from "@/hooks/useLeaderboard";
import { useMyLeaderboardRank } from "@/hooks/useMyLeaderboardRank";

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

const baseEntry = (overrides: Partial<LeaderboardEntry>): LeaderboardEntry => ({
  rank: 1,
  username: "u1",
  total_points: 100,
  current_level: 2,
  jedi_rank: "padawan",
  is_current_user: false,
  avatar_url: null,
  current_streak: 0,
  badges_count: 0,
  ...overrides,
});

const defaultAuthReturn = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  error: null,
  login: vi.fn(),
  loginAsync: vi.fn(),
  isLoggingIn: false,
  register: vi.fn(),
  registerAsync: vi.fn(),
  isRegistering: false,
  logout: vi.fn(),
  isLoggingOut: false,
  forgotPassword: vi.fn(),
  forgotPasswordAsync: vi.fn(),
  isForgotPasswordPending: false,
} as const;

const defaultMyRankReturn = {
  data: undefined,
  isLoading: false,
  isError: false,
  error: null,
  isFetching: false,
  refetch: vi.fn(),
} as const;

describe("LeaderboardPage (L2)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuth).mockReturnValue({ ...defaultAuthReturn });
    vi.mocked(useMyLeaderboardRank).mockReturnValue({
      ...defaultMyRankReturn,
    } as unknown as ReturnType<typeof useMyLeaderboardRank>);
  });

  it("affiche un CTA vers /challenges quand le classement est vide", () => {
    vi.mocked(useLeaderboard).mockReturnValue({
      leaderboard: [],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<LeaderboardPage />, { wrapper: TestWrapper });

    const cta = screen.getByRole("link", { name: /voir les défis/i });
    expect(cta).toHaveAttribute("href", "/challenges");
  });

  it("applique les surfaces podium aux trois premiers rangs", () => {
    vi.mocked(useLeaderboard).mockReturnValue({
      leaderboard: [
        baseEntry({ rank: 1, username: "first", jedi_rank: "youngling" }),
        baseEntry({ rank: 2, username: "second", jedi_rank: "knight" }),
        baseEntry({ rank: 3, username: "third", jedi_rank: "master" }),
      ],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<LeaderboardPage />, { wrapper: TestWrapper });

    const list = screen.getByRole("list", { name: /classement par points/i });
    const items = within(list).getAllByRole("listitem");
    expect(items).toHaveLength(3);

    expect(items[0]?.className).toMatch(/leaderboard-podium-surface--rank-1/);
    expect(items[1]?.className).toMatch(/leaderboard-podium-surface--rank-2/);
    expect(items[2]?.className).toMatch(/leaderboard-podium-surface--rank-3/);
  });

  it("rend sans erreur avec série et badges à zéro", () => {
    vi.mocked(useLeaderboard).mockReturnValue({
      leaderboard: [
        baseEntry({
          rank: 1,
          username: "solo",
          current_streak: 0,
          badges_count: 0,
        }),
      ],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<LeaderboardPage />, { wrapper: TestWrapper });

    expect(screen.getByText("solo")).toBeInTheDocument();
    expect(screen.queryByTitle("Série en jours")).not.toBeInTheDocument();
  });

  it("affiche le séparateur et le rang hors top quand l’API me/rank renvoie des données", () => {
    vi.mocked(useAuth).mockReturnValue({
      ...defaultAuthReturn,
      user: {
        id: 99,
        username: "hors_top",
        email: "hors_top@test.com",
        role: "apprenant",
        is_active: true,
        current_level: 5,
        jedi_rank: "padawan",
      },
      isAuthenticated: true,
    });
    vi.mocked(useLeaderboard).mockReturnValue({
      leaderboard: [
        baseEntry({ rank: 1, username: "top1", total_points: 900 }),
        baseEntry({ rank: 2, username: "top2", total_points: 800 }),
      ],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    vi.mocked(useMyLeaderboardRank).mockReturnValue({
      data: { rank: 120, total_points: 3 },
      isLoading: false,
      isError: false,
      error: null,
      isFetching: false,
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useMyLeaderboardRank>);

    render(<LeaderboardPage />, { wrapper: TestWrapper });

    expect(screen.getByText(/votre position/i)).toBeInTheDocument();
    expect(screen.getByText("hors_top")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    const footerBlock = screen.getByText(/votre position/i).closest(".border-t");
    expect(footerBlock).toBeTruthy();
    expect(within(footerBlock as HTMLElement).getByText("3")).toBeInTheDocument();
    expect(within(footerBlock as HTMLElement).getByText("pts")).toBeInTheDocument();
  });
});
