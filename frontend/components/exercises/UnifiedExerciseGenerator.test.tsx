import type { ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { UnifiedExerciseGenerator } from "./UnifiedExerciseGenerator";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import type { Exercise } from "@/types/api";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

const generateExerciseAsync = vi.fn();
let isQuickPending = false;

vi.mock("@/hooks/useExercises", () => ({
  useExercises: () => ({
    generateExercise: vi.fn(),
    generateExerciseAsync,
    isGenerating: isQuickPending,
    exercises: [],
    total: 0,
    hasMore: false,
    isLoading: false,
    isFetching: false,
    error: null,
  }),
}));

vi.mock("@/hooks/useAIExerciseGenerator", () => ({
  useAIExerciseGenerator: () => ({
    isGenerating: false,
    streamedText: "",
    generatedExercise: null,
    setGeneratedExercise: vi.fn(),
    generate: vi.fn(),
    cancel: vi.fn(),
  }),
}));

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

const quickExercise: Exercise = {
  id: 99,
  title: "Exercice rapide",
  question: "2+2?",
  correct_answer: "4",
  exercise_type: "addition",
  difficulty: "initie",
  choices: ["3", "4", "5"],
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
  ai_generated: false,
  view_count: 0,
};

describe("UnifiedExerciseGenerator — chemin rapide (non-IA)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    isQuickPending = false;
    generateExerciseAsync.mockResolvedValue(quickExercise);
  });

  it("après succès génération rapide, affiche la CTA Voir l'exercice et navigue au clic", async () => {
    render(
      <Wrapper>
        <UnifiedExerciseGenerator />
      </Wrapper>
    );

    const generateBtn = screen.getByRole("button", { name: fr.exercises.generator.generate });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(generateExerciseAsync).toHaveBeenCalledWith({
        exercise_type: "addition",
        age_group: "6-8",
        save: true,
      });
    });

    const viewBtn = await screen.findByRole("button", {
      name: fr.exercises.aiGenerator.viewExercise,
    });
    expect(viewBtn).toBeTruthy();
    fireEvent.click(viewBtn);
    expect(push).toHaveBeenCalledWith("/exercises/99");
  });

  it("sans id persisté, pas de bouton Voir l'exercice", async () => {
    generateExerciseAsync.mockResolvedValue({
      ...quickExercise,
      id: 0 as unknown as number,
    });
    render(
      <Wrapper>
        <UnifiedExerciseGenerator />
      </Wrapper>
    );
    fireEvent.click(screen.getByRole("button", { name: fr.exercises.generator.generate }));
    await waitFor(() => expect(generateExerciseAsync).toHaveBeenCalled());
    expect(
      screen.queryByRole("button", { name: fr.exercises.aiGenerator.viewExercise })
    ).toBeNull();
  });
});
