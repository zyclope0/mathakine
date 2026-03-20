"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

type RecommendationOpenResponse = {
  id: number;
  clicked_count: number;
  last_clicked_at: string | null;
};

export interface Recommendation {
  id: number;
  exercise_type: string;
  difficulty: string;
  age_group?: string;
  reason: string;
  /** R5 — clé stable i18n ; si absente, afficher ``reason`` */
  reason_code?: string;
  reason_params?: Record<string, string | number | boolean | null | undefined>;
  priority?: number;
  exercise_title?: string;
  exercise_question?: string;
  exercise_id?: number;
  challenge_id?: number;
  challenge_title?: string;
  recommendation_type?: "exercise" | "challenge";
}

/**
 * R5 / R6 — Traduction depuis reason_code + reason_params, sinon fallback ``reason``.
 */
export function formatRecommendationReasonDisplay(
  rec: Pick<Recommendation, "reason" | "reason_code" | "reason_params">,
  t: (key: string, values?: Record<string, string | number>) => string,
  getExerciseTypeLabel?: (canonicalType: string) => string
): string {
  const code = rec.reason_code;
  if (code) {
    const msgKey = code.replace(/\./g, "_");
    const params = rec.reason_params ?? {};
    const base = { default: rec.reason ?? "" } as Record<string, string | number>;

    if (code.startsWith("reco.challenge.")) {
      const rawType = typeof params.challenge_type === "string" ? params.challenge_type : "custom";
      const challengeTypeLabel = t(`challengeTypes.${rawType}`, { default: rawType });
      return t(`codes.${msgKey}`, {
        ...base,
        challengeType: challengeTypeLabel,
      });
    }

    if (code.startsWith("reco.exercise.")) {
      const rawEt = typeof params.exercise_type === "string" ? params.exercise_type : "";
      const exerciseType = getExerciseTypeLabel ? getExerciseTypeLabel(rawEt) : rawEt;
      const values: Record<string, string | number> = { ...base, exerciseType };
      if (params.success_rate !== undefined && params.success_rate !== null) {
        values.successRate = Number(params.success_rate);
      }
      const td = params.target_difficulty;
      if (typeof td === "string" && td) {
        values.targetDifficulty = t(`difficulties.${td}`, { default: td });
      }
      const nd = params.next_difficulty;
      if (typeof nd === "string" && nd) {
        values.nextDifficulty = t(`difficulties.${nd}`, { default: nd });
      }
      return t(`codes.${msgKey}`, values);
    }

    return t(`codes.${msgKey}`, base);
  }
  return rec.reason ?? "";
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

  const openMutation = useMutation({
    mutationFn: async (recommendationId: number) => {
      const body = { recommendation_id: recommendationId };
      try {
        return await api.post<RecommendationOpenResponse>("/api/recommendations/open", body);
      } catch (e) {
        // Backend non redemarre ou path filtre : replie sur l'alias `/clicked`
        if (e instanceof ApiClientError && e.status === 404) {
          return await api.post<RecommendationOpenResponse>("/api/recommendations/clicked", body);
        }
        throw e;
      }
    },
    // Pas d'invalidation agressive : évite boucles refetch ; le clic est un signal R4 ponctuel
  });

  const completeMutation = useMutation({
    mutationFn: async (recommendationId: number) => {
      return await api.post<{
        message: string;
        id: number;
        verified_by_attempt?: boolean;
        completion_kind?: string;
      }>("/api/recommendations/complete", {
        recommendation_id: recommendationId,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      toast.success(t("completedSuccess", { default: "Marqué comme fait" }));
    },
    onError: (error: ApiClientError) => {
      toast.error(error.message || t("updateErrorDescription"));
    },
  });

  return {
    recommendations: recommendations || [],
    isLoading,
    error,
    generate: generateMutation.mutateAsync,
    isGenerating: generateMutation.isPending,
    complete: completeMutation.mutateAsync,
    isCompleting: completeMutation.isPending,
    recordOpen: openMutation.mutateAsync,
    isRecordingOpen: openMutation.isPending,
  };
}
