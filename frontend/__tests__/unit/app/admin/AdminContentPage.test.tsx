import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const mockSearchGet = vi.fn();

vi.mock("next/navigation", () => ({
  useSearchParams: () => ({
    get: (k: string) => mockSearchGet(k),
  }),
}));

const mockUseAdminExercises = vi.fn();
const mockUseAdminChallenges = vi.fn();
const mockUseAdminBadges = vi.fn();

vi.mock("@/hooks/useAdminExercises", () => ({
  useAdminExercises: (...args: unknown[]) => mockUseAdminExercises(...args),
}));
vi.mock("@/hooks/useAdminChallenges", () => ({
  useAdminChallenges: (...args: unknown[]) => mockUseAdminChallenges(...args),
}));
vi.mock("@/hooks/useAdminBadges", () => ({
  useAdminBadges: () => mockUseAdminBadges(),
}));

vi.mock("@/components/admin/ExerciseEditModal", () => ({
  ExerciseEditModal: (p: { exerciseId: number | null; open: boolean }) =>
    p.open ? (
      <div data-testid="exercise-edit-modal" data-exercise-id={String(p.exerciseId ?? "")} />
    ) : null,
}));

import AdminContentPage from "@/app/admin/content/page";

const defaultExercise = {
  id: 1,
  title: "Exercice Alpha",
  exercise_type: "ADDITION",
  difficulty: "PADAWAN",
  age_group: "9-11",
  is_archived: false,
  attempt_count: 0,
  success_rate: 0,
  created_at: "2024-01-01T00:00:00Z",
};

function exerciseHookReturn() {
  return {
    exercises: [defaultExercise],
    total: 1,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    updateArchived: vi.fn(),
    isUpdating: false,
  };
}

function challengeHookReturn() {
  return {
    challenges: [
      {
        id: 2,
        title: "Défi Beta",
        challenge_type: "logique",
        age_group: "9-11",
        is_archived: false,
        attempt_count: 0,
        success_rate: 0,
        created_at: "2024-01-01T00:00:00Z",
      },
    ],
    total: 1,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    updateArchived: vi.fn(),
    isUpdating: false,
  };
}

function badgeHookReturn() {
  return {
    badges: [
      {
        id: 3,
        code: "b1",
        name: "Badge Gamma",
        description: "",
        icon_url: "",
        category: "skill",
        difficulty: "bronze",
        points_reward: 10,
        is_secret: false,
        requirements: null,
        star_wars_title: "",
        is_active: true,
        created_at: null,
        _user_count: 0,
      },
    ],
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    create: vi.fn(),
    isCreating: false,
    update: vi.fn(),
    isUpdating: false,
    remove: vi.fn(),
    isDeleting: false,
  };
}

function renderPage() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={qc}>
      <AdminContentPage />
    </QueryClientProvider>
  );
}

describe("AdminContentPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSearchGet.mockImplementation((k) => new URLSearchParams("").get(k));
    mockUseAdminExercises.mockReturnValue(exerciseHookReturn());
    mockUseAdminChallenges.mockReturnValue(challengeHookReturn());
    mockUseAdminBadges.mockReturnValue(badgeHookReturn());
  });

  it("affiche la liste exercices sur l’onglet par défaut", () => {
    renderPage();
    expect(screen.getByText("Créer un exercice")).toBeInTheDocument();
    expect(screen.getByText("Exercice Alpha")).toBeInTheDocument();
    expect(screen.getByText("Niveau 2")).toBeInTheDocument();
  });

  it("affiche le palier F42 quand difficulty_tier est présent sur la liste", () => {
    mockUseAdminExercises.mockReturnValue({
      ...exerciseHookReturn(),
      exercises: [
        {
          ...defaultExercise,
          difficulty_tier: 4,
        },
      ],
    });
    renderPage();
    expect(screen.getByText("Palier 4")).toBeInTheDocument();
  });

  it("ouvre l’onglet défis depuis le query param tab=challenges", () => {
    mockSearchGet.mockImplementation((k) => new URLSearchParams("tab=challenges").get(k));
    renderPage();
    expect(screen.getByText("Créer un défi")).toBeInTheDocument();
    expect(screen.getByText("Défi Beta")).toBeInTheDocument();
  });

  it("ouvre l’onglet badges depuis tab=badges", () => {
    mockSearchGet.mockImplementation((k) => new URLSearchParams("tab=badges").get(k));
    renderPage();
    expect(screen.getByText("Créer un badge")).toBeInTheDocument();
    expect(screen.getByText("Badge Gamma")).toBeInTheDocument();
  });

  it("ouvre la modale exercice depuis edit= sur l’onglet exercices", () => {
    mockSearchGet.mockImplementation((k) => new URLSearchParams("tab=exercises&edit=42").get(k));
    renderPage();
    const el = screen.getByTestId("exercise-edit-modal");
    expect(el).toBeInTheDocument();
    expect(el).toHaveAttribute("data-exercise-id", "42");
  });
});
