"use client";

import { Button } from "@/components/ui/button";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export interface ChallengeSolverMcqGridProps {
  choicesArray: string[];
  userAnswer: string;
  hasSubmitted: boolean;
  onSelectChoice: (choice: string) => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverMcqGrid({
  choicesArray,
  userAnswer,
  hasSubmitted,
  onSelectChoice,
  t,
}: ChallengeSolverMcqGridProps) {
  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 gap-3"
      role="radiogroup"
      aria-label="Choix de réponses pour le défi logique"
    >
      {choicesArray.map((choice, index) => (
        <Button
          key={index}
          variant={userAnswer === choice ? "default" : "outline"}
          onClick={() => onSelectChoice(choice)}
          className="h-auto py-4 text-left justify-start"
          disabled={hasSubmitted}
          role="radio"
          aria-checked={userAnswer === choice}
          aria-label={`${t("option", { index: index + 1 })}: ${choice}`}
          tabIndex={hasSubmitted ? -1 : userAnswer === choice || index === 0 ? 0 : -1}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              onSelectChoice(choice);
            }
            if (e.key === "ArrowRight" && index < choicesArray.length - 1) {
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
        </Button>
      ))}
    </div>
  );
}
