import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useExerciseSolverController } from "@/hooks/useExerciseSolverController";
import { INTERLEAVED_STORAGE_KEY } from "@/lib/exercises/exerciseSolverSession";

const mockPush = vi.fn();
const mockReplace = vi.fn();
const mockUseExercise = vi.fn();
const mockSubmitAnswer = vi.fn();
const mockFetchNextReviewApi = vi.fn();
const mockReadSpacedReviewNext = vi.fn();
const mockStoreSpacedReviewNext = vi.fn();
const mockClearSpacedReviewNext = vi.fn();

let searchParamsGet: (key: string) => string | null = () => null;

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  useSearchParams: () => ({
    get: (key: string) => searchParamsGet(key),
  }),
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("@/hooks/useExercise", () => ({
  useExercise: (...args: unknown[]) => mockUseExercise(...args),
}));

vi.mock("@/hooks/useSubmitAnswer", () => ({
  useSubmitAnswer: () => ({
    submitAnswer: mockSubmitAnswer,
    isSubmitting: false,
    submitResult: undefined,
  }),
}));

vi.mock("@/hooks/useIrtScores", () => ({
  useIrtScores: () => ({
    resolveIsOpenAnswer: () => false,
  }),
}));

vi.mock("@/hooks/useNextReview", () => ({
  fetchNextReviewApi: () => mockFetchNextReviewApi(),
}));

vi.mock("@/lib/spacedReviewSession", () => ({
  readSpacedReviewNext: (...args: unknown[]) => mockReadSpacedReviewNext(...args),
  storeSpacedReviewNext: (...args: unknown[]) => mockStoreSpacedReviewNext(...args),
  clearSpacedReviewNext: (...args: unknown[]) => mockClearSpacedReviewNext(...args),
}));

describe("useExerciseSolverController", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    searchParamsGet = () => null;
    sessionStorage.clear();
    mockUseExercise.mockReturnValue({
      exercise: {
        id: 7,
        title: "E",
        question: "Q",
        correct_answer: "a",
        exercise_type: "ADDITION",
        choices: ["a", "b"],
        explanation: "ex",
      },
      isLoading: false,
      error: null,
    });
    mockFetchNextReviewApi.mockResolvedValue(null);
    mockReadSpacedReviewNext.mockReturnValue(null);
  });

  it("disables useExercise fetch in spaced-review mode", async () => {
    searchParamsGet = (key: string) => (key === "session" ? "spaced-review" : null);
    mockFetchNextReviewApi.mockResolvedValue({
      has_due_review: true,
      summary: {
        f04_initialized: true,
        active_cards_count: 1,
        due_today_count: 0,
        overdue_count: 0,
        next_review_date: "2026-01-01",
      },
      next_review: {
        review_item_id: 1,
        exercise_id: 7,
        due_status: "due_today",
        next_review_date: "2026-01-01",
        exercise: {
          id: 7,
          title: "R",
          question: "RQ",
          exercise_type: "ADDITION",
          difficulty: "INITIE",
          age_group: "6-8",
          difficulty_tier: null,
          choices: ["1", "2"],
          image_url: null,
          audio_url: null,
        },
      },
    });

    const { result } = renderHook(() => useExerciseSolverController(7));

    await waitFor(() => {
      expect(result.current.displayExercise?.title).toBe("R");
    });
    expect(mockUseExercise).toHaveBeenCalledWith(7, { enabled: false });
  });

  it("uses standard exercise as displayExercise outside spaced-review", () => {
    const { result } = renderHook(() => useExerciseSolverController(7));
    expect(result.current.sessionMode).toBeNull();
    expect(result.current.displayExercise?.title).toBe("E");
  });

  it("reads interleaved session from sessionStorage when mode is interleaved", () => {
    searchParamsGet = (key: string) => (key === "session" ? "interleaved" : null);
    const payload = JSON.stringify({
      plan: ["ADDITION"],
      completedCount: 0,
      length: 1,
    });
    sessionStorage.setItem(INTERLEAVED_STORAGE_KEY, payload);

    const { result } = renderHook(() => useExerciseSolverController(7));

    expect(result.current.sessionData?.plan).toEqual(["ADDITION"]);
  });
});
