"use client";

import { cn } from "@/lib/utils";

interface GrowthMindsetHintProps {
  supportText: string;
  strategyText?: string;
  correctAnswerLabel?: string;
  correctAnswer?: string;
  className?: string;
}

/**
 * Bloc de feedback "pas encore" centré sur l'effort + stratégie.
 * Réutilisable pour garder une UX cohérente et éviter la duplication.
 */
export function GrowthMindsetHint({
  supportText,
  strategyText,
  correctAnswerLabel,
  correctAnswer,
  className,
}: GrowthMindsetHintProps) {
  return (
    <div className={cn("space-y-1", className)}>
      <p className="text-sm opacity-90">{supportText}</p>
      {strategyText && <p className="text-sm opacity-90">{strategyText}</p>}
      {correctAnswerLabel && correctAnswer && (
        <p className="text-sm opacity-90">
          {correctAnswerLabel} <strong>{correctAnswer}</strong>
        </p>
      )}
    </div>
  );
}

