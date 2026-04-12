"use client";

/**
 * useAdminAiMonitoringPageController — état local `days`, agrégation des hooks admin IA,
 * dérivés et libellés workload pour la page admin Monitoring IA (ACTIF-06-AI-MONITORING-01).
 *
 * Aucun fetch direct : délègue à useAdminAiStats / useAdminGenerationMetrics / useAdminAiEvalHarnessRuns. Pas de JSX.
 */

import { useCallback, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  useAdminAiEvalHarnessRuns,
  useAdminAiStats,
  useAdminGenerationMetrics,
} from "@/hooks/useAdminAiStats";

/** Limite des runs harness persistés affichés en bas de page (inchangée produit). */
export const HARNESS_RUNS_LIMIT = 25;

const KNOWN_WORKLOAD_KEYS = ["assistant_chat", "exercises_ai", "challenges_ai", "unknown"] as const;

type KnownWorkloadKey = (typeof KNOWN_WORKLOAD_KEYS)[number];

function isKnownWorkloadKey(value: string): value is KnownWorkloadKey {
  return (KNOWN_WORKLOAD_KEYS as readonly string[]).includes(value);
}

export function useAdminAiMonitoringPageController() {
  const t = useTranslations("adminPages.aiMonitoring");
  const [days, setDays] = useState<number>(1);

  const { data: statsData, isLoading: statsLoading, error: statsError } = useAdminAiStats(days);
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
  } = useAdminGenerationMetrics(days);
  const {
    data: harnessData,
    isLoading: harnessLoading,
    error: harnessError,
  } = useAdminAiEvalHarnessRuns(HARNESS_RUNS_LIMIT);

  const isLoading = statsLoading || metricsLoading || harnessLoading;
  const error = statsError || metricsError || harnessError;

  const statsByWorkload = statsData?.stats.by_workload ?? {};
  const statsByType = statsData?.stats.by_type ?? {};
  const statsByModel = statsData?.stats.by_model ?? {};
  const metricsByWorkload = metricsData?.summary.by_workload ?? {};
  const metricsByType = metricsData?.summary.by_type ?? {};
  const errorTypes = metricsData?.summary.error_types ?? {};

  const daysOptions = useMemo(
    () =>
      [
        { value: "1", label: t("days.1") },
        { value: "7", label: t("days.7") },
        { value: "30", label: t("days.30") },
      ] as const,
    [t]
  );

  const formatWorkloadLabel = useCallback(
    (workload: string) => {
      if (isKnownWorkloadKey(workload)) {
        return t(`workloads.${workload}`);
      }
      return workload;
    },
    [t]
  );

  const handleDaysChange = useCallback((value: string) => {
    setDays(Number(value));
  }, []);

  return {
    t,
    days,
    handleDaysChange,
    statsData,
    metricsData,
    harnessData,
    isLoading,
    error,
    statsByWorkload,
    statsByType,
    statsByModel,
    metricsByWorkload,
    metricsByType,
    errorTypes,
    daysOptions,
    formatWorkloadLabel,
  };
}
