"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

export interface Recommendation {
  id: number;
  exercise_type: string;
  difficulty: string;
  age_group?: string;
  reason: string;
  exercise_title?: string;
  exercise_question?: string;
  exercise_id?: number;
}

export function useRecommendations() {
  const queryClient = useQueryClient();
  const t = useTranslations("toasts.recommendations");

  const {
    data: recommendations,
    isLoading,
    error,
  } = useQuery<Recommendation[], ApiClientError>({
    queryKey: ["recommendations"],
    queryFn: async () => {
      return await api.get<Recommendation[]>("/api/recommendations");
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      return await api.post("/api/recommendations/generate");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      toast.success(t("updatedSuccess"));
    },
    onError: (error: ApiClientError) => {
      toast.error(t("updateError"), {
        description: error.message || t("updateErrorDescription"),
      });
    },
  });

  return {
    recommendations: recommendations || [],
    isLoading,
    error,
    generate: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
  };
}
