"use client";

import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";
import type { ChallengesStats } from "@/types/api";

const STALE_MS = 5 * 60 * 1000;

/**
 * Statistiques agrégées du catalogue de défis (GET /api/challenges/stats).
 * Données peu volatiles — cache 5 minutes.
 */
export function useChallengesStats(): UseQueryResult<ChallengesStats, ApiClientError> {
  return useQuery<ChallengesStats, ApiClientError>({
    queryKey: ["challenges", "catalog-stats"],
    queryFn: async () => api.get<ChallengesStats>("/api/challenges/stats"),
    staleTime: STALE_MS,
    refetchOnWindowFocus: false,
  });
}
