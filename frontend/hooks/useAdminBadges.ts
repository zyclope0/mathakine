"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface AdminBadge {
  id: number;
  code: string;
  name: string;
  description: string;
  icon_url: string;
  category: string;
  difficulty: string;
  points_reward: number;
  is_secret: boolean;
  requirements: Record<string, unknown> | string | null;
  star_wars_title: string;
  is_active: boolean;
  created_at: string | null;
  _user_count?: number;
}

export interface AdminBadgesResponse {
  success: boolean;
  data: AdminBadge[];
}

export function useAdminBadges() {
  const { data, isLoading, error, refetch } = useQuery<
    AdminBadgesResponse,
    ApiClientError
  >({
    queryKey: ["admin", "badges"],
    queryFn: async () => api.get<AdminBadgesResponse>("/api/admin/badges"),
    staleTime: 30 * 1000,
  });

  const badges = data?.data ?? [];
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: async (payload: Omit<AdminBadge, "id" | "created_at">) =>
      api.post<AdminBadge>("/api/admin/badges", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "badges"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({
      id,
      payload,
    }: { id: number; payload: Partial<AdminBadge> }) =>
      api.put<AdminBadge>(`/api/admin/badges/${id}`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "badges"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (badgeId: number) =>
      api.delete<{ success: boolean; id: number }>(`/api/admin/badges/${badgeId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "badges"] });
    },
  });

  return {
    badges,
    isLoading,
    error,
    refetch,
    create: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    update: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    remove: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
