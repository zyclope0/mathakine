"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface BadgeProgressItem {
  id: number;
  code: string;
  name: string;
  progress?: number;
  current?: number;
  target?: number;
}

export interface BadgesProgressData {
  unlocked: { id: number; code: string; name: string }[];
  in_progress: BadgeProgressItem[];
}

export function useBadgesProgress() {
  const { data, isLoading, error } = useQuery<
    { success: boolean; data: BadgesProgressData },
    ApiClientError
  >({
    queryKey: ["badges", "progress"],
    queryFn: async () => {
      return await api.get<{ success: boolean; data: BadgesProgressData }>(
        "/api/challenges/badges/progress"
      );
    },
    staleTime: 60 * 1000,
  });

  return {
    unlocked: data?.data?.unlocked ?? [],
    inProgress: data?.data?.in_progress ?? [],
    isLoading,
    error,
  };
}
