"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface LeaderboardEntry {
  rank: number;
  username: string;
  total_points: number;
  current_level: number;
  jedi_rank: string;
  is_current_user: boolean;
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[];
}

export function useLeaderboard(limit = 50, ageGroup?: string | null) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (ageGroup) params.set("age_group", ageGroup);

  const { data, isLoading, error, refetch } = useQuery<LeaderboardResponse, ApiClientError>({
    queryKey: ["leaderboard", limit, ageGroup ?? "all"],
    queryFn: async () => {
      return await api.get<LeaderboardResponse>(`/api/users/leaderboard?${params}`);
    },
    staleTime: 60 * 1000,
  });

  return {
    leaderboard: data?.leaderboard ?? [],
    isLoading,
    error,
    refetch,
  };
}
