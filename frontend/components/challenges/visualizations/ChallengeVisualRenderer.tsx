'use client';

import { CHALLENGE_TYPES } from '@/lib/constants/challenges';
import { SequenceRenderer } from './SequenceRenderer';
import { PatternRenderer } from './PatternRenderer';
import { VisualRenderer } from './VisualRenderer';
import { PuzzleRenderer } from './PuzzleRenderer';
import { GraphRenderer } from './GraphRenderer';
import { DefaultRenderer } from './DefaultRenderer';
import type { Challenge } from '@/types/api';

interface ChallengeVisualRendererProps {
  challenge: Challenge;
  className?: string;
  onPuzzleOrderChange?: (order: string[]) => void;
  onAnswerChange?: (answer: string) => void;
}

/**
 * Composant principal qui route vers le bon renderer selon le type de challenge.
 * Gère le rendu interactif des visual_data selon le challenge_type.
 */
export function ChallengeVisualRenderer({ challenge, className, onPuzzleOrderChange, onAnswerChange }: ChallengeVisualRendererProps) {
  if (!challenge.visual_data) {
    return null;
  }

  const challengeType = challenge.challenge_type?.toLowerCase();

  // Router vers le bon composant selon le type
  switch (challengeType) {
    case CHALLENGE_TYPES.SEQUENCE:
      return <SequenceRenderer visualData={challenge.visual_data} className={className} onAnswerChange={onAnswerChange} />;
    
    case CHALLENGE_TYPES.PATTERN:
      return <PatternRenderer visualData={challenge.visual_data} className={className} onAnswerChange={onAnswerChange} />;
    
    case CHALLENGE_TYPES.VISUAL:
    case CHALLENGE_TYPES.SPATIAL:
      return <VisualRenderer visualData={challenge.visual_data} className={className} />;
    
    case CHALLENGE_TYPES.PUZZLE:
      return <PuzzleRenderer visualData={challenge.visual_data} className={className} onOrderChange={onPuzzleOrderChange} />;
    
    case CHALLENGE_TYPES.GRAPH:
      return <GraphRenderer visualData={challenge.visual_data} className={className} />;
    
    default:
      // Fallback pour les types non supportés ou personnalisés
      return <DefaultRenderer visualData={challenge.visual_data} className={className} />;
  }
}

