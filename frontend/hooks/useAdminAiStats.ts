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

export interface RuntimeRetentionMeta {
  max_age_days: number;
  max_events_per_key: number;
  disclaimer_fr: string;
}

export interface TokenStats {
  total_tokens: number;
  total_cost: number;
  average_tokens: number;
  count: number;
  by_type?: Record<string, TokenStatsByType>;
  by_model?: Record<string, ModelStats>;
  by_workload?: Record<string, TokenStatsByType>;
  retention?: RuntimeRetentionMeta;
  cost_disclaimer_fr?: string;
}

export interface DailySummary {
  [metric_key: string]: {
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
  by_workload?: Record<string, GenerationMetricsByType>;
  error_types?: Record<string, number>;
  retention?: RuntimeRetentionMeta;
  metrics_disclaimer_fr?: string;
}

export interface AdminGenerationMetricsResponse {
  days: number;
  summary: GenerationSummary;
}

export function useAdminAiStats(days: number = 1, metricKey?: string) {
  const params = new URLSearchParams();
  params.set("days", String(days));
  if (metricKey) params.set("challenge_type", metricKey);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "ai-stats", days, metricKey ?? "all"],
    queryFn: async () => {
      return await api.get<AdminAiStatsResponse>(`/api/admin/ai-stats?${params.toString()}`);
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

export interface HarnessRunSummary {
  id: number;
  run_uuid: string;
  mode: string;
  target: string;
  corpus_path: string;
  corpus_version: number;
  started_at: string | null;
  completed_at: string | null;
  cases_total: number;
  cases_run: number;
  cases_passed: number;
  cases_failed: number;
  cases_skipped: number;
  limitations_note: string;
  json_artifact_path: string | null;
  markdown_artifact_path: string | null;
  git_revision: string | null;
  app_version: string | null;
  live_opt_in: boolean;
  created_at: string | null;
}

export interface AdminAiEvalHarnessRunsResponse {
  runs: HarnessRunSummary[];
  limit: number;
  disclaimer_fr: string;
}

export function useAdminAiEvalHarnessRuns(limit: number = 20) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "ai-eval-harness-runs", limit],
    queryFn: async () => {
      return await api.get<AdminAiEvalHarnessRunsResponse>(
        `/api/admin/ai-eval-harness-runs?limit=${limit}`
      );
    },
    staleTime: 60 * 1000,
  });

  return { data: data ?? null, isLoading, error, refetch };
}
