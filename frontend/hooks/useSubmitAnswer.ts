"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { trackFirstAttempt } from "@/lib/analytics/edtech";
import { readBadgeThematicTitleRaw } from "@/lib/gamification/badgeThematicTitle";

export interface SubmitAnswerPayload {
  exercise_id: number;
  answer: string;
  time_spent?: number;
  analytics_type?: "exercise" | "challenge" | "interleaved";
}

export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
  attempt_id?: number;
  new_badges?: Array<{
    id: number;
    name: string;
    /** Cle publique preferee (F43-A4) - meme valeur que `star_wars_title`. */
    thematic_title?: string | null;
    /** @deprecated F43-A4 - compat ; preferer `thematic_title`. */
    star_wars_title?: string | null;
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
      void exercise_id; // exclu de dataToSend, utilisé via payload.exercise_id
      return api.post<SubmitAnswerResponse>(`/api/exercises/${exerciseId}/attempt`, dataToSend);
    },
    onSuccess: (data, variables) => {
      trackFirstAttempt(variables.analytics_type ?? "exercise", variables.exercise_id);

      // Invalider le cache de l'exercice pour recharger les stats
      queryClient.invalidateQueries({ queryKey: ["exercise", variables.exercise_id] });
      // Ne PAS invalider ["exercises"] : évite le reshuffle aléatoire au rafraîchissement.
      // Le badge "Résolu" vient de completed-exercises, pas de la liste.
      queryClient.invalidateQueries({ queryKey: ["user", "stats"] });

      // Si la réponse est correcte, invalider et refetch la progression + badges + recommandations + défis quotidiens
      if (data.is_correct) {
        queryClient.invalidateQueries({ queryKey: ["completed-exercises"] });
        queryClient.refetchQueries({ queryKey: ["completed-exercises"] });
        queryClient.invalidateQueries({ queryKey: ["badges"] });
        queryClient.invalidateQueries({ queryKey: ["user", "progress"] });
        queryClient.invalidateQueries({ queryKey: ["recommendations"] });
        queryClient.invalidateQueries({ queryKey: ["daily-challenges"] });
      }

      // Afficher les badges gagnés si présents
      if (data.new_badges && data.new_badges.length > 0) {
        data.new_badges.forEach((badge) => {
          const subtitle = readBadgeThematicTitleRaw(badge);
          toast.success(t("badges.badgeUnlocked"), {
            description: `${badge.name}${subtitle ? ` - ${subtitle}` : ""}`,
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
