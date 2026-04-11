/**
 * Unit tests for useIrtScores (TEST-IRT-SCORES-01) — API + auth mocked; no UI.
 */

import { createElement, type ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api/client";
import type { IrtScores, IrtTypeScore } from "@/hooks/useIrtScores";
import { useIrtScores } from "@/hooks/useIrtScores";

const authMock = vi.hoisted(() => ({
  isAuthenticated: false,
  user: null as { preferred_difficulty?: string | null } | null,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: authMock.user,
    isAuthenticated: authMock.isAuthenticated,
  }),
}));

vi.mock("@/lib/api/client", () => ({
  api: {
    get: vi.fn(),
  },
}));

const mockGet = vi.mocked(api.get);

type DiagnosticStatusResponse = {
  has_completed: boolean;
  latest: {
    id: number;
    completed_at: string;
    triggered_from: string;
    questions_asked: number;
    duration_seconds: number | null;
    scores: IrtScores;
  } | null;
};

function score(partial: Partial<IrtTypeScore> & Pick<IrtTypeScore, "difficulty">): IrtTypeScore {
  return {
    level: 1,
    correct: 1,
    total: 10,
    ...partial,
  };
}

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return { Wrapper };
}

function diagnosticPayload(latest: DiagnosticStatusResponse["latest"], has_completed: boolean) {
  return { has_completed, latest } satisfies DiagnosticStatusResponse;
}

describe("useIrtScores", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authMock.isAuthenticated = false;
    authMock.user = null;
  });

  it("utilisateur non authentifié : pas d’appel GET diagnostic, irtScores null, hasCompletedDiagnostic false", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    expect(mockGet).not.toHaveBeenCalled();
    expect(result.current.irtScores).toBeNull();
    expect(result.current.hasCompletedDiagnostic).toBe(false);
  });

  it("score direct GRAND_MAITRE : resolveIsOpenAnswer et getIrtLevel alignés", async () => {
    authMock.isAuthenticated = true;
    const scores: IrtScores = {
      addition: score({ difficulty: "GRAND_MAITRE" }),
    };
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores,
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => {
      expect(result.current.irtScores).not.toBeNull();
    });
    expect(result.current.resolveIsOpenAnswer("addition")).toBe(true);
    expect(result.current.getIrtLevel("addition")).toBe("GRAND_MAITRE");
  });

  it("score direct sous seuil (CHEVALIER) : resolveIsOpenAnswer false", async () => {
    authMock.isAuthenticated = true;
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores: { addition: score({ difficulty: "CHEVALIER" }) },
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.resolveIsOpenAnswer("addition")).toBe(false);
    expect(result.current.getIrtLevel("addition")).toBe("CHEVALIER");
  });

  it("proxy mixte : minimum des quatre types de base", async () => {
    authMock.isAuthenticated = true;
    const scores: IrtScores = {
      addition: score({ difficulty: "MAITRE" }),
      soustraction: score({ difficulty: "PADAWAN" }),
      multiplication: score({ difficulty: "GRAND_MAITRE" }),
      division: score({ difficulty: "CHEVALIER" }),
    };
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores,
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.getIrtLevel("mixte")).toBe("PADAWAN");
    expect(result.current.resolveIsOpenAnswer("mixte")).toBe(false);
  });

  it("proxy fractions : moyenne plancher de multiplication + division", async () => {
    authMock.isAuthenticated = true;
    const scores: IrtScores = {
      multiplication: score({ difficulty: "MAITRE" }),
      division: score({ difficulty: "GRAND_MAITRE" }),
    };
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores,
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.getIrtLevel("fractions")).toBe("MAITRE");
    expect(result.current.resolveIsOpenAnswer("fractions")).toBe(false);
  });

  it("type non couvert (geometrie) avec diagnostic : fallback preferred_difficulty", async () => {
    authMock.isAuthenticated = true;
    authMock.user = { preferred_difficulty: "GRAND_MAITRE" };
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores: { addition: score({ difficulty: "INITIE" }) },
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.getIrtLevel("geometrie")).toBeNull();
    expect(result.current.resolveIsOpenAnswer("geometrie")).toBe(true);
  });

  it("aucun diagnostic (latest null) : fallback profil GRAND_MAITRE / adulte / CHEVALIER / null", async () => {
    authMock.isAuthenticated = true;
    const { Wrapper } = createWrapper();

    authMock.user = { preferred_difficulty: "GRAND_MAITRE" };
    mockGet.mockResolvedValueOnce(diagnosticPayload(null, false));
    const r1 = renderHook(() => useIrtScores(), { wrapper: Wrapper });
    await waitFor(() => expect(r1.result.current.irtScores).toBeNull());
    expect(r1.result.current.resolveIsOpenAnswer("addition")).toBe(true);

    authMock.user = { preferred_difficulty: "adulte" };
    mockGet.mockResolvedValueOnce(diagnosticPayload(null, false));
    const r2 = renderHook(() => useIrtScores(), { wrapper: createWrapper().Wrapper });
    await waitFor(() => expect(r2.result.current.irtScores).toBeNull());
    expect(r2.result.current.resolveIsOpenAnswer("division")).toBe(true);

    authMock.user = { preferred_difficulty: "CHEVALIER" };
    mockGet.mockResolvedValueOnce(diagnosticPayload(null, false));
    const r3 = renderHook(() => useIrtScores(), { wrapper: createWrapper().Wrapper });
    await waitFor(() => expect(r3.result.current.irtScores).toBeNull());
    expect(r3.result.current.resolveIsOpenAnswer("addition")).toBe(false);

    authMock.user = { preferred_difficulty: null };
    mockGet.mockResolvedValueOnce(diagnosticPayload(null, false));
    const r4 = renderHook(() => useIrtScores(), { wrapper: createWrapper().Wrapper });
    await waitFor(() => expect(r4.result.current.irtScores).toBeNull());
    expect(r4.result.current.resolveIsOpenAnswer("addition")).toBe(false);
  });

  it("isIrtCovered : true pour direct / mixte / fractions ; false pour geometrie, texte, divers", async () => {
    authMock.isAuthenticated = true;
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores: {},
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.isIrtCovered("addition")).toBe(true);
    expect(result.current.isIrtCovered("MiXtE")).toBe(true);
    expect(result.current.isIrtCovered("fractions")).toBe(true);
    expect(result.current.isIrtCovered("geometrie")).toBe(false);
    expect(result.current.isIrtCovered("texte")).toBe(false);
    expect(result.current.isIrtCovered("divers")).toBe(false);
  });

  it("normalisation exerciseType et difficulté inconnue : pas de crash, fallback profil", async () => {
    authMock.isAuthenticated = true;
    authMock.user = { preferred_difficulty: "PADAWAN" };
    const scores: IrtScores = {
      addition: score({ difficulty: "NOT_A_REAL_LEVEL" }),
    };
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores,
        },
        true
      )
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useIrtScores(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.irtScores).not.toBeNull());
    expect(result.current.getIrtLevel("AdDiTiOn")).toBeNull();
    expect(result.current.resolveIsOpenAnswer("AdDiTiOn")).toBe(false);
  });

  it("hasCompletedDiagnostic reflète data.has_completed", async () => {
    authMock.isAuthenticated = true;
    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 1,
          completed_at: "2026-01-01T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores: { addition: score({ difficulty: "INITIE" }) },
        },
        false
      )
    );
    const { Wrapper } = createWrapper();
    const { result: rFalse } = renderHook(() => useIrtScores(), { wrapper: Wrapper });
    await waitFor(() => expect(rFalse.current.irtScores).not.toBeNull());
    expect(rFalse.current.hasCompletedDiagnostic).toBe(false);

    mockGet.mockResolvedValueOnce(
      diagnosticPayload(
        {
          id: 2,
          completed_at: "2026-01-02T00:00:00Z",
          triggered_from: "onboarding",
          questions_asked: 5,
          duration_seconds: 30,
          scores: { addition: score({ difficulty: "INITIE" }) },
        },
        true
      )
    );
    const w2 = createWrapper();
    const { result: rTrue } = renderHook(() => useIrtScores(), { wrapper: w2.Wrapper });
    await waitFor(() => expect(rTrue.current.hasCompletedDiagnostic).toBe(true));
  });
});
