import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { ApiClientError } from "@/lib/api/client";

const mockPush = vi.fn();
const mockReplace = vi.fn();
const mockUseExercise = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  useSearchParams: () => ({
    get: () => null,
  }),
}));

vi.mock("@/hooks/useExercise", () => ({
  useExercise: (...args: unknown[]) => mockUseExercise(...args),
}));

vi.mock("@/hooks/useSubmitAnswer", () => ({
  useSubmitAnswer: () => ({
    submitAnswer: vi.fn(),
    isSubmitting: false,
    submitResult: undefined,
  }),
}));

vi.mock("@/hooks/useIrtScores", () => ({
  useIrtScores: () => ({
    resolveIsOpenAnswer: () => false,
  }),
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useExerciseTranslations: () => ({
    getTypeDisplay: () => "Type",
    getAgeDisplay: () => "6-8",
  }),
}));

vi.mock("@/hooks/useNextReview", () => ({
  fetchNextReviewApi: vi.fn().mockResolvedValue(null),
}));

import { ExerciseSolver } from "./ExerciseSolver";

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ExerciseSolver (facade)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it("shows loading state while exercise query is pending", () => {
    mockUseExercise.mockReturnValue({
      exercise: undefined,
      isLoading: true,
      error: null,
    });

    render(<ExerciseSolver exerciseId={5} />, { wrapper: Wrapper });

    expect(screen.getByText(/Chargement/i)).toBeInTheDocument();
  });

  it("shows not found copy when exercise returns 404", () => {
    mockUseExercise.mockReturnValue({
      exercise: undefined,
      isLoading: false,
      error: new ApiClientError("Not found", 404),
    });

    render(<ExerciseSolver exerciseId={5} />, { wrapper: Wrapper });

    expect(screen.getByText(/n'existe pas/i)).toBeInTheDocument();
  });
});
