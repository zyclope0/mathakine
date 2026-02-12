"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type {
  Challenge,
  ChallengeAttemptResponse,
  ChallengesPaginatedResponse,
  ChallengeFiltersWithSearch,
} from "@/types/api";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { ChallengeType, AgeGroup } from "@/lib/constants/challenges";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { debugLog } from "@/lib/utils/debug";

export interface ChallengeFilters {
  challenge_type?: ChallengeType;
  age_group?: AgeGroup;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface SubmitChallengeAnswerPayload {
  challenge_id: number;
  answer: string;
  time_spent?: number;
  hints_used?: number[];
}

export function useChallenges(filters?: ChallengeFilters) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();
  const t = useTranslations("toasts");
  const [hints, setHints] = useState<string[]>([]);

  // Invalider les queries quand la locale change
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ["challenges"] });
  }, [locale, queryClient]);

  // Liste des défis logiques avec pagination
  // Utiliser des valeurs primitives explicites dans queryKey pour une meilleure détection des changements
  const {
    data: paginatedData,
    isLoading,
    isFetching,
    error,
  } = useQuery<ChallengesPaginatedResponse, ApiClientError>({
    queryKey: [
      "challenges",
      filters?.skip ?? 0,
      filters?.limit ?? 15,
      filters?.challenge_type ?? null,
      filters?.age_group ?? null,
      filters?.search ?? null,
      locale,
    ],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.challenge_type) params.append("challenge_type", filters.challenge_type);
      if (filters?.age_group) params.append("age_group", filters.age_group);
      if (filters?.search) params.append("search", filters.search);
      // Toujours envoyer skip et limit pour garantir la pagination
      params.append("skip", (filters?.skip ?? 0).toString());
      params.append("limit", (filters?.limit ?? 15).toString());
      params.append("active_only", "true");

      const queryString = params.toString();
      const endpoint = `/api/challenges${queryString ? `?${queryString}` : ""}`;

      debugLog("[useChallenges] Fetching challenges from:", endpoint);
      const result = await api.get<ChallengesPaginatedResponse>(endpoint);
      debugLog(
        "[useChallenges] Received challenges:",
        result?.items?.length || 0,
        "total:",
        result?.total || 0
      );
      return result;
    },
    staleTime: 30 * 1000, // 30 secondes (cohérent avec useChallenge)
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    retry: 2,
  });

  // Extraire les données paginées
  const challenges = paginatedData?.items || [];
  const total = paginatedData?.total || 0;
  const hasMore = paginatedData?.hasMore || false;

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

      // Si la réponse est correcte, invalider et refetch immédiatement la query de progression
      if (data.is_correct) {
        queryClient.invalidateQueries({ queryKey: ["completed-challenges"] });
        // Refetch immédiatement pour mettre à jour les badges rapidement
        queryClient.refetchQueries({ queryKey: ["completed-challenges"] });
      }

      // Afficher les badges gagnés si présents
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          toast.success(t("badges.badgeUnlocked"), {
            description: `${badge.name}${badge.star_wars_title ? ` - ${badge.star_wars_title}` : ""}`,
            duration: 5000,
          });
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
