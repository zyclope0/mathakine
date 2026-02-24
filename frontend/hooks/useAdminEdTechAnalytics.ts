"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface EdTechEventItem {
  id: number;
  user_id: number | null;
  event: string;
  payload: Record<string, unknown> | null;
  created_at: string | null;
}

export interface EdTechAggregates {
  [event: string]: {
    count: number;
    avg_time_to_first_attempt_ms: number | null;
  };
}

export interface EdTechCtrSummary {
  total_clicks: number;
  guided_clicks: number;
  guided_rate_pct: number;
}

export interface AdminEdTechAnalyticsResponse {
  period: string;
  since: string;
  aggregates: EdTechAggregates;
  ctr_summary: EdTechCtrSummary;
  events: EdTechEventItem[];
}

export function useAdminEdTechAnalytics(
  period: "7d" | "30d" = "7d",
  eventFilter?: string
) {
  const params = new URLSearchParams();
  params.set("period", period);
  if (eventFilter) params.set("event", eventFilter);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "analytics", "edtech", period, eventFilter ?? "all"],
    queryFn: async () => {
      return await api.get<AdminEdTechAnalyticsResponse>(
        `/api/admin/analytics/edtech?${params.toString()}`
      );
    },
    staleTime: 60 * 1000,
  });

  return {
    data: data ?? null,
    isLoading,
    error,
    refetch,
  };
}
