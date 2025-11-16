'use client';

import { useQuery } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';
import { debugLog } from '@/lib/utils/debug';

/**
 * Hook pour récupérer les IDs d'exercices complétés par l'utilisateur actuel
 */
export function useCompletedExercises() {
  const { data, isLoading, error } = useQuery<number[], ApiClientError>({
    queryKey: ['completed-exercises'],
    queryFn: async () => {
      try {
        const result = await api.get<{ completed_ids: number[] }>('/api/exercises/completed-ids');
        debugLog('[useCompletedExercises] Received completed exercise IDs:', result?.completed_ids?.length || 0);
        return result?.completed_ids || [];
      } catch (error) {
        // Si l'utilisateur n'est pas authentifié, retourner un tableau vide
        if (error instanceof ApiClientError && error.status === 401) {
          return [];
        }
        throw error;
      }
    },
    staleTime: 0, // Toujours considérer comme stale pour refetch immédiat après invalidation
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  return {
    completedIds: data || [],
    isLoading,
    error,
    isCompleted: (exerciseId: number) => (data || []).includes(exerciseId),
  };
}

/**
 * Hook pour récupérer les IDs de challenges complétés par l'utilisateur actuel
 */
export function useCompletedChallenges() {
  const { data, isLoading, error } = useQuery<number[], ApiClientError>({
    queryKey: ['completed-challenges'],
    queryFn: async () => {
      try {
        const result = await api.get<{ completed_ids: number[] }>('/api/challenges/completed-ids');
        debugLog('[useCompletedChallenges] Received completed challenge IDs:', result?.completed_ids?.length || 0);
        return result?.completed_ids || [];
      } catch (error) {
        // Si l'utilisateur n'est pas authentifié, retourner un tableau vide
        if (error instanceof ApiClientError && error.status === 401) {
          return [];
        }
        throw error;
      }
    },
    staleTime: 0, // Toujours considérer comme stale pour refetch immédiat après invalidation
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  return {
    completedIds: data || [],
    isLoading,
    error,
    isCompleted: (challengeId: number) => (data || []).includes(challengeId),
  };
}

