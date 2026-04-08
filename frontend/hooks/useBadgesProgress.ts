"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { BadgeProgressItem } from "@/lib/badges/types";

export type { BadgeProgressItem, SuccessRateProgressDetail } from "@/lib/badges/types";

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
