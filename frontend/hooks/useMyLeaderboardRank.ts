"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { LeaderboardPeriod } from "@/hooks/useLeaderboard";

export interface MyLeaderboardRankResponse {
  rank: number;
  total_points: number;
}

/**
 * Rang par points (GET /api/users/me/rank), même paramètre ``period`` que le classement.
 * À n'activer que lorsque l'utilisateur n'apparaît pas dans le top affiché.
 */
export function useMyLeaderboardRank(enabled: boolean, period: LeaderboardPeriod = "all") {
  const params = new URLSearchParams({ period });

  return useQuery<MyLeaderboardRankResponse, ApiClientError>({
    queryKey: ["leaderboard", "me", "rank", period],
    queryFn: async () => api.get<MyLeaderboardRankResponse>(`/api/users/me/rank?${params}`),
    enabled,
    staleTime: 60 * 1000,
  });
}
