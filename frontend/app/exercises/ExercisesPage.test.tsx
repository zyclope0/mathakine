/**
 * Smoke tests for app/exercises/page.tsx (ARCH-EXERCISES-01).
 */

import type { ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ExercisesPage from "./page";
import { useContentListPageController } from "@/hooks/useContentListPageController";
import { useExercises } from "@/hooks/useExercises";
import { useCompletedExercises } from "@/hooks/useCompletedItems";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import fr from "@/messages/fr.json";
import { CONTENT_LIST_ORDER } from "@/lib/constants/contentListOrder";
import type { Exercise } from "@/types/api";

vi.mock("next/dynamic", () => ({
  default: () => () => null,
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

vi.mock("@/hooks/useContentListPageController", () => ({
  useContentListPageController: vi.fn(),
}));

vi.mock("@/hooks/useExercises", () => ({
  useExercises: vi.fn(),
}));

vi.mock("@/hooks/useCompletedItems", () => ({
  useCompletedExercises: vi.fn(),
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useExerciseTranslations: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useSearchParams: () => ({ get: () => null, toString: () => "" }),
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
}));

const mockExercise: Exercise = {
  id: 1,
  title: "Test exercise",
  question: "2+2?",
  correct_answer: "4",
  exercise_type: "addition",
  age_group: "6-8",
  difficulty: "easy",
  created_at: "",
  updated_at: "",
};

function makeController(overrides: Record<string, unknown> = {}) {
  return {
    typeFilter: "all",
    setTypeFilter: vi.fn(),
    ageFilter: "all",
    setAgeFilter: vi.fn(),
    searchQuery: "",
    setSearchQuery: vi.fn(),
    filtersPanelOpen: false,
    setFiltersPanelOpen: vi.fn(),
    hideCompleted: false,
    setHideCompleted: vi.fn(),
    selectedItemId: null,
    isModalOpen: false,
    currentPage: 1,
    setCurrentPage: vi.fn(),
    viewMode: "grid" as const,
    setViewMode: vi.fn(),
    handleFilterChange: vi.fn(),
    handlePageChange: vi.fn(),
    orderFilter: CONTENT_LIST_ORDER.RANDOM,
    handleOrderChange: vi.fn(),
    resetOrderPreference: vi.fn(),
    hasActiveFilters: false,
    advancedActiveCount: 0,
    clearFilters: vi.fn(),
    clearTypeFilter: vi.fn(),
    clearAgeFilter: vi.fn(),
    openItem: vi.fn(),
    closeModal: vi.fn(),
    handleModalOpenChange: vi.fn(),
    ...overrides,
  };
}

function TestWrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={client}>
      <NextIntlClientProvider locale="fr" messages={fr}>
        {children}
      </NextIntlClientProvider>
    </QueryClientProvider>
  );
}

describe("ExercisesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useContentListPageController).mockReturnValue(
      makeController() as unknown as ReturnType<typeof useContentListPageController>
    );
    vi.mocked(useExerciseTranslations).mockReturnValue({
      getTypeDisplay: (x: string | null | undefined) => x ?? "",
      getAgeDisplay: (x: string | null | undefined) => x ?? "",
    });
    vi.mocked(useCompletedExercises).mockReturnValue({
      isCompleted: () => false,
      completedIds: [],
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useCompletedExercises>);
  });

  it("affiche le titre de la page quand la liste est chargée", () => {
    vi.mocked(useExercises).mockReturnValue({
      exercises: [mockExercise],
      total: 1,
      hasMore: false,
      isLoading: false,
      isFetching: false,
      error: null,
      generateExercise: vi.fn(),
      generateExerciseAsync: vi.fn(),
      isGenerating: false,
    } as unknown as ReturnType<typeof useExercises>);

    render(<ExercisesPage />, { wrapper: TestWrapper });

    expect(screen.getByRole("heading", { name: fr.exercises.title })).toBeInTheDocument();
    expect(screen.getByText("Test exercise")).toBeInTheDocument();
  });

  it("affiche l'état de chargement", () => {
    vi.mocked(useExercises).mockReturnValue({
      exercises: [],
      total: 0,
      hasMore: false,
      isLoading: true,
      isFetching: false,
      error: null,
      generateExercise: vi.fn(),
      generateExerciseAsync: vi.fn(),
      isGenerating: false,
    } as unknown as ReturnType<typeof useExercises>);

    render(<ExercisesPage />, { wrapper: TestWrapper });

    expect(screen.getByText(fr.exercises.list.loading)).toBeInTheDocument();
  });

  it("affiche le message liste vide", () => {
    vi.mocked(useExercises).mockReturnValue({
      exercises: [],
      total: 0,
      hasMore: false,
      isLoading: false,
      isFetching: false,
      error: null,
      generateExercise: vi.fn(),
      generateExerciseAsync: vi.fn(),
      isGenerating: false,
    } as unknown as ReturnType<typeof useExercises>);

    render(<ExercisesPage />, { wrapper: TestWrapper });

    expect(screen.getByText(fr.exercises.list.empty)).toBeInTheDocument();
  });
});
