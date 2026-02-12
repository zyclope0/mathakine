"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { Exercise } from "@/types/api";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect } from "react";

export function useExercise(exerciseId: number) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();

  // Invalider les queries quand la locale change
  useEffect(() => {
    if (exerciseId > 0) {
      queryClient.invalidateQueries({ queryKey: ["exercise", exerciseId] });
    }
  }, [locale, exerciseId, queryClient]);

  const {
    data: exercise,
    isLoading,
    error,
  } = useQuery<Exercise, ApiClientError>({
    queryKey: ["exercise", exerciseId, locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<Exercise>(`/api/exercises/${exerciseId}`);
    },
    enabled: !!exerciseId && exerciseId > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    exercise,
    isLoading,
    error,
  };
}
