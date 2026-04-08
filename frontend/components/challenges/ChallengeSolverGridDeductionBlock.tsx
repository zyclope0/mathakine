"use client";

import { Badge } from "@/components/ui/badge";
import { parseDeductionAssociationParts } from "@/lib/challenges/challengeSolverCommandBar";
import type { ChallengeSolverCommandBarT } from "@/components/challenges/ChallengeSolverCommandBarTypes";

export interface ChallengeSolverGridDeductionBlockProps {
  userAnswer: string;
  t: ChallengeSolverCommandBarT;
}

export function ChallengeSolverGridDeductionBlock({
  userAnswer,
  t,
}: ChallengeSolverGridDeductionBlockProps) {
  return (
    <div className="space-y-3">
      {userAnswer ? (
        <div className="p-4 bg-muted/50 rounded-xl border border-border">
          <p className="text-sm font-medium text-foreground mb-2">
            {t("yourAssociations") || "Vos associations"}
          </p>
          <div className="space-y-1">
            {userAnswer.split(",").map((association, index) => {
              const { left, rights } = parseDeductionAssociationParts(association);
              return (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <Badge variant="outline" className="bg-primary/10">
                    {left}
                  </Badge>
                  <span className="text-muted-foreground">→</span>
                  {rights.map((part, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {part}
                    </Badge>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="p-4 bg-muted/50 rounded-xl border border-border">
          <p className="text-sm text-muted-foreground">
            {t("completeAssociationsAbove") ||
              "Complétez vos associations dans la grille ci-dessus"}
          </p>
        </div>
      )}
    </div>
  );
}
