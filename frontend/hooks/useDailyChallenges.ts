"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type ApiClientError } from "@/lib/api/client";
import type { DailyChallenge, DailyChallengesResponse } from "@/types/api";

export function useDailyChallenges() {
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery<DailyChallenge[], ApiClientError>({
    queryKey: ["daily-challenges"],
    queryFn: async () => {
      const res = await api.get<DailyChallengesResponse>("/api/daily-challenges");
      return res.challenges ?? [];
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["daily-challenges"] });
  };

  return {
    challenges: data ?? [],
    isLoading,
    error,
    refetch,
    invalidate,
  };
}
