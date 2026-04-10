"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type ApiClientError } from "@/lib/api/client";
import type { Exercise } from "@/types/api";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect } from "react";

interface UseExerciseOptions {
  enabled?: boolean;
}

export function useExercise(exerciseId: number, options?: UseExerciseOptions) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();
  const enabled = options?.enabled ?? true;

  // Invalider les queries quand la locale change
  useEffect(() => {
    if (enabled && exerciseId > 0) {
      void queryClient.invalidateQueries({ queryKey: ["exercise", exerciseId] });
    }
  }, [locale, exerciseId, queryClient, enabled]);

  const {
    data: exercise,
    isLoading,
    error,
  } = useQuery<Exercise, ApiClientError>({
    queryKey: ["exercise", exerciseId, locale], // Inclure la locale dans la queryKey
    queryFn: async () => {
      return await api.get<Exercise>(`/api/exercises/${exerciseId}`);
    },
    enabled: enabled && !!exerciseId && exerciseId > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    exercise,
    isLoading,
    error,
  };
}
