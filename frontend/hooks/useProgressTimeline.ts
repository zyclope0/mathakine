"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type ApiClientError } from "@/lib/api/client";

/** Période de la timeline : 7 ou 30 jours */
export type TimelinePeriod = "7d" | "30d";

/** Point journalier de la timeline */
export interface TimelinePoint {
  date: string;
  attempts: number;
  correct: number;
  success_rate_pct: number;
  avg_time_spent_s: number | null;
  by_type: Record<string, { attempts: number; correct: number; success_rate_pct: number }>;
}

/** Résumé global de la période */
export interface TimelineSummary {
  total_attempts: number;
  total_correct: number;
  overall_success_rate_pct: number;
}

/** Réponse du endpoint GET /api/users/me/progress/timeline */
export interface ProgressTimelineResponse {
  period: TimelinePeriod;
  from: string;
  to: string;
  points: TimelinePoint[];
  summary: TimelineSummary;
}

/** Query key stable pour le cache React Query */
export const PROGRESS_TIMELINE_QUERY_KEY = ["user", "progress", "timeline"] as const;

/**
 * Hook pour récupérer la courbe d'évolution temporelle (F07).
 * Fetch GET /api/users/me/progress/timeline?period=7d|30d
 */
export function useProgressTimeline(period: TimelinePeriod = "7d") {
  return useQuery<ProgressTimelineResponse, ApiClientError>({
    queryKey: [...PROGRESS_TIMELINE_QUERY_KEY, period],
    queryFn: async () => {
      const data = await api.get<ProgressTimelineResponse>(
        `/api/users/me/progress/timeline?period=${period}`
      );
      return data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: true,
  });
}
