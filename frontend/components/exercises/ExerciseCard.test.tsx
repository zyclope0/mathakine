import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExerciseCard } from "./ExerciseCard";
import type { Exercise } from "@/types/api";
import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import fr from "@/messages/fr.json";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </NextIntlClientProvider>
  );
}

const noop = vi.fn();

describe("ExerciseCard", () => {
  const mockExercise: Exercise = {
    id: 1,
    title: "Test Exercise",
    question: "What is 2 + 2?",
    exercise_type: "addition",
    difficulty: "initie",
    correct_answer: "4",
    choices: ["3", "4", "5", "6"],
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
    ai_generated: false,
    view_count: 0,
  };

  it("affiche le titre de l'exercice", () => {
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByText("Test Exercise")).toBeInTheDocument();
  });

  it("affiche la question de l'exercice", () => {
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByText("What is 2 + 2?")).toBeInTheDocument();
  });

  it("affiche le badge de type d'exercice", () => {
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByText(/addition/i)).toBeInTheDocument();
  });

  it("n'affiche pas de badge IA textuel — seule l'icône Sparkles est présente (distill P2)", () => {
    const aiExercise = { ...mockExercise, ai_generated: true };
    render(<ExerciseCard exercise={aiExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    // Le badge texte "IA" a été retiré — l'icône Sparkles (aria-hidden) suffit
    expect(screen.queryByText("IA")).not.toBeInTheDocument();
  });

  it("affiche le CTA Résoudre (pill discret, carte entière cliquable)", () => {
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    const cta = screen.getAllByText(/résoudre/i)[0];
    expect(cta).toBeInTheDocument();
  });

  it("la carte est un bouton accessible au clavier avec aria-labelledby sur le titre", () => {
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    // ContentCardBase monte un motion.button quand onClick est présent
    const btn = screen.getByRole("button");
    expect(btn).toHaveAttribute("aria-labelledby", `exercise-title-${mockExercise.id}`);
    expect(btn).toHaveAttribute("aria-describedby", `exercise-description-${mockExercise.id}`);
  });

  it("appelle onOpen avec l'id de l'exercice au clic", async () => {
    const onOpen = vi.fn();
    render(<ExerciseCard exercise={mockExercise} completed={false} onOpen={onOpen} />, {
      wrapper: TestWrapper,
    });
    screen.getByRole("button").click();
    expect(onOpen).toHaveBeenCalledWith(mockExercise.id);
  });

  it("affiche le badge Résolu quand completed est true", () => {
    render(<ExerciseCard exercise={mockExercise} completed onOpen={noop} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByLabelText(/résolu/i)).toBeInTheDocument();
  });
});
