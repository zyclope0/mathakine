import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import AdminPage from "./page";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </NextIntlClientProvider>
  );
}

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/hooks/useAdminOverview", () => ({
  useAdminOverview: vi.fn(),
}));

vi.mock("@/hooks/useAdminReports", () => ({
  useAdminReports: vi.fn(),
}));

vi.mock("@/lib/api/client", () => ({
  api: { downloadCsv: vi.fn() },
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/components/admin/AdminAcademyStatsSection", () => ({
  AdminAcademyStatsSection: () => <div data-testid="academy-stats-stub" />,
}));

import { useAdminOverview } from "@/hooks/useAdminOverview";
import { useAdminReports } from "@/hooks/useAdminReports";

describe("AdminPage (overview)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAdminReports).mockReturnValue({
      reports: null,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminReports>);
  });

  it("shows overview error message when useAdminOverview errors", () => {
    vi.mocked(useAdminOverview).mockReturnValue({
      overview: { total_users: 0, total_exercises: 0, total_challenges: 0, total_attempts: 0 },
      isLoading: false,
      error: new Error("boom"),
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAdminOverview>);

    render(<AdminPage />, { wrapper: TestWrapper });
    expect(
      screen.getByText("Erreur de chargement. Droits insuffisants ou API indisponible.")
    ).toBeInTheDocument();
  });

  it("shows loading state while overview loads", () => {
    vi.mocked(useAdminOverview).mockReturnValue({
      overview: { total_users: 0, total_exercises: 0, total_challenges: 0, total_attempts: 0 },
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminOverview>);

    render(<AdminPage />, { wrapper: TestWrapper });
    expect(screen.getAllByText("Chargement...").length).toBeGreaterThanOrEqual(1);
  });

  it("shows KPI grid when overview succeeds", () => {
    vi.mocked(useAdminOverview).mockReturnValue({
      overview: {
        total_users: 10,
        total_exercises: 20,
        total_challenges: 30,
        total_attempts: 40,
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as ReturnType<typeof useAdminOverview>);

    render(<AdminPage />, { wrapper: TestWrapper });
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Utilisateurs/i })).toHaveAttribute(
      "href",
      "/admin/users"
    );
  });
});
