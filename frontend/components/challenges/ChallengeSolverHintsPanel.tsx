"use client";

import { Lightbulb } from "lucide-react";
import { useTranslations } from "next-intl";
import { MathText } from "@/components/ui/MathText";

interface ChallengeSolverHintsPanelProps {
  hintsUsed: number[];
  availableHints: string[];
}

/**
 * Affiche la liste des indices déjà révélés.
 * Composant purement visuel — pas de logique getHint.
 * Rendu nul si aucun indice n'a été utilisé.
 */
export function ChallengeSolverHintsPanel({
  hintsUsed,
  availableHints,
}: ChallengeSolverHintsPanelProps) {
  const t = useTranslations("challenges.solver");

  if (hintsUsed.length === 0) return null;

  return (
    <div className="mt-6 bg-muted/50 border border-border rounded-xl p-4">
      <h3 className="flex items-center gap-2 text-amber-400 font-semibold mb-3">
        <Lightbulb className="h-5 w-5" />
        {t("hintsUsed")}
      </h3>
      <ul className="space-y-2">
        {hintsUsed.map((hintIndex) => {
          const hintText =
            hintIndex > 0 && hintIndex <= availableHints.length
              ? availableHints[hintIndex - 1]
              : null;
          if (!hintText) return null;
          return (
            <li key={hintIndex} className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">{hintIndex}.</span>
              <MathText size="sm" className="text-foreground">
                {hintText}
              </MathText>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
