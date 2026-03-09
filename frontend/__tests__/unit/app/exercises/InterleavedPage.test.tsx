/**
 * Lot 3 — InterleavedPage : erreur génération initiale, 409 not_enough_variety.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import InterleavedPage from "@/app/exercises/interleaved/page";

const mockReplace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace, push: vi.fn() }),
}));

vi.mock("@/lib/api/client", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  ApiClientError: class ApiClientError extends Error {
    status: number;
    details: unknown;
    constructor(message: string, status: number, details?: unknown) {
      super(message);
      this.status = status;
      this.details = details;
    }
  },
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/components/layout", () => ({
  PageLayout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("sonner", () => ({
  toast: { info: vi.fn(), error: vi.fn() },
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("InterleavedPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it("409 not_enough_variety → redirect /exercises", async () => {
    const { api, ApiClientError } = await import("@/lib/api/client");
    vi.mocked(api.get).mockRejectedValue(
      new ApiClientError("Not enough variety", 409, { detail: { code: "not_enough_variety" } })
    );

    render(<InterleavedPage />, { wrapper: TestWrapper });

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/exercises"));
    expect(sessionStorage.getItem("interleaved_session")).toBeNull();
  });

  it("erreur génération initiale → redirect /exercises sans sessionStorage", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      plan: ["addition"],
      length: 1,
      eligible_types: ["addition"],
      session_kind: "interleaved",
      message_key: "",
    });
    vi.mocked(api.post).mockRejectedValue(new Error("Network error"));

    render(<InterleavedPage />, { wrapper: TestWrapper });

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/exercises"));
    expect(sessionStorage.getItem("interleaved_session")).toBeNull();
  });

  it("plan vide → redirect /exercises", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      plan: [],
      length: 0,
      eligible_types: [],
      session_kind: "interleaved",
      message_key: "",
    });

    render(<InterleavedPage />, { wrapper: TestWrapper });

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/exercises"));
  });

  it("succès → sessionStorage + redirect vers exercice", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      plan: ["addition", "multiplication"],
      length: 2,
      eligible_types: ["addition", "multiplication"],
      session_kind: "interleaved",
      message_key: "",
    });
    vi.mocked(api.post).mockResolvedValue({ id: 42 });

    render(<InterleavedPage />, { wrapper: TestWrapper });

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/exercises/42?session=interleaved"));
    const stored = sessionStorage.getItem("interleaved_session");
    expect(stored).not.toBeNull();
    const parsed = JSON.parse(stored!);
    expect(parsed.plan).toEqual(["addition", "multiplication"]);
    expect(parsed.analytics?.firstAttemptTracked).toBe(false);
  });
});
