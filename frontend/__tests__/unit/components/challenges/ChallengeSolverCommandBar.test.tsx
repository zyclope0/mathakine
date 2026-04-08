/**
 * Characterization tests for ChallengeSolverCommandBar (FFI-L18B).
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";
import { ChallengeSolverCommandBar } from "@/components/challenges/ChallengeSolverCommandBar";
import type { ChallengeSolverCommandBarProps } from "@/components/challenges/ChallengeSolverCommandBar";

const solver = fr.challenges.solver;

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function baseProps(
  overrides: Partial<ChallengeSolverCommandBarProps> = {}
): ChallengeSolverCommandBarProps {
  return {
    userAnswer: "",
    hasSubmitted: false,
    isSubmitting: false,
    isAnswerEmpty: true,
    isDisabled: true,
    hintsUsedCount: 0,
    availableHintsCount: 0,
    hasHints: false,
    showMcq: false,
    choicesArray: [],
    hasVisualButtons: false,
    visualChoices: [],
    visualPositions: [],
    visualSelections: {},
    responseMode: "open_text",
    challengeType: "logic",
    hasVisualData: false,
    puzzleOrder: [],
    textInputKind: "default",
    onSelectChoice: vi.fn(),
    onSelectVisualPosition: vi.fn(),
    onSelectVisualSimple: vi.fn(),
    onUserAnswerChange: vi.fn(),
    onSubmit: vi.fn(),
    onRequestHint: vi.fn(),
    ...overrides,
  };
}

describe("ChallengeSolverCommandBar", () => {
  it("renders MCQ choices in radiogroup when showMcq", () => {
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          showMcq: true,
          choicesArray: ["A", "B"],
          isAnswerEmpty: false,
          isDisabled: false,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByRole("radiogroup")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /Option 1.*A/ })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /Option 2.*B/ })).toBeInTheDocument();
  });

  it("renders visual simple buttons when single position", () => {
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          hasVisualButtons: true,
          visualPositions: [1],
          visualChoices: ["rond", "carré"],
          isAnswerEmpty: false,
          isDisabled: false,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByRole("button", { name: "rond" })).toBeInTheDocument();
    expect(screen.getByText(solver.visualSelectHint)).toBeInTheDocument();
  });

  it("renders multi-position labels when several visual positions", () => {
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          hasVisualButtons: true,
          visualPositions: [1, 2],
          visualChoices: ["x"],
          isAnswerEmpty: false,
          isDisabled: false,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByText(solver.positionLabel.replace("{position}", "1"))).toBeInTheDocument();
    expect(screen.getByText(solver.positionLabel.replace("{position}", "2"))).toBeInTheDocument();
  });

  it("renders order puzzle badges and disabled answer field", () => {
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          responseMode: "interactive_order",
          challengeType: "puzzle",
          puzzleOrder: ["un", "deux"],
          userAnswer: "1,2",
          isAnswerEmpty: false,
          isDisabled: false,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByText("1. un")).toBeInTheDocument();
    expect(screen.getByText("2. deux")).toBeInTheDocument();
    expect(screen.getByLabelText(solver.puzzleAnswerLabel)).toBeDisabled();
  });

  it("renders free text input with validate disabled when empty", () => {
    render(<ChallengeSolverCommandBar {...baseProps()} />, { wrapper });

    expect(screen.getByLabelText(solver.answerFieldLabel)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: solver.validateAnswer })).toBeDisabled();
    expect(screen.getByText(solver.validateHint)).toBeInTheDocument();
  });

  it("calls onSubmit when validate clicked and not disabled", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          userAnswer: "ok",
          isAnswerEmpty: false,
          isDisabled: false,
          onSubmit,
        })}
      />,
      { wrapper }
    );

    await user.click(screen.getByRole("button", { name: solver.validateAnswer }));
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("shows hint button when hasHints and disables after submit", () => {
    const hintAria = solver.requestHint.replace("{current}", "1").replace("{total}", "2");
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          hasHints: true,
          availableHintsCount: 2,
          hasSubmitted: true,
          isAnswerEmpty: false,
          isDisabled: true,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByRole("button", { name: hintAria })).toBeDisabled();
  });

  it("shows checking state on validate when submitting", () => {
    render(
      <ChallengeSolverCommandBar
        {...baseProps({
          userAnswer: "x",
          isAnswerEmpty: false,
          isDisabled: true,
          isSubmitting: true,
        })}
      />,
      { wrapper }
    );

    expect(screen.getByText(solver.checking)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: solver.validating })).toHaveAttribute(
      "aria-busy",
      "true"
    );
  });
});
