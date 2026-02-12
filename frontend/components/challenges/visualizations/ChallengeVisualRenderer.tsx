"use client";

import { CHALLENGE_TYPES } from "@/lib/constants/challenges";
import { SequenceRenderer } from "./SequenceRenderer";
import { PatternRenderer } from "./PatternRenderer";
import { VisualRenderer } from "./VisualRenderer";
import { PuzzleRenderer } from "./PuzzleRenderer";
import { GraphRenderer } from "./GraphRenderer";
import { DeductionRenderer } from "./DeductionRenderer";
import { RiddleRenderer } from "./RiddleRenderer";
import { ChessRenderer } from "./ChessRenderer";
import { ProbabilityRenderer } from "./ProbabilityRenderer";
import { CodingRenderer } from "./CodingRenderer";
import { DefaultRenderer } from "./DefaultRenderer";
import type { Challenge } from "@/types/api";

interface ChallengeVisualRendererProps {
  challenge: Challenge;
  className?: string | undefined;
  onPuzzleOrderChange?: ((order: string[]) => void) | undefined;
  onAnswerChange?: ((answer: string) => void) | undefined;
}

/**
 * Composant principal qui route vers le bon renderer selon le type de challenge.
 * Gère le rendu interactif des visual_data selon le challenge_type.
 */
export function ChallengeVisualRenderer({
  challenge,
  className,
  onPuzzleOrderChange,
  onAnswerChange,
}: ChallengeVisualRendererProps) {
  if (!challenge.visual_data) {
    return null;
  }

  const challengeType = challenge.challenge_type?.toLowerCase();

  // Router vers le bon composant selon le type
  switch (challengeType) {
    case CHALLENGE_TYPES.SEQUENCE:
      return (
        <SequenceRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
          {...(onAnswerChange !== undefined && { onAnswerChange })}
        />
      );

    case CHALLENGE_TYPES.PATTERN:
      return (
        <PatternRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
          {...(onAnswerChange !== undefined && { onAnswerChange })}
        />
      );

    case CHALLENGE_TYPES.VISUAL:
      // VISUAL inclut les défis spatiaux (rotation, symétrie, etc.)
      return (
        <VisualRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    case CHALLENGE_TYPES.PUZZLE:
      return (
        <PuzzleRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
          {...(onPuzzleOrderChange !== undefined && { onOrderChange: onPuzzleOrderChange })}
        />
      );

    case CHALLENGE_TYPES.GRAPH:
      return (
        <GraphRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    case CHALLENGE_TYPES.DEDUCTION:
      return (
        <DeductionRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
          {...(onAnswerChange !== undefined && { onAnswerChange })}
        />
      );

    case CHALLENGE_TYPES.RIDDLE:
      return (
        <RiddleRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    case CHALLENGE_TYPES.CHESS:
      return (
        <ChessRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    case CHALLENGE_TYPES.PROBABILITY:
      return (
        <ProbabilityRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    case CHALLENGE_TYPES.CODING:
      return (
        <CodingRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );

    default:
      // Fallback pour les types non supportés ou personnalisés
      return (
        <DefaultRenderer
          visualData={challenge.visual_data}
          {...(className !== undefined && { className })}
        />
      );
  }
}
