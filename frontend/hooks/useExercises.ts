"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { Exercise, PaginatedResponse } from "@/types/api";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect } from "react";
import { debugLog } from "@/lib/utils/debug";

export interface ExerciseFilters {
  exercise_type?: string;
  age_group?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

interface GenerateExerciseParams {
  exercise_type: string;
  age_group: string;
  save?: boolean;
}

export function useExercises(filters?: ExerciseFilters) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();
  const t = useTranslations("toasts");

  // Invalider les queries quand la locale change (mais ne pas refetch automatiquement)
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ["exercises"] });
  }, [locale, queryClient]);

  // Liste des exercices avec pagination
  // Utiliser une queryKey explicite pour garantir que les changements de pagination déclenchent un refetch
  const {
    data: paginatedResponse,
    isLoading,
    error,
    isFetching,
  } = useQuery<PaginatedResponse<Exercise>>({
    queryKey: [
      "exercises",
      filters?.skip ?? 0,
      filters?.limit ?? 15,
      filters?.exercise_type ?? null,
      filters?.age_group ?? null,
      filters?.search ?? null,
      locale,
    ],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.exercise_type) params.append("exercise_type", filters.exercise_type);
      if (filters?.age_group) params.append("age_group", filters.age_group);
      if (filters?.search) params.append("search", filters.search);
      // Toujours envoyer skip et limit pour la pagination
      params.append("skip", (filters?.skip ?? 0).toString());
      params.append("limit", (filters?.limit ?? 15).toString());

      const queryString = params.toString();
      const endpoint = `/api/exercises?${queryString}`;

      debugLog("[useExercises] Fetching exercises from:", endpoint);
      const result = await api.get<PaginatedResponse<Exercise>>(endpoint);
      debugLog(
        "[useExercises] Received exercises:",
        result?.items?.length || 0,
        "total:",
        result?.total || 0
      );
      return result;
    },
    staleTime: 10 * 1000, // 10 secondes (réduit pour pagination plus réactive)
    gcTime: 5 * 60 * 1000, // Garder en cache 5 minutes
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    retry: 2,
  });

  // Extraire les exercices et métadonnées de pagination
  const exercises = paginatedResponse?.items || [];
  const total = paginatedResponse?.total || 0;
  const hasMore = paginatedResponse?.hasMore || false;

  // Note: Pour récupérer un exercice spécifique, utiliser le hook useExercise(id) séparé

  // Générer un exercice standard
  const generateMutation = useMutation({
    mutationFn: async (params: GenerateExerciseParams) => {
      return await api.post<Exercise>("/api/exercises/generate", params);
    },
    onSuccess: async (data) => {
      // Invalider ET refetch immédiatement pour afficher le nouvel exercice
      // Utiliser la même queryKey que la query principale pour respecter les filtres
      await queryClient.invalidateQueries({ queryKey: ["exercises"] });
      // Le refetch se fera automatiquement grâce à refetchOnMount: 'always'
      toast.success(t("exercises.generateSuccess"), {
        description: t("exercises.generateSuccessDescription", { title: data.title }),
      });
    },
    onError: (error: ApiClientError) => {
      toast.error(t("exercises.generateError"), {
        description: error.message || t("exercises.generateErrorDescription"),
      });
    },
  });

  return {
    exercises,
    total,
    hasMore,
    isLoading,
    isFetching, // Utile pour afficher un indicateur pendant la pagination
    error,
    generateExercise: generateMutation.mutate,
    generateExerciseAsync: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
  };
}
