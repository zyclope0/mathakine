"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface AdminChallenge {
  id: number;
  title: string;
  challenge_type: string;
  age_group: string;
  is_archived: boolean;
  attempt_count: number;
  success_rate: number;
  created_at?: string | null;
}

export interface AdminChallengesParams {
  archived?: boolean;
  type?: string;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  skip?: number;
  limit?: number;
}

export interface AdminChallengesResponse {
  items: AdminChallenge[];
  total: number;
}

export function useAdminChallenges(params: AdminChallengesParams = {}) {
  const { archived, type, search, sort, order, skip = 0, limit = 20 } = params;

  const searchParams = new URLSearchParams();
  if (archived !== undefined) searchParams.set("archived", String(archived));
  if (type) searchParams.set("type", type);
  if (search) searchParams.set("search", search);
  if (sort) searchParams.set("sort", sort);
  if (order) searchParams.set("order", order);
  searchParams.set("skip", String(skip));
  searchParams.set("limit", String(limit));

  const queryString = searchParams.toString();
  const url = `/api/admin/challenges${queryString ? `?${queryString}` : ""}`;

  const { data, isLoading, error, refetch } = useQuery<
    AdminChallengesResponse,
    ApiClientError
  >({
    queryKey: ["admin", "challenges", { archived, type, search, sort, order, skip, limit }],
    queryFn: async () => api.get<AdminChallengesResponse>(url),
    staleTime: 30 * 1000,
  });

  const queryClient = useQueryClient();
  const patchMutation = useMutation({
    mutationFn: async ({
      challengeId,
      isArchived,
    }: {
      challengeId: number;
      isArchived: boolean;
    }) => {
      return api.patch<{
        id: number;
        title: string;
        is_archived: boolean;
      }>(`/api/admin/challenges/${challengeId}`, { is_archived: isArchived });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "challenges"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "overview"] });
    },
  });

  return {
    challenges: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refetch,
    updateArchived: patchMutation.mutateAsync,
    isUpdating: patchMutation.isPending,
    updateError: patchMutation.error,
  };
}
