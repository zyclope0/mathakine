import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { ExerciseModal } from "@/components/exercises/ExerciseModal";
import { useExercise } from "@/hooks/useExercise";
import { useSubmitAnswer } from "@/hooks/useSubmitAnswer";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useIrtScores } from "@/hooks/useIrtScores";

vi.mock("@/hooks/useExercise", () => ({
  useExercise: vi.fn(),
}));

vi.mock("@/hooks/useSubmitAnswer", () => ({
  useSubmitAnswer: vi.fn(),
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useExerciseTranslations: vi.fn(),
}));

vi.mock("@/hooks/useIrtScores", () => ({
  useIrtScores: vi.fn(),
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ExerciseModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(useExercise).mockReturnValue({
      exercise: {
        id: 1,
        title: "Addition simple",
        question: "2 + 2 = ?",
        exercise_type: "addition",
        age_group: "10_12",
        choices: ["3", "4"],
        explanation: "2 plus 2 fait 4.",
        hint: "Additionne les deux nombres.",
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useExercise>);

    vi.mocked(useSubmitAnswer).mockReturnValue({
      submitAnswer: vi.fn(),
      isSubmitting: false,
      submitResult: undefined,
    } as ReturnType<typeof useSubmitAnswer>);

    vi.mocked(useExerciseTranslations).mockReturnValue({
      getTypeDisplay: () => "Addition",
      getAgeDisplay: () => "10-12 ans",
    } as unknown as ReturnType<typeof useExerciseTranslations>);

    vi.mocked(useIrtScores).mockReturnValue({
      resolveIsOpenAnswer: () => false,
    } as unknown as ReturnType<typeof useIrtScores>);
  });

  it("réinitialise la réponse sélectionnée quand la modal est fermée puis rouverte", async () => {
    const onOpenChange = vi.fn();
    const { rerender } = render(
      <ExerciseModal exerciseId={1} open={true} onOpenChange={onOpenChange} />,
      { wrapper: TestWrapper }
    );

    const selectedChoice = screen.getByRole("radio", { name: /Option 2: 4/i });
    await userEvent.click(selectedChoice);
    expect(selectedChoice).toHaveAttribute("aria-checked", "true");

    rerender(<ExerciseModal exerciseId={1} open={false} onOpenChange={onOpenChange} />);
    rerender(<ExerciseModal exerciseId={1} open={true} onOpenChange={onOpenChange} />);

    expect(screen.getByRole("radio", { name: /Option 2: 4/i })).toHaveAttribute(
      "aria-checked",
      "false"
    );
  });

  it("affiche une explication lisible quand la réponse est correcte", async () => {
    vi.mocked(useSubmitAnswer).mockReturnValue({
      submitAnswer: vi.fn(),
      isSubmitting: false,
      submitResult: {
        is_correct: true,
        correct_answer: "4",
        explanation: "Pour soustraire 4 de 11, il faut calculer leur différence.",
      },
    } as ReturnType<typeof useSubmitAnswer>);

    render(<ExerciseModal exerciseId={1} open={true} onOpenChange={vi.fn()} />, {
      wrapper: TestWrapper,
    });

    const title = await screen.findByText("Explication");
    expect(title).toHaveClass("text-primary");

    const explanation = screen.getByText(
      "Pour soustraire 4 de 11, il faut calculer leur différence."
    );
    expect(explanation.closest(".math-text")).toHaveClass("text-foreground");
  });
});
