"use client";

import { useState } from "react";
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

const DAYS_OPTIONS = [
  { value: "1", label: "Aujourd'hui" },
  { value: "7", label: "7 derniers jours" },
  { value: "30", label: "30 derniers jours" },
];

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

function formatWorkloadLabel(workload: string): string {
  switch (workload) {
    case "assistant_chat":
      return "Assistant chat (authentifie, rate-limite)";
    case "exercises_ai":
      return "Exercices IA";
    case "challenges_ai":
      return "Defis IA";
    case "unknown":
      return "Cle runtime non classe (unknown)";
    default:
      return workload;
  }
}

export default function AdminAiMonitoringPage() {
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

  const toolbar = (
    <Select value={String(days)} onValueChange={(v) => setDays(Number(v))}>
      <SelectTrigger className="w-[180px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {DAYS_OPTIONS.map((opt) => (
          <SelectItem key={opt.value} value={opt.value}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );

  return (
    <AdminReadHeavyPageShell
      title="Monitoring IA"
      description="Couts estimes et qualite runtime : chat assistant authentifie rate-limite, exercices IA, defis IA. Donnees process a retention bornee ; harness persisté en bas de page."
      toolbar={toolbar}
      hasError={!!error}
      errorMessage="Erreur de chargement. Verifiez vos droits admin."
      isLoading={isLoading}
      loadingMessage="Chargement du monitoring IA..."
    >
      <div className="space-y-8">
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-foreground">
          <p className="font-medium">Limites a connaitre (IA12)</p>
          <ul className="mt-2 list-inside list-disc space-y-1 text-muted-foreground">
            <li>
              Le chat d&apos;assistance est <strong>authentifié</strong> (JWT + cookies sur{" "}
              <code className="rounded bg-muted px-1">/api/chat</code> et le proxy Next) et{" "}
              <strong>rate-limité</strong> — son poids apparaît dans les workloads ci-dessous.
            </li>
            <li>
              Coûts USD = <strong>estimations</strong> (grilles indicatives), pas une vérité
              comptable.
            </li>
            <li>
              {statsData?.stats.retention?.disclaimer_fr ??
                "Agrégats runtime : mémoire process purgée au-delà de la fenêtre de rétention."}
            </li>
            <li>
              {metricsData?.summary.metrics_disclaimer_fr ??
                "Pour des runs figés, voir la section harness persisté ci-dessous."}
            </li>
          </ul>
        </div>

        <section className="space-y-4">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            <Coins className="h-5 w-5 text-primary" />
            Tokens OpenAI
          </h2>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Appels IA</CardTitle>
                <Bot className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{statsData?.stats.count ?? 0}</p>
                <p className="text-xs text-muted-foreground">sur la periode</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Tokens totaux</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {statsData?.stats.total_tokens.toLocaleString() ?? 0}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  moy. {statsData?.stats.average_tokens.toFixed(0) ?? 0} / appel
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Cout estime</CardTitle>
                <Coins className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{formatCost(statsData?.stats.total_cost ?? 0)}</p>
                <p className="mt-1 text-xs text-muted-foreground">USD - estimation runtime</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Resume du jour</CardTitle>
                <Bot className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {Object.keys(statsData?.daily_summary ?? {}).length === 0 ? (
                  <p className="text-sm text-muted-foreground">Aucune donnee</p>
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
                  Repartition par workload
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Workload</th>
                        <th className="px-4 py-3 text-right font-medium">Appels</th>
                        <th className="px-4 py-3 text-right font-medium">Tokens moy.</th>
                        <th className="px-4 py-3 text-right font-medium">Cout total</th>
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
                  Detail par cle runtime
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Detail fin par cle interne: type de defi, type d&apos;exercice IA ou segment du
                  chat.
                </p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Cle</th>
                        <th className="px-4 py-3 text-right font-medium">Appels</th>
                        <th className="px-4 py-3 text-right font-medium">Tokens moy.</th>
                        <th className="px-4 py-3 text-right font-medium">Cout total</th>
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
                  Repartition par modele IA
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Repartition runtime reelle des appels par famille de modele.
                </p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Modele</th>
                        <th className="px-4 py-3 text-right font-medium">Appels</th>
                        <th className="px-4 py-3 text-right font-medium">Tokens totaux</th>
                        <th className="px-4 py-3 text-right font-medium">Cout estime</th>
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
            Qualite des generations
          </h2>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Taux de succes</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.success_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">cas enregistres comme reussis</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Echecs validation</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.validation_failure_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">sur les flux valides metier</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Auto-corrections</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatRate(metricsData?.summary.auto_correction_rate ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  retries / corrections automatiques
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Duree moyenne</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatDuration(metricsData?.summary.average_duration ?? 0)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">sur les succes</p>
              </CardContent>
            </Card>
          </div>

          {Object.keys(metricsByWorkload).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Qualite par workload
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Workload</th>
                        <th className="px-4 py-3 text-right font-medium">Generations</th>
                        <th className="px-4 py-3 text-right font-medium">Succes</th>
                        <th className="px-4 py-3 text-right font-medium">Validation KO</th>
                        <th className="px-4 py-3 text-right font-medium">Auto-corr.</th>
                        <th className="px-4 py-3 text-right font-medium">Duree moy.</th>
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
                  Detail par cle runtime
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Cle</th>
                        <th className="px-4 py-3 text-right font-medium">Generations</th>
                        <th className="px-4 py-3 text-right font-medium">Succes</th>
                        <th className="px-4 py-3 text-right font-medium">Validation KO</th>
                        <th className="px-4 py-3 text-right font-medium">Auto-corr.</th>
                        <th className="px-4 py-3 text-right font-medium">Duree moy.</th>
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
                  <p>Aucune generation IA enregistree sur cette periode.</p>
                  <p className="mt-1 text-sm">
                    Les donnees s&apos;accumulent au fil des appels chat, des exercices IA et des
                    defis IA.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {Object.keys(errorTypes).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Erreurs observees
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left font-medium">Type d&apos;erreur</th>
                        <th className="px-4 py-3 text-right font-medium">Occurrences</th>
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
            Harness d&apos;evaluation (persiste)
          </h2>
          <p className="text-sm text-muted-foreground">{harnessData?.disclaimer_fr}</p>
          {harnessData && harnessData.runs.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Derniers runs ({harnessData.runs.length})</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Mode offline/live, cible, corpus et compteurs au moment du run. Chemins
                  d&apos;artefacts si enregistrés côté serveur.
                </p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left font-medium">Termine</th>
                        <th className="px-3 py-2 text-left font-medium">Mode</th>
                        <th className="px-3 py-2 text-left font-medium">Cible</th>
                        <th className="px-3 py-2 text-right font-medium">OK / KO / skip</th>
                        <th className="px-3 py-2 text-left font-medium">Artifacts</th>
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
                Aucun run harness persisté en base pour l&apos;instant.
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </AdminReadHeavyPageShell>
  );
}
