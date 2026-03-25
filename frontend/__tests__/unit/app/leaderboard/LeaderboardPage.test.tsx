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

import { useLeaderboard } from "@/hooks/useLeaderboard";

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

describe("LeaderboardPage (L2)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

    expect(items[0]?.className).toMatch(/ring-amber-500/);
    expect(items[1]?.className).toMatch(/ring-slate/);
    expect(items[2]?.className).toMatch(/ring-amber-700/);
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
});
