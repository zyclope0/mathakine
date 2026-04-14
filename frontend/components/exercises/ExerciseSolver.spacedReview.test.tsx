import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
const mockPush = vi.fn();
const mockReplace = vi.fn();
const mockUseExercise = vi.fn();
const mockFetchNextReviewApi = vi.fn();

const reviewSafeExerciseFixture = {
  id: 1,
  title: "Test SR",
  question: "2+2?",
  exercise_type: "ADDITION",
  difficulty: "INITIE",
  age_group: "6-8",
  difficulty_tier: null,
  choices: ["3", "4"],
  image_url: null,
  audio_url: null,
};

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  useSearchParams: () => ({
    get: (key: string) => (key === "session" ? "spaced-review" : null),
  }),
}));

vi.mock("@/hooks/useExercise", () => ({
  useExercise: (...args: unknown[]) => mockUseExercise(...args),
}));

vi.mock("@/hooks/useSubmitAnswer", () => ({
  useSubmitAnswer: () => ({
    submitAnswer: vi.fn(),
    isSubmitting: false,
    submitResult: null,
  }),
}));

vi.mock("@/hooks/useIrtScores", () => ({
  useIrtScores: () => ({
    resolveIsOpenAnswer: () => false,
  }),
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useExerciseTranslations: () => ({
    getTypeDisplay: () => "Addition",
    getAgeDisplay: () => "6-8",
  }),
}));

vi.mock("@/hooks/useNextReview", () => ({
  fetchNextReviewApi: () => mockFetchNextReviewApi(),
}));

import { ExerciseSolver } from "./ExerciseSolver";

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ExerciseSolver - session spaced-review", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    mockUseExercise.mockReturnValue({
      exercise: undefined,
      isLoading: false,
      error: null,
    });
    mockFetchNextReviewApi.mockResolvedValue(null);
  });

  it("renders the spaced-review safe payload without spoiler-bearing fallback data", async () => {
    mockFetchNextReviewApi.mockResolvedValue({
      has_due_review: true,
      summary: {
        f04_initialized: true,
        active_cards_count: 2,
        due_today_count: 1,
        overdue_count: 0,
        next_review_date: "2026-03-30",
      },
      next_review: {
        review_item_id: 43,
        exercise_id: 1,
        due_status: "due_today",
        next_review_date: "2026-03-29",
        exercise: reviewSafeExerciseFixture,
      },
    });

    render(<ExerciseSolver exerciseId={1} />, { wrapper: Wrapper });

    await waitFor(() => {
      expect(screen.getByText("Test SR")).toBeInTheDocument();
    });
    expect(screen.getByText(/Entraînement/i)).toBeInTheDocument();
    expect(screen.queryByText(/indice discret/i)).not.toBeInTheDocument();
    expect(mockUseExercise).toHaveBeenCalledWith(1, { enabled: false });
    expect(mockFetchNextReviewApi).toHaveBeenCalled();
  });

  it("keeps the first choice keyboard-reachable before any selection", async () => {
    mockFetchNextReviewApi.mockResolvedValue({
      has_due_review: true,
      summary: {
        f04_initialized: true,
        active_cards_count: 2,
        due_today_count: 1,
        overdue_count: 0,
        next_review_date: "2026-03-30",
      },
      next_review: {
        review_item_id: 43,
        exercise_id: 1,
        due_status: "due_today",
        next_review_date: "2026-03-29",
        exercise: reviewSafeExerciseFixture,
      },
    });

    render(<ExerciseSolver exerciseId={1} />, { wrapper: Wrapper });

    const choices = await screen.findAllByRole("radio");
    expect(choices).toHaveLength(2);
    expect(choices[0]).toHaveAttribute("tabindex", "0");
    expect(choices[1]).toHaveAttribute("tabindex", "-1");
  });
});
