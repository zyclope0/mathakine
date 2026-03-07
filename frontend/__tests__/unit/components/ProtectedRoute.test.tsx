import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/hooks/useAuth";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
    replace: vi.fn(),
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

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("affiche immédiatement le contenu si un utilisateur est déjà en cache", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        access_scope: "full_access",
        onboarding_completed_at: "2026-03-06T08:00:00Z",
      },
      isLoading: true,
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute>
        <div>Contenu protégé</div>
      </ProtectedRoute>
    );

    expect(screen.getByText("Contenu protégé")).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("redirige vers /login après le timeout de sécurité si l'auth reste indéterminée", async () => {
    vi.useFakeTimers();
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: true,
      isAuthenticated: false,
    } as unknown as ReturnType<typeof useAuth>);

    render(
      <ProtectedRoute>
        <div>Contenu protégé</div>
      </ProtectedRoute>
    );

    expect(screen.getByText("Chargement...")).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
    });

    expect(pushMock).toHaveBeenCalledWith("/login");
  });
});
