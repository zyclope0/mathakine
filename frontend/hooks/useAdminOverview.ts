"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface AdminOverview {
  total_users: number;
  total_exercises: number;
  total_challenges: number;
  total_attempts: number;
}

export function useAdminOverview() {
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<AdminOverview, ApiClientError>({
    queryKey: ["admin", "overview"],
    queryFn: async () => {
      return await api.get<AdminOverview>("/api/admin/overview");
    },
    staleTime: 60 * 1000,
  });

  return {
    overview: data ?? { total_users: 0, total_exercises: 0, total_challenges: 0, total_attempts: 0 },
    isLoading,
    error,
    refetch,
  };
}
