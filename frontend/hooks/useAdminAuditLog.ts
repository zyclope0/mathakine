"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface AuditLogEntry {
  id: number;
  admin_user_id: number | null;
  admin_username: string | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  details: Record<string, unknown> | null;
  created_at: string | null;
}

export interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
}

const ACTION_LABELS: Record<string, string> = {
  user_patch: "Modif. utilisateur",
  exercise_create: "Création exercice",
  exercise_update: "Modif. exercice",
  exercise_archive: "Archivage exercice",
  exercise_duplicate: "Duplication exercice",
  challenge_create: "Création défi",
  challenge_update: "Modif. défi",
  challenge_archive: "Archivage défi",
  challenge_duplicate: "Duplication défi",
  export_csv: "Export CSV",
};

export function getAuditActionLabel(action: string): string {
  return ACTION_LABELS[action] ?? action;
}

export function useAdminAuditLog(params?: {
  skip?: number;
  limit?: number;
  action?: string;
  resource_type?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params?.skip != null) searchParams.set("skip", String(params.skip));
  if (params?.limit != null) searchParams.set("limit", String(params.limit));
  if (params?.action) searchParams.set("action", params.action);
  if (params?.resource_type) searchParams.set("resource_type", params.resource_type);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin-audit-log", params],
    queryFn: async () => {
      const query = searchParams.toString();
      const res = await api.get<AuditLogResponse>(
        `/api/admin/audit-log${query ? `?${query}` : ""}`
      );
      return res;
    },
    staleTime: 10_000,
  });

  return {
    items: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refetch,
  };
}
