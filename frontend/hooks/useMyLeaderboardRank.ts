"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface MyLeaderboardRankResponse {
  rank: number;
  total_points: number;
}

/**
 * Rang global par points (GET /api/users/me/rank).
 * À n'activer que lorsque l'utilisateur n'apparaît pas dans le top leaderboard affiché.
 */
export function useMyLeaderboardRank(enabled: boolean) {
  return useQuery<MyLeaderboardRankResponse, ApiClientError>({
    queryKey: ["leaderboard", "me", "rank"],
    queryFn: async () => api.get<MyLeaderboardRankResponse>("/api/users/me/rank"),
    enabled,
    staleTime: 60 * 1000,
  });
}
