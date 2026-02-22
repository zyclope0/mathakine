"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect } from "react";
import { debugLog } from "@/lib/utils/debug";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  hasMore?: boolean;
}

export interface PaginatedContentFilters {
  skip?: number;
  limit?: number;
  search?: string;
  [key: string]: string | number | null | undefined;
}

/** Filtres acceptés : types compatibles (ExerciseFilters, ChallengeFilters, etc.) */
export type PaginatedContentFiltersInput = Partial<
  Record<string, string | number | null | undefined>
>;

export interface UsePaginatedContentConfig<T> {
  /** Base endpoint (ex: "/api/exercises", "/api/challenges") */
  endpoint: string;
  /** Query key prefix pour cache (ex: "exercises", "challenges") */
  queryKey: string;
  /** Noms des paramètres de filtre (ex: { type: "exercise_type" } ou { type: "challenge_type" }) */
  paramKeys?: Record<string, string>;
  /** Paramètres fixes à toujours envoyer (ex: { active_only: "true" }) */
  fixedParams?: Record<string, string>;
  staleTime?: number;
  defaultLimit?: number;
}

/**
 * Hook générique pour contenu paginé (DRY useExercises / useChallenges).
 */
export function usePaginatedContent<T>(
  filters: PaginatedContentFiltersInput = {},
  config: UsePaginatedContentConfig<T>
) {
  const queryClient = useQueryClient();
  const { locale } = useLocaleStore();
  const {
    endpoint,
    queryKey,
    paramKeys = {},
    fixedParams = {},
    staleTime = 30 * 1000,
    defaultLimit = 15,
  } = config;

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: [queryKey] });
  }, [locale, queryClient, queryKey]);

  const skip = filters?.skip ?? 0;
  const limit = filters?.limit ?? defaultLimit;

  const { data, isLoading, isFetching, error } = useQuery<PaginatedResponse<T>>({
    queryKey: [
      queryKey,
      skip,
      limit,
      ...Object.keys(paramKeys).map((k) => filters[k] ?? null),
      filters?.search ?? null,
      locale,
    ],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append("skip", skip.toString());
      params.append("limit", limit.toString());
      if (filters?.search) params.append("search", String(filters.search));

      for (const [filterKey, paramName] of Object.entries(paramKeys)) {
        const val = filters[filterKey];
        if (val != null && val !== "") params.append(paramName, String(val));
      }
      for (const [k, v] of Object.entries(fixedParams)) {
        params.append(k, v);
      }

      const queryString = params.toString();
      const url = `${endpoint}${queryString ? `?${queryString}` : ""}`;
      debugLog(`[usePaginatedContent] Fetching ${queryKey}:`, url);
      const result = await api.get<PaginatedResponse<T>>(url);
      debugLog(
        `[usePaginatedContent] ${queryKey}:`,
        result?.items?.length ?? 0,
        "total:",
        result?.total ?? 0
      );
      return result;
    },
    staleTime,
    gcTime: 5 * 60 * 1000,
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    retry: 2,
  });

  return {
    items: data?.items ?? [],
    total: data?.total ?? 0,
    hasMore: data?.hasMore ?? false,
    isLoading,
    isFetching,
    error,
  };
}
