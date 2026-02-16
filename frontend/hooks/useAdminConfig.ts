"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiClientError } from "@/lib/api/client";

export interface AdminConfigItem {
  key: string;
  value: boolean | number | string;
  type: "bool" | "int" | "str";
  category: string;
  label: string;
  min?: number;
  max?: number;
}

interface AdminConfigResponse {
  settings: AdminConfigItem[];
}

const EMPTY_SETTINGS: AdminConfigItem[] = [];

export function useAdminConfig() {
  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<AdminConfigResponse, ApiClientError>({
    queryKey: ["admin", "config"],
    queryFn: async () => {
      return await api.get<AdminConfigResponse>("/api/admin/config");
    },
    staleTime: 60 * 1000,
  });

  const updateMutation = useMutation({
    mutationFn: async (settings: Record<string, boolean | number | string>) => {
      return await api.put<{ status: string }>("/api/admin/config", {
        settings,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "config"] });
    },
  });

  return {
    settings: data?.settings ?? EMPTY_SETTINGS,
    isLoading,
    error,
    refetch,
    updateSettings: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
  };
}
