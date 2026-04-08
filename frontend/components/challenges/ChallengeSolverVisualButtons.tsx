"use client";

import { Button } from "@/components/ui/button";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export interface ChallengeSolverVisualButtonsProps {
  visualPositions: number[];
  visualChoices: string[];
  visualSelections: Record<number, string>;
  userAnswer: string;
  hasSubmitted: boolean;
  onSelectPosition: (pos: number, choice: string) => void;
  onSelectSimple: (choice: string) => void;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverVisualButtons({
  visualPositions,
  visualChoices,
  visualSelections,
  userAnswer,
  hasSubmitted,
  onSelectPosition,
  onSelectSimple,
  t,
}: ChallengeSolverVisualButtonsProps) {
  return (
    <div className="space-y-4">
      {visualPositions.length > 1 ? (
        visualPositions.map((pos) => (
          <div key={pos}>
            <p className="text-sm font-medium text-foreground mb-2">
              {t("positionLabel", { position: pos })}
            </p>
            <div className="flex flex-wrap gap-2">
              {visualChoices.map((choice) => {
                const isSelected = visualSelections[pos] === choice;
                return (
                  <Button
                    key={`${pos}-${choice}`}
                    variant={isSelected ? "default" : "outline"}
                    size="sm"
                    onClick={() => onSelectPosition(pos, choice)}
                    disabled={hasSubmitted}
                    aria-pressed={isSelected}
                  >
                    {choice}
                  </Button>
                );
              })}
            </div>
          </div>
        ))
      ) : (
        <div className="flex flex-wrap gap-2">
          {visualChoices.map((choice) => {
            const isSelected = userAnswer === choice;
            return (
              <Button
                key={choice}
                variant={isSelected ? "default" : "outline"}
                size="sm"
                onClick={() => onSelectSimple(choice)}
                disabled={hasSubmitted}
                aria-pressed={isSelected}
              >
                {choice}
              </Button>
            );
          })}
        </div>
      )}
      <p className="text-xs text-muted-foreground">{t("visualSelectHint")}</p>
    </div>
  );
}
