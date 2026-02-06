'use client';

import { useQuery } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';

/**
 * Types pour les statistiques globales de l'Académie
 */
export interface AcademyStatistics {
  total_exercises: number;
  total_challenges: number;
  total_content: number;
  archived_exercises: number;
  ai_generated: number;
  ai_generated_exercises: number;
  ai_generated_challenges: number;
  ai_generated_percentage: number;
}

export interface DisciplineData {
  count: number;
  discipline_name: string;
  percentage: number;
}

export interface RankData {
  count: number;
  rank_name: string;
  description: string;
  min_age: number;
  percentage: number;
}

export interface ApprenticeGroupData {
  count: number;
  group_name: string;
  description: string;
  percentage: number;
}

export interface GlobalPerformance {
  total_attempts: number;
  exercise_attempts: number;
  challenge_attempts: number;
  successful_attempts: number;
  mastery_rate: number;
  challenge_mastery_rate: number;
  message: string;
}

export interface LegendaryChallenge {
  id: number;
  title: string;
  discipline: string;
  rank: string;
  apprentices_trained: number;
}

export interface AcademyStats {
  archive_status: string;
  academy_statistics: AcademyStatistics;
  by_discipline: Record<string, DisciplineData>;
  by_rank: Record<string, RankData>;
  by_apprentice_group: Record<string, ApprenticeGroupData>;
  global_performance: GlobalPerformance;
  legendary_challenges: LegendaryChallenge[];
  sage_wisdom: string;
}

/**
 * Hook pour récupérer les statistiques globales de l'Académie
 * 
 * Endpoint: GET /api/exercises/stats
 * 
 * Ces stats sont publiques et ne nécessitent pas d'authentification.
 * Elles représentent les statistiques globales de tous les exercices,
 * pas les stats personnelles d'un utilisateur.
 */
export function useAcademyStats() {
  const { data, isLoading, error, refetch } = useQuery<AcademyStats | null, ApiClientError>({
    queryKey: ['academy', 'stats'],
    queryFn: async () => {
      try {
        const response = await api.get<AcademyStats>('/api/exercises/stats');
        return response;
      } catch (err) {
        // En cas d'erreur, retourner null plutôt que de bloquer l'UI
        console.error('Erreur lors de la récupération des stats de l\'Académie:', err);
        return null;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (données peu changeantes)
    refetchOnWindowFocus: false, // Pas besoin de rafraîchir à chaque focus
    retry: 1,
  });

  return {
    stats: data ?? null,
    isLoading,
    error,
    refetch,
  };
}
