"use client";

import { cn } from "@/lib/utils";

interface ExerciseSolverChoicesProps {
  /** Open-answer mode (IRT-resolved). */
  isOpenAnswer: boolean;
  choices: string[];
  selectedAnswer: string | null;
  hasSubmitted: boolean;
  /** Returns true if `choice` is the correct answer (after submit). */
  isCorrectChoice: (choice: string) => boolean;
  sessionMode: "interleaved" | "spaced-review" | null;
  /** The canonical correct answer (for no-choices fallback). */
  correctAnswer: string;
  onSelectAnswer: (choice: string) => void;
  onSubmitOpenAnswer: () => void;
  /** i18n strings */
  labels: {
    openAnswerLabel: string;
    openAnswerPlaceholder: string;
    option: (index: number) => string;
    answerCorrect: string;
    answerIncorrect: string;
    reviewNoChoicesFallback: string;
    noChoices: string;
  };
}

export function ExerciseSolverChoices({
  isOpenAnswer,
  choices,
  selectedAnswer,
  hasSubmitted,
  isCorrectChoice,
  sessionMode,
  correctAnswer,
  onSelectAnswer,
  onSubmitOpenAnswer,
  labels,
}: ExerciseSolverChoicesProps) {
  if (isOpenAnswer) {
    return (
      <div className="mb-8 space-y-3">
        <label
          htmlFor="open-answer-input"
          className="block text-sm font-medium text-muted-foreground"
        >
          {labels.openAnswerLabel}
        </label>
        <input
          id="open-answer-input"
          type="text"
          value={selectedAnswer ?? ""}
          onChange={(e) => !hasSubmitted && onSelectAnswer(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && selectedAnswer && !hasSubmitted) onSubmitOpenAnswer();
          }}
          disabled={hasSubmitted}
          autoFocus
          className={cn(
            "w-full rounded-2xl py-5 px-6 text-2xl font-medium text-foreground bg-secondary/50 border-2 border-border",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all",
            hasSubmitted && "opacity-70 cursor-not-allowed",
            hasSubmitted && selectedAnswer !== null && isCorrectChoice(selectedAnswer ?? "")
              ? "border-emerald-500 bg-emerald-500/10 text-emerald-400"
              : hasSubmitted && "border-red-500 bg-red-500/10 text-red-400"
          )}
          placeholder={labels.openAnswerPlaceholder}
          aria-label={labels.openAnswerLabel}
        />
      </div>
    );
  }

  if (choices.length > 0) {
    return (
      <div
        className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8"
        role="radiogroup"
        aria-label="Choix de réponses pour l'exercice"
      >
        {choices.map((choice, index) => {
          const isSelected = selectedAnswer === choice;
          const showCorrect = hasSubmitted && isCorrectChoice(choice);
          const showIncorrect = hasSubmitted && isSelected && !isCorrectChoice(choice);

          return (
            <button
              key={index}
              type="button"
              className={cn(
                "rounded-2xl py-6 md:py-8 text-2xl font-medium text-foreground cursor-pointer transition-all text-center border-2",
                !hasSubmitted &&
                  !showCorrect &&
                  !showIncorrect &&
                  (isSelected
                    ? "border-primary bg-primary/20 shadow-[0_0_20px_hsl(var(--primary)/0.3)]"
                    : "bg-secondary/50 border-border hover:bg-secondary hover:border-primary/50 hover:-translate-y-1"),
                showCorrect &&
                  "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:bg-emerald-500/20",
                showIncorrect && "bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20",
                hasSubmitted && !isSelected && !isCorrectChoice(choice) && "opacity-50"
              )}
              onClick={() => onSelectAnswer(choice)}
              disabled={hasSubmitted}
              role="radio"
              aria-checked={isSelected ? "true" : "false"}
              aria-label={`${labels.option(index + 1)}: ${choice}${
                hasSubmitted
                  ? isCorrectChoice(choice)
                    ? ` - ${labels.answerCorrect}`
                    : showIncorrect
                      ? ` - ${labels.answerIncorrect}`
                      : ""
                  : ""
              }`}
              tabIndex={hasSubmitted ? -1 : isSelected || index === 0 ? 0 : -1}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectAnswer(choice);
                }
                if (e.key === "ArrowRight" && index < choices.length - 1) {
                  e.preventDefault();
                  const next = e.currentTarget.parentElement?.children[index + 1] as HTMLElement;
                  next?.focus();
                }
                if (e.key === "ArrowLeft" && index > 0) {
                  e.preventDefault();
                  const prev = e.currentTarget.parentElement?.children[index - 1] as HTMLElement;
                  prev?.focus();
                }
              }}
            >
              {choice}
            </button>
          );
        })}
      </div>
    );
  }

  if (sessionMode === "spaced-review" && !hasSubmitted) {
    return (
      <div className="p-6 border rounded-xl bg-muted/40 border-border mb-8">
        <p className="text-muted-foreground text-sm leading-relaxed">
          {labels.reviewNoChoicesFallback}
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg bg-muted/50 mb-8">
      <p className="text-muted-foreground text-sm">
        {labels.noChoices} <strong>{correctAnswer}</strong>
      </p>
    </div>
  );
}
