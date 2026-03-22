"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { Exercise } from "@/types/api";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { usePaginatedContent } from "./usePaginatedContent";
import type { ContentListOrder } from "@/lib/constants/contentListOrder";

export interface ExerciseFilters {
  exercise_type?: string;
  age_group?: string;
  search?: string;
  skip?: number;
  limit?: number;
  order?: ContentListOrder;
  hide_completed?: boolean;
}

interface GenerateExerciseParams {
  exercise_type: string;
  age_group: string;
  save?: boolean;
}

export function useExercises(filters?: ExerciseFilters) {
  const queryClient = useQueryClient();
  const t = useTranslations("toasts");

  const {
    items: exercises,
    total,
    hasMore,
    isLoading,
    isFetching,
    error,
  } = usePaginatedContent<Exercise>(
    filters as Record<string, string | number | null | undefined> | undefined,
    {
      endpoint: "/api/exercises",
      queryKey: "exercises",
      paramKeys: {
        exercise_type: "exercise_type",
        age_group: "age_group",
        order: "order",
        hide_completed: "hide_completed",
      },
      staleTime: 10 * 1000,
    }
  );

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
      // Refetch déclenché par invalidation (liste à jour après génération)
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
    /** Fire-and-forget ; le résultat n’est pas remonté au caller. */
    generateExercise: generateMutation.mutate,
    /** À utiliser quand le caller doit réagir au payload (ex. CTA après création). */
    generateExerciseAsync: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
  };
}
