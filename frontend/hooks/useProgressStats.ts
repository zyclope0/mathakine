import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

export interface ProgressByCategory {
  completed: number;
  accuracy: number;
}

export interface ProgressStats {
  total_attempts: number;
  correct_attempts: number;
  accuracy: number;
  average_time: number;
  exercises_completed: number;
  highest_streak: number;
  current_streak: number;
  by_category: Record<string, ProgressByCategory>;
}

/**
 * Hook pour récupérer les statistiques de progression de l'utilisateur (exercices uniquement)
 */
export function useProgressStats() {
  return useQuery<ProgressStats>({
    queryKey: ['user', 'progress'],
    queryFn: async () => {
      return await api.get<ProgressStats>('/api/users/me/progress');
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: true,
  });
}
