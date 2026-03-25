import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface ChallengeProgressDetail {
  id: number;
  title: string;
  is_completed: boolean;
  attempts: number;
  best_time: number | null;
}

export interface ChallengesProgress {
  completed_challenges: number;
  total_challenges: number;
  success_rate: number;
  average_time: number;
  challenges: ChallengeProgressDetail[];
}

/** Ligne agrégée par type de défi (table challenge_progress, lot C3). */
export interface ChallengeProgressByTypeRow {
  id: number;
  user_id: number;
  challenge_type: string;
  total_attempts: number;
  correct_attempts: number;
  completion_rate: number;
  mastery_level: string;
  last_attempted_at: string | null;
}

export interface ChallengesDetailedProgressResponse {
  items: ChallengeProgressByTypeRow[];
}

/**
 * Hook pour récupérer la progression des défis logiques de l'utilisateur
 */
export function useChallengesProgress() {
  return useQuery<ChallengesProgress>({
    queryKey: ["user", "challenges", "progress"],
    queryFn: async () => {
      return await api.get<ChallengesProgress>("/api/users/me/challenges/progress");
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: true,
  });
}

/**
 * Hook pour la maîtrise par type (challenge_progress) — complète useChallengesProgress.
 */
export function useChallengesDetailedProgress() {
  return useQuery<ChallengesDetailedProgressResponse>({
    queryKey: ["user", "challenges", "detailed-progress"],
    queryFn: async () => {
      return await api.get<ChallengesDetailedProgressResponse>(
        "/api/users/me/challenges/detailed-progress"
      );
    },
    staleTime: 1000 * 60 * 2,
    refetchOnWindowFocus: true,
  });
}
