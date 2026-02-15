"use client";

import { useQuery } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface AdminReports {
  period: "7d" | "30d";
  days: number;
  new_users: number;
  attempts_exercises: number;
  attempts_challenges: number;
  total_attempts: number;
  success_rate: number;
  active_users: number;
}

export function useAdminReports(period: "7d" | "30d" = "7d") {
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<AdminReports, ApiClientError>({
    queryKey: ["admin", "reports", period],
    queryFn: async () => {
      return await api.get<AdminReports>(`/api/admin/reports?period=${period}`);
    },
    staleTime: 2 * 60 * 1000,
    enabled: !!period,
  });

  return {
    reports: data ?? null,
    isLoading,
    error,
    refetch,
  };
}
