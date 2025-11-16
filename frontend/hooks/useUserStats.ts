'use client';

import { useQuery } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';
import { safeValidateUserStats, type UserStats } from '@/lib/validations/dashboard';

export type { UserStats };

export type TimeRange = '7' | '30' | '90' | 'all';

export function useUserStats(timeRange: TimeRange = '30') {
  const { data: rawStats, isLoading, error, refetch } = useQuery<UserStats | null, ApiClientError>({
    queryKey: ['user', 'stats', timeRange],
    queryFn: async () => {
      const rawData = await api.get<unknown>(`/api/users/stats?timeRange=${timeRange}`);
      
      // Valider et normaliser les données avec Zod
      const validatedStats = safeValidateUserStats(rawData);
      
      if (!validatedStats) {
        // Si la validation échoue, retourner null pour déclencher l'état d'erreur
        throw new Error('Données de statistiques invalides');
      }
      
      return validatedStats;
    },
    staleTime: 30 * 1000, // 30 secondes
    refetchOnWindowFocus: true,
    retry: 1, // Réessayer une fois en cas d'erreur
  });

  return {
    stats: rawStats ?? null,
    isLoading,
    error,
    refetch,
  };
}

