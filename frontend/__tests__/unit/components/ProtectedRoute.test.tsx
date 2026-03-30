"use client";

import { act, render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fr from "@/messages/fr.json";
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
    expect(pushMock).not.toHaveBeenCalled();
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

    expect(pushMock).toHaveBeenCalledWith("/login");
  });
});
