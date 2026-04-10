"use client";

import { useCallback, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { Bot, Coins, CheckCircle, AlertTriangle, Clock, Zap } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AdminReadHeavyPageShell } from "@/components/admin/AdminReadHeavyPageShell";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useAdminAiEvalHarnessRuns,
  useAdminAiStats,
  useAdminGenerationMetrics,
} from "@/hooks/useAdminAiStats";

function formatCost(cost: number): string {
  if (cost === 0) return "$0.00";
  if (cost < 0.001) return `$${cost.toFixed(6)}`;
  return `$${cost.toFixed(4)}`;
}

function formatRate(rate: number): string {
  return `${rate.toFixed(1)}%`;
}

function formatDuration(seconds: number): string {
  if (seconds === 0) return "-";
  return `${seconds.toFixed(2)}s`;
}

export default function AdminAiMonitoringPage() {
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
  } = useAdminAiEvalHarnessRuns(25);

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
      const key = workload as "assistant_chat" | "exercises_ai" | "challenges_ai" | "unknown";
      if (
        key === "assistant_chat" ||
        key === "exercises_ai" ||
        key === "challenges_ai" ||
        key === "unknown"
      ) {
        return t(`workloads.${key}`);
      }
      return workload;
    },
    [t]
  );

  const toolbar = (
    <Select value={String(days)} onValueChange={(v) => setDays(Number(v))}>
      <SelectTrigger className="w-[180px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {daysOptions.map((opt) => (
          <SelectItem key={opt.value} value={opt.value}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );

  return (
    <AdminReadHeavyPageShell
      title={t("title")}
      description={t("description")}
      toolbar={toolbar}
      hasError={!!error}
      errorMessage={t("errorLoading")}
      isLoading={isLoading}
      loadingMessage={t("loading")}
    >
      <div className="space-y-8">
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-foreground">
          <p className="font-medium">{t("limitsTitle")}</p>
          <ul className="mt-2 list-inside list-disc space-y-1 text-muted-foreground">
            <li>
              {t.rich("limitsChat", {
                s: (chunks) => <strong>{chunks}</strong>,
                c: (chunks) => <code className="rounded bg-muted px-1">{chunks}</code>,
              })}
            </li>
            <li>{t.rich("limitsCosts", { s: (chunks) => <strong>{chunks}</strong> })}</li>
            <li>{statsData?.stats.retention?.disclaimer_fr ?? t("fallbackRetention")}</li>
            <li>{metricsData?.summary.metrics_disclaimer_fr ?? t("fallbackMetrics")}</li>
          </ul>
        </div>

        <section className="space-y-4">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            <Coins className="h-5 w-5 text-primary" />
            {t("tokensSection")}
          </h2>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("calls")}</CardTitle>
                <Bot className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{statsData?.stats.count ?? 0}</p>
                <p className="text-xs text-muted-foreground">{t("onPeriod")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("totalTokens")}</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {statsData?.stats.total_tokens.toLocaleString() ?? 0}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {t("avgPerCall", {
                    avg: (statsData?.stats?.average_tokens ?? 0).toFixed(0),
                  })}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("estCost")}</CardTitle>
                <Coins className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{formatCost(statsData?.stats.total_cost ?? 0)}</p>
                <p className="mt-1 text-xs text-muted-foreground">{t("usdNote")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("daySummary")}</CardTitle>
                <Bot className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {Object.keys(statsData?.daily_summary ?? {}).length === 0 ? (
                  <p className="text-sm text-muted-foreground">{t("noData")}</p>
                ) : (
                  <ul className="space-y-1">
                    {Object.entries(statsData?.daily_summary ?? {}).map(([metricKey, totals]) => (
                      <li key={metricKey} className="flex justify-between text-xs">
                        <span className="text-muted-foreground">{metricKey}</span>
                        <span className="font-medium">{formatCost(totals.cost)}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>

          {Object.keys(statsByWorkload).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  {t("byWorkload")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thWorkload")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thCalls")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAvgTokens")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thTotalCost")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(statsByWorkload).map(([workload, stats]) => (
                        <tr key={workload} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="px-4 py-3">{formatWorkloadLabel(workload)}</td>
                          <td className="px-4 py-3 text-right">{stats.count}</td>
                          <td className="px-4 py-3 text-right">
                            {stats.average_tokens.toFixed(0)}
                          </td>
                          <td className="px-4 py-3 text-right">{formatCost(stats.total_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {Object.keys(statsByType).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  {t("detailByKey")}
                </CardTitle>
                <p className="text-sm text-muted-foreground">{t("detailByKeyDesc")}</p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thKey")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thCalls")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAvgTokens")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thTotalCost")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(statsByType).map(([metricKey, stats]) => (
                        <tr key={metricKey} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="px-4 py-3 font-mono text-xs">{metricKey}</td>
                          <td className="px-4 py-3 text-right">{stats.count}</td>
                          <td className="px-4 py-3 text-right">
                            {stats.average_tokens.toFixed(0)}
                          </td>
                          <td className="px-4 py-3 text-right">{formatCost(stats.total_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {Object.keys(statsByModel).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  {t("byModel")}
                </CardTitle>
                <p className="text-sm text-muted-foreground">{t("byModelDesc")}</p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thModel")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thCalls")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thTotalTokens")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("estCost")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(statsByModel).map(([model, stats]) => (
                        <tr key={model} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="px-4 py-3 font-mono text-xs">{model}</td>
                          <td className="px-4 py-3 text-right">{stats.count}</td>
                          <td className="px-4 py-3 text-right">
                            {stats.total_tokens.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right">{formatCost(stats.total_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </section>

        <section className="space-y-4">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            <CheckCircle className="h-5 w-5 text-primary" />
            {t("qualitySection")}
          </h2>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("successRate")}</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.success_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{t("successHint")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("validationFailures")}</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.validation_failure_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{t("validationHint")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("autoCorrections")}</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.auto_correction_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{t("autoCorrHint")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">{t("avgDuration")}</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatDuration(metricsData?.summary.average_duration ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{t("onSuccess")}</p>
              </CardContent>
            </Card>
          </div>

          {Object.keys(metricsByWorkload).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  {t("qualityByWorkload")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thWorkload")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thGenerations")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thSuccess")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thValidationKo")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAutoCorr")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAvgDur")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(metricsByWorkload).map(([workload, metrics]) => (
                        <tr key={workload} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="px-4 py-3">{formatWorkloadLabel(workload)}</td>
                          <td className="px-4 py-3 text-right">{metrics.total_generations}</td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.success_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.validation_failure_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.auto_correction_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatDuration(metrics.average_duration)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {Object.keys(metricsByType).length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  {t("detailByKey")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thKey")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thGenerations")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thSuccess")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thValidationKo")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAutoCorr")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thAvgDur")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(metricsByType).map(([metricKey, metrics]) => (
                        <tr key={metricKey} className="border-b last:border-0 hover:bg-muted/50">
                          <td className="px-4 py-3 font-mono text-xs">{metricKey}</td>
                          <td className="px-4 py-3 text-right">{metrics.total_generations}</td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.success_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.validation_failure_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatRate(metrics.auto_correction_rate)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {formatDuration(metrics.average_duration)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-muted-foreground">
                  <Bot className="mx-auto mb-3 h-12 w-12 opacity-50" />
                  <p>{t("noGenTitle")}</p>
                  <p className="mt-1 text-sm">{t("noGenHint")}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {Object.keys(errorTypes).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  {t("errorsObserved")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">{t("thErrorType")}</th>
                        <th className="px-4 py-3 text-right font-medium">{t("thOccurrences")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(errorTypes)
                        .sort((a, b) => b[1] - a[1])
                        .map(([errorType, count]) => (
                          <tr key={errorType} className="border-b last:border-0 hover:bg-muted/50">
                            <td className="px-4 py-3 font-mono text-xs">{errorType}</td>
                            <td className="px-4 py-3 text-right">{count}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </section>

        <section className="space-y-4">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            <Bot className="h-5 w-5 text-primary" />
            {t("harnessSection")}
          </h2>
          <p className="text-sm text-muted-foreground">{harnessData?.disclaimer_fr}</p>
          {harnessData && harnessData.runs.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>{t("lastRuns", { count: harnessData.runs.length })}</CardTitle>
                <p className="text-sm text-muted-foreground">{t("harnessCardDesc")}</p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left font-medium">{t("thCompleted")}</th>
                        <th className="px-3 py-2 text-left font-medium">{t("thMode")}</th>
                        <th className="px-3 py-2 text-left font-medium">{t("thTarget")}</th>
                        <th className="px-3 py-2 text-right font-medium">{t("thOkKoSkip")}</th>
                        <th className="px-3 py-2 text-left font-medium">{t("thArtifacts")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {harnessData.runs.map((run) => (
                        <tr key={run.run_uuid} className="border-b last:border-0">
                          <td className="px-3 py-2 whitespace-nowrap text-xs">
                            {run.completed_at ?? "—"}
                          </td>
                          <td className="px-3 py-2 font-mono text-xs">{run.mode}</td>
                          <td className="px-3 py-2 font-mono text-xs">{run.target}</td>
                          <td className="px-3 py-2 text-right text-xs">
                            {run.cases_passed}/{run.cases_failed}/{run.cases_skipped}
                          </td>
                          <td className="px-3 py-2 text-xs text-muted-foreground">
                            {run.json_artifact_path || run.markdown_artifact_path ? (
                              <span className="break-all">
                                {run.json_artifact_path ?? run.markdown_artifact_path}
                              </span>
                            ) : (
                              "—"
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-sm text-muted-foreground">
                {t("harnessEmpty")}
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </AdminReadHeavyPageShell>
  );
}
