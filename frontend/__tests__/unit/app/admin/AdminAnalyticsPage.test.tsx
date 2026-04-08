import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import AdminAnalyticsPage from "@/app/admin/analytics/page";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";

vi.mock("@/hooks/useAdminEdTechAnalytics", () => ({
  useAdminEdTechAnalytics: vi.fn(),
}));

import { useAdminEdTechAnalytics } from "@/hooks/useAdminEdTechAnalytics";

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("AdminAnalyticsPage", () => {
  it("affiche l'erreur API quand le hook renvoie une erreur", () => {
    vi.mocked(useAdminEdTechAnalytics).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error("fail"),
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAdminEdTechAnalytics>);

    render(<AdminAnalyticsPage />, { wrapper: TestWrapper });
    expect(
      screen.getByText("Erreur de chargement. Vérifiez vos droits admin.")
    ).toBeInTheDocument();
  });

  it("affiche le chargement quand isLoading", () => {
    vi.mocked(useAdminEdTechAnalytics).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAdminEdTechAnalytics>);

    render(<AdminAnalyticsPage />, { wrapper: TestWrapper });
    expect(screen.getByText("Chargement des analytics...")).toBeInTheDocument();
  });

  it("affiche l'état vide global quand pas de données", () => {
    vi.mocked(useAdminEdTechAnalytics).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAdminEdTechAnalytics>);

    render(<AdminAnalyticsPage />, { wrapper: TestWrapper });
    expect(screen.getByText("Aucune donnée.")).toBeInTheDocument();
  });

  it("affiche le libellé 'depuis le clic Quick Start' pour la métrique temps moyen", () => {
    vi.mocked(useAdminEdTechAnalytics).mockReturnValue({
      data: {
        period: "7d",
        since: "2026-03-01T00:00:00Z",
        unique_users: 1,
        aggregates: {
          first_attempt: {
            count: 1,
            avg_time_to_first_attempt_ms: 86000,
            by_type: { exercise: 1, challenge: 0 },
          },
        },
        ctr_summary: {
          total_clicks: 1,
          guided_clicks: 1,
          guided_rate_pct: 100,
          by_type: { exercise: 1, challenge: 0 },
        },
        events: [],
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminEdTechAnalytics>);

    render(<AdminAnalyticsPage />, { wrapper: TestWrapper });

    expect(screen.getByText("depuis le clic Quick Start")).toBeInTheDocument();
    expect(screen.getByText("Temps moyen clic Quick Start → 1er attempt")).toBeInTheDocument();
  });

  it("n'affiche pas 'depuis la vue du dashboard'", () => {
    vi.mocked(useAdminEdTechAnalytics).mockReturnValue({
      data: {
        period: "7d",
        since: "2026-03-01T00:00:00Z",
        unique_users: 1,
        aggregates: {
          first_attempt: {
            count: 1,
            avg_time_to_first_attempt_ms: 86000,
            by_type: { exercise: 1, challenge: 0 },
          },
        },
        ctr_summary: {
          total_clicks: 1,
          guided_clicks: 1,
          guided_rate_pct: 100,
          by_type: { exercise: 1, challenge: 0 },
        },
        events: [],
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminEdTechAnalytics>);

    render(<AdminAnalyticsPage />, { wrapper: TestWrapper });

    expect(screen.queryByText("depuis la vue du dashboard")).not.toBeInTheDocument();
  });
});
