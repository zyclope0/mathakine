"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

export interface TokenStatsByType {
  total_tokens: number;
  total_cost: number;
  count: number;
  average_tokens: number;
}

export interface ModelStats {
  total_tokens: number;
  total_cost: number;
  count: number;
}

export interface TokenStats {
  total_tokens: number;
  total_cost: number;
  average_tokens: number;
  count: number;
  by_type?: Record<string, TokenStatsByType>;
  by_model?: Record<string, ModelStats>;
}

export interface DailySummary {
  [challenge_type: string]: {
    tokens: number;
    cost: number;
  };
}

export interface AdminAiStatsResponse {
  days: number;
  stats: TokenStats;
  daily_summary: DailySummary;
}

export interface GenerationMetricsByType {
  success_rate: number;
  validation_failure_rate: number;
  auto_correction_rate: number;
  average_duration: number;
  total_generations: number;
}

export interface GenerationSummary {
  success_rate: number;
  validation_failure_rate: number;
  auto_correction_rate: number;
  average_duration: number;
  by_type: Record<string, GenerationMetricsByType>;
}

export interface AdminGenerationMetricsResponse {
  days: number;
  summary: GenerationSummary;
}

export function useAdminAiStats(days: number = 1, challengeType?: string) {
  const params = new URLSearchParams();
  params.set("days", String(days));
  if (challengeType) params.set("challenge_type", challengeType);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "ai-stats", days, challengeType ?? "all"],
    queryFn: async () => {
      return await api.get<AdminAiStatsResponse>(
        `/api/admin/ai-stats?${params.toString()}`
      );
    },
    staleTime: 60 * 1000,
  });

  return { data: data ?? null, isLoading, error, refetch };
}

export function useAdminGenerationMetrics(days: number = 1) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "generation-metrics", days],
    queryFn: async () => {
      return await api.get<AdminGenerationMetricsResponse>(
        `/api/admin/generation-metrics?days=${days}`
      );
    },
    staleTime: 60 * 1000,
  });

  return { data: data ?? null, isLoading, error, refetch };
}
