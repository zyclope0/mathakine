/**
 * Regression : Enter vide / espaces en mode open-answer ne doit pas declencher onSubmitOpenAnswer.
 * Heuristique H5 - Prevention des erreurs.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExerciseSolverChoices } from "./ExerciseSolverChoices";

const baseLabels = {
  openAnswerLabel: "Votre reponse",
  openAnswerPlaceholder: "Entrez votre reponse...",
  option: (index: number) => `Option ${index}`,
  answerCorrect: "Correct",
  answerIncorrect: "Incorrect",
  reviewNoChoicesFallback: "Aucun choix disponible",
  noChoices: "Reponse correcte :",
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

describe("ExerciseSolverChoices - open-answer Enter guard", () => {
  it("n'appelle pas onSubmitOpenAnswer si l'input est vide", async () => {
    const onSubmit = vi.fn();
    renderOpenAnswer(null, onSubmit);
    const input = screen.getByLabelText("Votre reponse");
    await userEvent.type(input, "{Enter}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("n'appelle pas onSubmitOpenAnswer si l'input ne contient que des espaces", async () => {
    const onSubmit = vi.fn();
    renderOpenAnswer("   ", onSubmit);
    screen.getByLabelText("Votre reponse");
    await userEvent.keyboard("{Enter}");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("appelle onSubmitOpenAnswer quand l'input a du contenu valide", async () => {
    const onSubmit = vi.fn();
    renderOpenAnswer("42", onSubmit);
    const input = screen.getByLabelText("Votre reponse");
    await userEvent.click(input);
    await userEvent.keyboard("{Enter}");
    expect(onSubmit).toHaveBeenCalledOnce();
  });
});
