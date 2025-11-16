'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';
import { toast } from 'sonner';

export interface SubmitAnswerPayload {
  exercise_id: number;
  answer: string;
  time_spent?: number;
}

export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
  attempt_id?: number;
  new_badges?: Array<{
    id: number;
    name: string;
    star_wars_title?: string;
    points_reward: number;
  }>;
  badges_earned?: number;
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();

  const submitMutation = useMutation<SubmitAnswerResponse, ApiClientError, SubmitAnswerPayload>({
    mutationFn: async (payload) => {
      return api.post<SubmitAnswerResponse>('/api/submit-answer', payload);
    },
    onSuccess: (data, variables) => {
      // Invalider le cache de l'exercice pour recharger les stats
      queryClient.invalidateQueries({ queryKey: ['exercise', variables.exercise_id] });
      queryClient.invalidateQueries({ queryKey: ['exercises'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'stats'] });
      
      // Si la réponse est correcte, invalider et refetch immédiatement la query de progression
      if (data.is_correct) {
        queryClient.invalidateQueries({ queryKey: ['completed-exercises'] });
        // Refetch immédiatement pour mettre à jour les badges rapidement
        queryClient.refetchQueries({ queryKey: ['completed-exercises'] });
      }
      
      // Afficher les badges gagnés si présents
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          toast.success(`Badge débloqué ! 🎖️`, {
            description: `${badge.name}${badge.star_wars_title ? ` - ${badge.star_wars_title}` : ''}`,
            duration: 5000,
          });
        });
      }
    },
    onError: (error: ApiClientError) => {
      toast.error('Erreur', {
        description: error.message || 'Impossible d\'enregistrer votre réponse.',
      });
    },
  });

  return {
    submitAnswer: submitMutation.mutateAsync,
    isSubmitting: submitMutation.isPending,
    submitResult: submitMutation.data,
  };
}

