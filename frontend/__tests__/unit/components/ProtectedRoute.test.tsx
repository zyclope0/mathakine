"use client";

import { act, render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fr from "@/messages/fr.json";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";

const replaceMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: replaceMock,
    prefetch: vi.fn(),
    back: vi.fn(),
    pathname: "/",
    query: {},
    asPath: "/",
  }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("affiche immediatement le contenu si un utilisateur est deja en cache", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        role: "enseignant",
        access_scope: "full_access",
        onboarding_completed_at: "2026-03-06T08:00:00Z",
      },
      isLoading: true,
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute>
        <div>Contenu protege</div>
      </ProtectedRoute>,
      { wrapper: TestWrapper }
    );

    expect(screen.getByText("Contenu protege")).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("redirige vers /login apres le timeout de securite si l'auth reste indeterminee", async () => {
    vi.useFakeTimers();
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: true,
      isAuthenticated: false,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute>
        <div>Contenu protege</div>
      </ProtectedRoute>,
      { wrapper: TestWrapper }
    );

    expect(screen.getAllByText("Chargement...")).toHaveLength(2);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
    });

    expect(replaceMock).toHaveBeenCalledWith("/login");
  });

  it("redirige un apprenant vers /home-learner quand le dashboard adulte lui est interdit", async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 42,
        role: "apprenant",
        access_scope: "full_access",
        onboarding_completed_at: "2026-03-06T08:00:00Z",
      },
      isLoading: false,
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute allowedRoles={["enseignant", "moderateur", "admin"]}>
        <div>Dashboard adulte</div>
      </ProtectedRoute>,
      { wrapper: TestWrapper }
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/home-learner");
    });
    expect(screen.queryByText("Dashboard adulte")).not.toBeInTheDocument();
  });

  it("laisse passer un apprenant sur une surface apprenante autorisee", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 7,
        role: "apprenant",
        access_scope: "full_access",
        onboarding_completed_at: "2026-03-06T08:00:00Z",
      },
      isLoading: false,
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute allowedRoles={["apprenant"]} redirectAuthenticatedTo="/dashboard">
        <div>Mon espace apprenant</div>
      </ProtectedRoute>,
      { wrapper: TestWrapper }
    );

    expect(screen.getByText("Mon espace apprenant")).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("redirige un role adulte vers /dashboard sur /home-learner avant l'onboarding", async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 11,
        role: "enseignant",
        access_scope: "full",
        onboarding_completed_at: null,
      },
      isLoading: false,
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute
        requireOnboardingCompleted
        allowedRoles={["apprenant"]}
        prioritizeRoleRedirect
        redirectAuthenticatedTo="/dashboard"
      >
        <div>Home learner</div>
      </ProtectedRoute>,
      { wrapper: TestWrapper }
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/dashboard");
    });
    expect(screen.queryByText("Home learner")).not.toBeInTheDocument();
  });
});
