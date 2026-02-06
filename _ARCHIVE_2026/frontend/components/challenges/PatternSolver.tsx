'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils/cn';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';

export type PatternType = 'arithmetic' | 'geometric' | 'fibonacci' | 'custom';

export interface PatternChallenge {
  sequence: number[];
  pattern: PatternType;
  nextValue: number;
  options?: number[];
  explanation?: string;
}

interface PatternSolverProps {
  challenge: PatternChallenge;
  onSolve: (selectedValue: number) => void;
  disabled?: boolean;
  showFeedback?: boolean;
}

export function PatternSolver({
  challenge,
  onSolve,
  disabled = false,
  showFeedback = true,
}: PatternSolverProps) {
  const { focusMode, reducedMotion } = useAccessibilityStore();
  const [selectedValue, setSelectedValue] = useState<number | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  // Générer les options si non fournies
  const options =
    challenge.options ||
    [
      challenge.nextValue - 2,
      challenge.nextValue - 1,
      challenge.nextValue,
      challenge.nextValue + 1,
      challenge.nextValue + 2,
    ].filter((v) => v >= 0); // Éviter les valeurs négatives

  const handleSelect = (value: number) => {
    if (disabled || hasSubmitted) return;
    setSelectedValue(value);
    setIsCorrect(null);
  };

  const handleSubmit = () => {
    if (disabled || selectedValue === null || hasSubmitted) return;

    const correct = selectedValue === challenge.nextValue;
    setIsCorrect(correct);
    setHasSubmitted(true);

    if (showFeedback) {
      // Appeler le callback après un court délai pour permettre le feedback visuel
      setTimeout(() => {
        onSolve(selectedValue);
      }, reducedMotion ? 0 : 500);
    } else {
      onSolve(selectedValue);
    }
  };

  const getPatternDescription = () => {
    switch (challenge.pattern) {
      case 'arithmetic':
        return 'Séquence arithmétique';
      case 'geometric':
        return 'Séquence géométrique';
      case 'fibonacci':
        return 'Séquence de Fibonacci';
      case 'custom':
        return 'Séquence personnalisée';
      default:
        return 'Séquence';
    }
  };

  return (
    <div className="space-y-6" role="group" aria-label="Résolveur de séquence">
      {/* Description du pattern */}
      <div className="text-sm text-muted-foreground">
        <span className="font-semibold">Type :</span> {getPatternDescription()}
      </div>

      {/* Séquence affichée */}
      <div
        className="flex flex-wrap gap-4 items-center justify-center"
        role="list"
        aria-label="Séquence à compléter"
      >
        {challenge.sequence.map((value, index) => (
          <div
            key={index}
            className={cn(
              'w-16 h-16 bg-primary/20 border-2 border-primary rounded-lg flex items-center justify-center text-2xl font-bold',
              focusMode && 'w-20 h-20 text-3xl'
            )}
            role="listitem"
            aria-label={`Valeur ${index + 1} : ${value}`}
          >
            {value}
          </div>
        ))}
        <div
          className={cn(
            'w-16 h-16 bg-surface-elevated border-2 border-dashed border-primary/50 rounded-lg flex items-center justify-center text-2xl font-bold',
            focusMode && 'w-20 h-20 text-3xl',
            selectedValue !== null && 'border-primary border-solid bg-primary/10'
          )}
          role="listitem"
          aria-label="Valeur manquante"
        >
          {selectedValue !== null ? selectedValue : '?'}
        </div>
      </div>

      {/* Options de réponse */}
      <div
        className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2"
        role="radiogroup"
        aria-label="Options de réponse"
      >
        {options.map((value) => {
          const isSelected = selectedValue === value;
          const isCorrectOption = value === challenge.nextValue;
          const showCorrect = hasSubmitted && isCorrect !== null;

          return (
            <Button
              key={value}
              variant={isSelected ? 'default' : 'outline'}
              onClick={() => handleSelect(value)}
              disabled={disabled || hasSubmitted}
              className={cn(
                'h-16 text-lg font-semibold',
                focusMode && 'h-20 text-xl',
                showCorrect &&
                  (isCorrectOption
                    ? 'bg-success text-success-foreground border-success'
                    : isSelected && !isCorrectOption
                      ? 'bg-error text-error-foreground border-error'
                      : ''),
                !reducedMotion && 'transition-all duration-200'
              )}
              role="radio"
              aria-checked={isSelected}
              aria-label={`Option ${value}`}
              tabIndex={disabled ? -1 : 0}
            >
              {value}
            </Button>
          );
        })}
      </div>

      {/* Bouton de validation */}
      <div className="flex justify-center">
        <Button
          onClick={handleSubmit}
          disabled={disabled || selectedValue === null || hasSubmitted}
          size="lg"
          className={cn(focusMode && 'h-14 text-lg px-8')}
          aria-label="Valider la réponse"
        >
          {hasSubmitted
            ? isCorrect
              ? '✅ Correct !'
              : '❌ Incorrect'
            : 'Valider'}
        </Button>
      </div>

      {/* Feedback et explication */}
      {showFeedback && hasSubmitted && isCorrect !== null && (
        <div
          className={cn(
            'p-4 rounded-lg border-2',
            isCorrect
              ? 'bg-success/20 text-success border-success/30'
              : 'bg-error/20 text-error border-error/30'
          )}
          role="alert"
          aria-live="polite"
        >
          <p className="font-semibold mb-2">
            {isCorrect ? '✅ Correct !' : '❌ Incorrect, essaie encore !'}
          </p>
          {challenge.explanation && (
            <p className="text-sm mt-2">{challenge.explanation}</p>
          )}
          {!isCorrect && (
            <p className="text-sm mt-2 font-semibold">
              La bonne réponse était : {challenge.nextValue}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

