/**
 * Characterization tests for DiagnosticSolver (COMP-DIAGNOSTIC-01) — phases via mocked useDiagnostic.
 */

import type { ReactElement } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import { DiagnosticSolver } from "@/components/diagnostic/DiagnosticSolver";
import { useDiagnostic } from "@/hooks/useDiagnostic";
import fr from "@/messages/fr.json";
import type { DiagnosticQuestion, DiagnosticResult } from "@/hooks/useDiagnostic";

vi.mock("@/hooks/useDiagnostic", () => ({
  useDiagnostic: vi.fn(),
}));

const baseQuestion: DiagnosticQuestion = {
  exercise_type: "addition",
  difficulty: "INITIE",
  level_ordinal: 1,
  question: "1 + 1 = ?",
  choices: ["2", "3"],
  explanation: "Un plus un égale deux.",
  hint: "",
  question_number: 1,
  max_questions: 10,
  types_remaining: 4,
};

const baseResult: DiagnosticResult = {
  id: 1,
  completed_at: "",
  triggered_from: "onboarding",
  questions_asked: 5,
  duration_seconds: 12,
  scores: {
    addition: { level: 1, difficulty: "INITIE", correct: 3, total: 5 },
  },
};

function renderWithLocale(ui: ReactElement) {
  return render(
    <NextIntlClientProvider locale="fr" messages={fr}>
      {ui}
    </NextIntlClientProvider>
  );
}

function mockHook(partial: Partial<ReturnType<typeof useDiagnostic>>) {
  vi.mocked(useDiagnostic).mockReturnValue({
    phase: "idle",
    currentQuestion: null,
    selectedAnswer: null,
    isCorrect: null,
    correctAnswerForFeedback: null,
    result: null,
    error: null,
    startDiagnostic: vi.fn(),
    setSelectedAnswer: vi.fn(),
    submitAnswer: vi.fn(),
    nextQuestion: vi.fn(),
    ...partial,
  } as unknown as ReturnType<typeof useDiagnostic>);
}

describe("DiagnosticSolver", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("phase idle : titre, sous-titre et CTA démarrer", () => {
    mockHook({ phase: "idle" });
    renderWithLocale(<DiagnosticSolver />);

    expect(screen.getByRole("heading", { name: fr.diagnostic.title })).toBeInTheDocument();
    expect(screen.getByText(fr.diagnostic.subtitle)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: fr.diagnostic.startButton })).toBeInTheDocument();
  });

  it("phase error : titre erreur, message, réessayer et retour accueil", () => {
    mockHook({ phase: "error", error: "Réseau indisponible" });
    renderWithLocale(<DiagnosticSolver />);

    expect(screen.getByRole("heading", { name: fr.diagnostic.error.title })).toBeInTheDocument();
    expect(screen.getByText("Réseau indisponible")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: fr.diagnostic.error.retry })).toBeInTheDocument();
    const back = screen.getByRole("link", { name: new RegExp(fr.diagnostic.error.backHome, "i") });
    expect(back).toHaveAttribute("href", "/");
  });

  it("phase results : bilan, score par type et CTA tableau de bord / exercices", () => {
    mockHook({ phase: "results", result: baseResult });
    renderWithLocale(<DiagnosticSolver />);

    expect(screen.getByRole("heading", { name: fr.diagnostic.results.title })).toBeInTheDocument();
    expect(screen.getByText(fr.diagnostic.results.subtitle)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: new RegExp(fr.diagnostic.results.ctaDashboard, "i") })
    ).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: fr.diagnostic.results.ctaExercises })).toHaveAttribute(
      "href",
      "/exercises"
    );
    expect(screen.getByText(fr.diagnostic.results.typeLabel.addition)).toBeInTheDocument();
    expect(screen.getByLabelText(/addition:/i)).toBeInTheDocument();
  });

  it("phase results avec onComplete : CTA dashboard déclenche le callback", async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();
    mockHook({ phase: "results", result: baseResult });
    renderWithLocale(<DiagnosticSolver onComplete={onComplete} />);

    await user.click(
      screen.getByRole("button", { name: new RegExp(fr.diagnostic.results.ctaDashboard, "i") })
    );
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it("phase question : radiogroup et validation désactivée sans choix", () => {
    mockHook({
      phase: "question",
      currentQuestion: baseQuestion,
      selectedAnswer: null,
    });
    renderWithLocale(<DiagnosticSolver />);

    const group = screen.getByRole("radiogroup", {
      name: fr.diagnostic.question.chooseAnswer,
    });
    expect(within(group).getAllByRole("radio")).toHaveLength(2);
    const validate = screen.getByRole("button", { name: fr.diagnostic.answer.validateDisabled });
    expect(validate).toBeDisabled();
  });

  it("phase feedback : affiche bonne réponse et bouton question suivante", () => {
    mockHook({
      phase: "feedback",
      currentQuestion: baseQuestion,
      selectedAnswer: "2",
      isCorrect: true,
      correctAnswerForFeedback: "2",
    });
    renderWithLocale(<DiagnosticSolver />);

    expect(screen.getByText(fr.diagnostic.answer.correct)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: fr.diagnostic.answer.next })).toBeInTheDocument();
  });
});
