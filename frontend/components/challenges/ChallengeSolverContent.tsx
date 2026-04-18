"use client";

import Image from "next/image";
import { MathText } from "@/components/ui/MathText";
import { ChallengeVisualRenderer } from "@/components/challenges/visualizations/ChallengeVisualRenderer";
import { useTranslations } from "next-intl";
import type { Challenge } from "@/types/api";
import type { ChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";

interface ChallengeSolverContentProps {
  challenge: Challenge;
  retryKey: number;
  onPuzzleOrderChange: (order: string[]) => void;
  onAnswerChange: (answer: string) => void;
  visualResponseMode: ChallengeResponseMode;
  visualShowMcq: boolean;
}

/**
 * Bloc de contenu du défi : description, question, image, visual renderer.
 * Le keying `visual-${id}-${retryKey}` préserve le remount des visualisations
 * lors d'un retry sans changer le comportement actuel.
 */
export function ChallengeSolverContent({
  challenge,
  retryKey,
  onPuzzleOrderChange,
  onAnswerChange,
  visualResponseMode,
  visualShowMcq,
}: ChallengeSolverContentProps) {
  const t = useTranslations("challenges.solver");

  return (
    <div className="space-y-4">
      {challenge.description && (
        <div className="bg-muted/50 border border-border rounded-xl p-4">
          <MathText size="lg" className="text-foreground">
            {challenge.description}
          </MathText>
        </div>
      )}

      {challenge.question && challenge.question !== challenge.description && (
        <div className="bg-muted/50 border border-border rounded-xl p-4">
          <MathText size="lg" className="text-foreground font-medium">
            {challenge.question}
          </MathText>
        </div>
      )}

      {challenge.image_url && (
        <div className="flex justify-center">
          <div className="relative w-full max-w-2xl aspect-video rounded-xl overflow-hidden border border-border">
            <Image
              src={challenge.image_url}
              alt={t("challengeImage")}
              fill
              className="object-contain rounded-xl"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
              loading="lazy"
            />
          </div>
        </div>
      )}

      {challenge.visual_data && (
        <div key={`visual-${challenge.id}-${retryKey}`}>
          <ChallengeVisualRenderer
            challenge={challenge}
            onPuzzleOrderChange={onPuzzleOrderChange}
            onAnswerChange={onAnswerChange}
            responseMode={visualResponseMode}
            showMcq={visualShowMcq}
          />
        </div>
      )}
    </div>
  );
}
