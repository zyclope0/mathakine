"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type {
  Challenge,
  ChallengeAttemptResponse,
} from "@/types/api";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { ChallengeType, AgeGroup } from "@/lib/constants/challenges";
import { usePaginatedContent } from "./usePaginatedContent";

export interface ChallengeFilters {
  challenge_type?: ChallengeType;
  age_group?: AgeGroup;
  search?: string;
  skip?: number;
  limit?: number;
  order?: "random" | "recent";
  hide_completed?: boolean;
}

export interface SubmitChallengeAnswerPayload {
  challenge_id: number;
  answer: string;
  time_spent?: number;
  hints_used?: number[];
}

export function useChallenges(filters?: ChallengeFilters) {
  const queryClient = useQueryClient();
  const t = useTranslations("toasts");
  const [hints, setHints] = useState<string[]>([]);

  const {
    items: challenges,
    total,
    hasMore,
    isLoading,
    isFetching,
    error,
  } = usePaginatedContent<Challenge>(filters as Record<string, string | number | null | undefined> | undefined, {
    endpoint: "/api/challenges",
    queryKey: "challenges",
    paramKeys: {
      challenge_type: "challenge_type",
      age_group: "age_group",
      order: "order",
      hide_completed: "hide_completed",
    },
    fixedParams: { active_only: "true" },
    staleTime: 30 * 1000,
  });

  // Note: Pour récupérer un défi spécifique, utiliser le hook useChallenge(id) séparé

  // Soumettre une réponse à un défi
  const submitAnswerMutation = useMutation<
    ChallengeAttemptResponse,
    ApiClientError,
    SubmitChallengeAnswerPayload
  >({
    mutationFn: async (payload) => {
      return api.post<ChallengeAttemptResponse>(`/api/challenges/${payload.challenge_id}/attempt`, {
        user_solution: payload.answer,
        time_spent: payload.time_spent,
        hints_used: payload.hints_used || [],
      });
    },
    onSuccess: (data, variables) => {
      // Invalider le cache du défi pour recharger les stats
      queryClient.invalidateQueries({ queryKey: ["challenge", variables.challenge_id] });
      queryClient.invalidateQueries({ queryKey: ["challenges"] });
      queryClient.invalidateQueries({ queryKey: ["user", "stats"] });

      // Si la réponse est correcte, invalider et refetch la progression + badges
      if (data.is_correct) {
        queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
        queryClient.refetchQueries({ queryKey: ["completed-challenges"] });
        queryClient.invalidateQueries({ queryKey: ["badges"] });
        queryClient.invalidateQueries({ queryKey: ["user", "progress"] });
      }

      // Afficher les badges gagnés si présents
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          toast.success(t("badges.badgeUnlocked"), {
            description: `${badge.name}${badge.star_wars_title ? ` - ${badge.star_wars_title}` : ""}`,
            duration: 5000,
          });
        });
      } else if (data.progress_notification && data.progress_notification.remaining > 0) {
        toast.info(t("badges.progressNotification"), {
          description: t("badges.progressNotificationDesc", {
            name: data.progress_notification.name,
            count: data.progress_notification.remaining,
          }),
          duration: 4000,
        });
      }
    },
    onError: (error: ApiClientError) => {
      toast.error(t("challenges.submitError"), {
        description: error.message || t("challenges.submitErrorDescription"),
      });
    },
  });

  // Récupérer un indice pour un défi
  const getHintMutation = useMutation<string[], ApiClientError, number>({
    mutationFn: async (challengeId: number) => {
      // Récupérer le niveau d'indice suivant (basé sur le nombre d'indices déjà utilisés)
      const currentLevel = hints.length;
      const nextLevel = currentLevel + 1;
      const response = await api.get<{ hint: string }>(
        `/api/challenges/${challengeId}/hint?level=${nextLevel}`
      );
      // Le backend retourne un seul indice {hint: "..."}, on l'accumule dans le tableau existant
      if (response.hint) {
        return [...hints, response.hint];
      }
      return hints;
    },
    onSuccess: (newHints) => {
      // Mettre à jour les indices disponibles
      setHints(newHints);
    },
    onError: (error: ApiClientError) => {
      toast.error(t("challenges.hintError"), {
        description: error.message || t("challenges.hintErrorDescription"),
      });
    },
  });

  return {
    challenges,
    total,
    hasMore,
    isLoading,
    isFetching, // Ajouté pour indicateur de chargement pendant pagination
    error,
    submitAnswer: submitAnswerMutation.mutateAsync,
    isSubmitting: submitAnswerMutation.isPending,
    submitResult: submitAnswerMutation.data,
    getHint: getHintMutation.mutateAsync,
    isGettingHint: getHintMutation.isPending,
    hints,
    setHints,
  };
}
