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
