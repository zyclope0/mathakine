'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, ApiClientError } from '@/lib/api/client';
import type { Exercise, PaginatedResponse } from '@/types/api';
import { toast } from 'sonner';
import { useLocaleStore } from '@/lib/stores/localeStore';
import { useEffect } from 'react';
import { debugLog } from '@/lib/utils/debug';

export interface ExerciseFilters {
  exercise_type?: string;
  difficulty?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

interface GenerateExerciseParams {
  exercise_type: string;
  difficulty: string;
  save?: boolean;
}

export function useExercises(filters?: ExerciseFilters) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();

  // Invalider les queries quand la locale change (mais ne pas refetch automatiquement)
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['exercises'] });
  }, [locale, queryClient]);

  // Liste des exercices avec pagination
  const { data: paginatedResponse, isLoading, error } = useQuery<PaginatedResponse<Exercise>>({
    queryKey: ['exercises', filters, locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.exercise_type) params.append('exercise_type', filters.exercise_type);
      if (filters?.difficulty) params.append('difficulty', filters.difficulty);
      if (filters?.search) params.append('search', filters.search);
      if (filters?.skip) params.append('skip', filters.skip.toString());
      if (filters?.limit) params.append('limit', filters.limit.toString());

      const queryString = params.toString();
      const endpoint = `/api/exercises${queryString ? `?${queryString}` : ''}`;
      
      debugLog('[useExercises] Fetching exercises from:', endpoint);
      const result = await api.get<PaginatedResponse<Exercise>>(endpoint);
      debugLog('[useExercises] Received exercises:', result?.items?.length || 0, 'total:', result?.total || 0);
      return result;
    },
    staleTime: 30 * 1000, // 30 secondes
    // Optimiser refetchOnMount : seulement si les données sont stale ou absentes
    refetchOnMount: true, // Refetch si stale, mais utiliser le cache si frais
    refetchOnWindowFocus: false, // Ne pas refetch au focus pour éviter les requêtes inutiles
    retry: 2, // Réessayer 2 fois en cas d'erreur
  });
  
  // Extraire les exercices et métadonnées de pagination
  const exercises = paginatedResponse?.items || [];
  const total = paginatedResponse?.total || 0;
  const hasMore = paginatedResponse?.hasMore || false;

  // Note: Pour récupérer un exercice spécifique, utiliser le hook useExercise(id) séparé

  // Générer un exercice standard
  const generateMutation = useMutation({
    mutationFn: async (params: GenerateExerciseParams) => {
      return await api.post<Exercise>('/api/exercises/generate', params);
    },
    onSuccess: async (data) => {
      // Invalider ET refetch immédiatement pour afficher le nouvel exercice
      // Utiliser la même queryKey que la query principale pour respecter les filtres
      await queryClient.invalidateQueries({ queryKey: ['exercises'] });
      // Le refetch se fera automatiquement grâce à refetchOnMount: 'always'
      toast.success('Exercice généré !', {
        description: `Exercice "${data.title}" créé avec succès.`,
      });
    },
    onError: (error: ApiClientError) => {
      toast.error('Erreur de génération', {
        description: error.message || 'Impossible de générer l\'exercice',
      });
    },
  });

  return {
    exercises,
    total,
    hasMore,
    isLoading,
    error,
    generateExercise: generateMutation.mutate,
    generateExerciseAsync: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
  };
}

