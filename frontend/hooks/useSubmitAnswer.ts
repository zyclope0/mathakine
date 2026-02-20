"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

export interface SubmitAnswerPayload {
  exercise_id: number;
  answer: string;
  time_spent?: number;
}

export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
  attempt_id?: number;
  new_badges?: Array<{
    id: number;
    name: string;
    star_wars_title?: string;
    points_reward: number;
  }>;
  badges_earned?: number;
  progress_notification?: { name: string; remaining: number };
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();
  const t = useTranslations("toasts");

  const submitMutation = useMutation<SubmitAnswerResponse, ApiClientError, SubmitAnswerPayload>({
    mutationFn: async (payload) => {
      const exerciseId = payload.exercise_id;
      // Remove exercise_id from payload as it's now in the URL path
      const { exercise_id, ...dataToSend } = payload;
      return api.post<SubmitAnswerResponse>(`/api/exercises/${exerciseId}/attempt`, dataToSend);
    },
    onSuccess: (data, variables) => {
      // Invalider le cache de l'exercice pour recharger les stats
      queryClient.invalidateQueries({ queryKey: ["exercise", variables.exercise_id] });
      // Ne PAS invalider ["exercises"] : évite le reshuffle aléatoire au rafraîchissement.
      // Le badge "Résolu" vient de completed-exercises, pas de la liste.
      queryClient.invalidateQueries({ queryKey: ["user", "stats"] });

      // Si la réponse est correcte, invalider et refetch la progression + badges
      if (data.is_correct) {
        queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
        queryClient.refetchQueries({ queryKey: ["completed-exercises"] });
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
      toast.error(t("generic.submitError"), {
        description: error.message || t("generic.submitErrorDescription"),
      });
    },
  });

  return {
    submitAnswer: submitMutation.mutateAsync,
    isSubmitting: submitMutation.isPending,
    submitResult: submitMutation.data,
  };
}
