'use client';

import { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useExercise } from '@/hooks/useExercise';
import { useSubmitAnswer } from '@/hooks/useSubmitAnswer';
import { EXERCISE_TYPE_DISPLAY, DIFFICULTY_DISPLAY, DIFFICULTY_COLORS } from '@/lib/constants/exercises';
import { Loader2, CheckCircle2, XCircle, Lightbulb, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useQueryClient } from '@tanstack/react-query';

interface ExerciseModalProps {
  exerciseId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExerciseCompleted?: () => void;
}

export function ExerciseModal({
  exerciseId,
  open,
  onOpenChange,
  onExerciseCompleted,
}: ExerciseModalProps) {
  const queryClient = useQueryClient();
  const { exercise, isLoading, error } = useExercise(exerciseId || 0);
  const { submitAnswer, isSubmitting, submitResult } = useSubmitAnswer();
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const startTimeRef = useRef<number>(Date.now());

  // Réinitialiser l'état quand la modal s'ouvre ou l'exercice change
  useEffect(() => {
    if (open && exerciseId) {
      setSelectedAnswer(null);
      setHasSubmitted(false);
      setShowExplanation(false);
      startTimeRef.current = Date.now();
    }
  }, [open, exerciseId]);

  // Mettre à jour l'état quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      setShowExplanation(true);
      
      // Si l'exercice est complété avec succès, invalider et refetch immédiatement la query de progression
      if (submitResult.is_correct) {
        queryClient.invalidateQueries({ queryKey: ['completed-exercises'] });
        queryClient.invalidateQueries({ queryKey: ['exercises'] });
        // Refetch immédiatement pour mettre à jour les badges rapidement
        queryClient.refetchQueries({ queryKey: ['completed-exercises'] });
      }
    }
  }, [submitResult, queryClient]);

  // Fermer la modal après un délai si l'exercice est complété
  useEffect(() => {
    if (hasSubmitted && submitResult) {
      const timer = setTimeout(() => {
        if (onExerciseCompleted) {
          onExerciseCompleted();
        }
        // Fermer automatiquement après 3 secondes (optionnel)
        // onOpenChange(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [hasSubmitted, submitResult, onExerciseCompleted, onOpenChange]);

  const handleSelectAnswer = (answer: string) => {
    if (hasSubmitted) return;
    setSelectedAnswer(answer);
  };

  const handleSubmit = async () => {
    if (!selectedAnswer || !exercise || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000; // en secondes

    try {
      await submitAnswer({
        exercise_id: exercise.id,
        answer: selectedAnswer,
        time_spent: timeSpent,
      });
    } catch (error) {
      // L'erreur est déjà gérée par le hook useSubmitAnswer
      // Ne pas logger en production pour éviter les fuites d'information
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onOpenChange(false);
      // Réinitialiser l'état après fermeture
      setTimeout(() => {
        setSelectedAnswer(null);
        setHasSubmitted(false);
        setShowExplanation(false);
      }, 200);
    }
  };

  if (!exerciseId) {
    return null;
  }

  const difficultyKey = exercise?.difficulty?.toLowerCase() as keyof typeof DIFFICULTY_COLORS;
  const difficultyColor = DIFFICULTY_COLORS[difficultyKey] || DIFFICULTY_COLORS.initie;
  const typeDisplay =
    EXERCISE_TYPE_DISPLAY[exercise?.exercise_type as keyof typeof EXERCISE_TYPE_DISPLAY] ||
    exercise?.exercise_type;
  const difficultyDisplay =
    DIFFICULTY_DISPLAY[exercise?.difficulty?.toLowerCase() as keyof typeof DIFFICULTY_DISPLAY] ||
    exercise?.difficulty;
  const isCorrect = submitResult?.is_correct ?? false;
  const choices = exercise?.choices && exercise.choices.length > 0 ? exercise.choices : [];

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          {isLoading ? (
            <DialogTitle>Chargement de l'exercice...</DialogTitle>
          ) : error ? (
            <DialogTitle>Erreur de chargement</DialogTitle>
          ) : exercise ? (
            <>
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <DialogTitle className="text-xl">{exercise.title}</DialogTitle>
                  <div className="flex gap-2">
                    <Badge variant="outline" className={difficultyColor}>
                      {difficultyDisplay}
                    </Badge>
                    <Badge variant="outline">{typeDisplay}</Badge>
                  </div>
                </div>
              </div>
              <DialogDescription className="text-base mt-3">
                {exercise.question}
              </DialogDescription>
            </>
          ) : (
            <DialogTitle>Exercice</DialogTitle>
          )}
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center min-h-[300px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
              <p className="text-muted-foreground">Chargement de l'exercice...</p>
            </div>
          </div>
        ) : error ? (
          <div className="text-center space-y-4 py-8">
            <XCircle className="h-12 w-12 text-destructive mx-auto" />
            <div>
              <p className="text-muted-foreground mt-2">
                {error.status === 404
                  ? "Cet exercice n'existe pas ou a été supprimé."
                  : error.message || "Impossible de charger l'exercice."}
              </p>
            </div>
          </div>
        ) : exercise ? (
          <>

            <div className="space-y-6 py-4">
              {/* Choix de réponses */}
              {choices.length > 0 ? (
                <div 
                  className="grid grid-cols-2 gap-3"
                  role="radiogroup"
                  aria-label="Choix de réponses pour l'exercice"
                >
                  {choices.map((choice, index) => {
                    const isSelected = selectedAnswer === choice;
                    const isCorrectChoice = choice === exercise.correct_answer;
                    const showCorrect = hasSubmitted && isCorrectChoice;
                    const showIncorrect = hasSubmitted && isSelected && !isCorrectChoice;

                    return (
                      <Button
                        key={index}
                        variant={isSelected ? 'default' : 'outline'}
                        size="lg"
                        className={cn(
                          'h-auto py-4 px-6 text-lg font-medium transition-all',
                          !hasSubmitted && 'hover:bg-primary/10 hover:border-primary/50',
                          showCorrect &&
                            'bg-green-500/20 border-green-500 text-green-400 hover:bg-green-500/20',
                          showIncorrect &&
                            'bg-red-500/20 border-red-500 text-red-400 hover:bg-red-500/20',
                          hasSubmitted && !isSelected && !isCorrectChoice && 'opacity-50'
                        )}
                        onClick={() => handleSelectAnswer(choice)}
                        disabled={hasSubmitted}
                        role="radio"
                        aria-checked={isSelected}
                        aria-label={`Option ${index + 1}: ${choice}${hasSubmitted ? (isCorrectChoice ? ' - Réponse correcte' : (showIncorrect ? ' - Réponse incorrecte' : '')) : ''}`}
                        tabIndex={isSelected ? 0 : -1}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handleSelectAnswer(choice);
                          }
                          // Navigation par flèches
                          if (e.key === 'ArrowRight' && index < choices.length - 1) {
                            e.preventDefault();
                            const nextButton = e.currentTarget.parentElement?.children[index + 1] as HTMLElement;
                            nextButton?.focus();
                          }
                          if (e.key === 'ArrowLeft' && index > 0) {
                            e.preventDefault();
                            const prevButton = e.currentTarget.parentElement?.children[index - 1] as HTMLElement;
                            prevButton?.focus();
                          }
                        }}
                      >
                        {choice}
                      </Button>
                    );
                  })}
                </div>
              ) : (
                <div className="p-4 border rounded-lg bg-muted/50">
                  <p className="text-muted-foreground text-sm">
                    Cet exercice n'a pas de choix multiples. La réponse attendue est :{' '}
                    <strong>{exercise.correct_answer}</strong>
                  </p>
                </div>
              )}

              {/* Bouton de soumission */}
              {!hasSubmitted && (
                <Button
                  onClick={handleSubmit}
                  disabled={!selectedAnswer || isSubmitting}
                  className="w-full"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Enregistrement...
                    </>
                  ) : (
                    'Valider ma réponse'
                  )}
                </Button>
              )}

              {/* Feedback après soumission */}
              {hasSubmitted && submitResult && (
                <div
                  className={cn(
                    'p-4 rounded-lg border-2 transition-all',
                    isCorrect
                      ? 'bg-green-500/10 border-green-500/30 text-green-400'
                      : 'bg-red-500/10 border-red-500/30 text-red-400'
                  )}
                >
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle2 className="h-6 w-6 mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle className="h-6 w-6 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="font-semibold mb-1">
                        {isCorrect ? 'Bravo ! Réponse correcte 🎉' : 'Réponse incorrecte'}
                      </p>
                      {!isCorrect && (
                        <p className="text-sm opacity-90">
                          La bonne réponse était : <strong>{submitResult.correct_answer}</strong>
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Explication */}
              {showExplanation && (exercise.explanation || submitResult?.explanation) && (
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="h-5 w-5 text-primary-on-dark mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-primary-on-dark mb-2">Explication</h4>
                      <p className="text-sm text-text-secondary">
                        {submitResult?.explanation || exercise.explanation}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Indice (si disponible et pas encore soumis) */}
              {!hasSubmitted && exercise.hint && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowExplanation(true)}
                  className="w-full"
                >
                  <Lightbulb className="mr-2 h-4 w-4" />
                  Voir un indice
                </Button>
              )}
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

