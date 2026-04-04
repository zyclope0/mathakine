/**
 * Régression : Enter vide / espaces en mode open-answer ne doit pas déclencher onSubmitOpenAnswer.
 * Heuristique H5 (Prévention des erreurs) — NI audit 2026-04-04.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExerciseSolverChoices } from "@/components/exercises/ExerciseSolverChoices";

const baseLabels = {
  openAnswerLabel: "Votre réponse",
  openAnswerPlaceholder: "Entrez votre réponse…",
  option: (i: number) => `Option ${i}`,
  answerCorrect: "Correct",
  answerIncorrect: "Incorrect",
  reviewNoChoicesFallback: "Aucun choix disponible",
  noChoices: "Réponse correcte :",
};

function renderOpenAnswer(selectedAnswer: string | null, onSubmit = vi.fn(), onSelect = vi.fn()) {
  return render(
    <ExerciseSolverChoices
      isOpenAnswer={true}
      choices={[]}
      selectedAnswer={selectedAnswer}
      hasSubmitted={false}
      isCorrectChoice={() => false}
      sessionMode={null}
      correctAnswer="42"
      onSelectAnswer={onSelect}
      onSubmitOpenAnswer={onSubmit}
      labels={baseLabels}
    />
  );
}

describe("ExerciseSolverChoices — open-answer Enter guard", () => {
  it("n'appelle pas onSubmitOpenAnswer si l'input est vide (selectedAnswer null)", async () => {
    const onSubmit = vi.fn();
    renderOpenAnswer(null, onSubmit);
    const input = screen.getByLabelText("Votre réponse");
    await userEvent.type(input, "{Enter}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("n'appelle pas onSubmitOpenAnswer si l'input ne contient que des espaces", async () => {
    const onSubmit = vi.fn();
    // selectedAnswer est "   " (espaces) — le composant reçoit ça depuis le parent
    renderOpenAnswer("   ", onSubmit);
    const input = screen.getByLabelText("Votre réponse");
    await userEvent.keyboard("{Enter}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("appelle onSubmitOpenAnswer quand l'input a du contenu valide", async () => {
    const onSubmit = vi.fn();
    renderOpenAnswer("42", onSubmit);
    const input = screen.getByLabelText("Votre réponse");
    await userEvent.click(input);
    await userEvent.keyboard("{Enter}");
    expect(onSubmit).toHaveBeenCalledOnce();
  });
});
