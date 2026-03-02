"use client";

import { useState } from "react";
import { PageHeader, PageSection, LoadingState } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAdminAiStats, useAdminGenerationMetrics } from "@/hooks/useAdminAiStats";
import { Bot, Coins, CheckCircle, AlertTriangle, Clock, Zap } from "lucide-react";

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
  if (seconds === 0) return "—";
  return `${seconds.toFixed(2)}s`;
}

export default function AdminAiMonitoringPage() {
  const [days, setDays] = useState<number>(1);

  const { data: statsData, isLoading: statsLoading, error: statsError } = useAdminAiStats(days);
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
  } = useAdminGenerationMetrics(days);

  const isLoading = statsLoading || metricsLoading;
  const error = statsError || metricsError;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Monitoring IA"
        description="Coûts tokens OpenAI et qualité des générations de défis"
      />

      <PageSection>
        <div className="flex flex-wrap gap-4 items-center mb-4">
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
        </div>

        {error ? (
          <Card>
            <CardContent className="py-12">
              <p className="text-center text-destructive">
                Erreur de chargement. Vérifiez vos droits admin.
              </p>
            </CardContent>
          </Card>
        ) : isLoading ? (
          <LoadingState message="Chargement du monitoring IA..." />
        ) : (
          <div className="space-y-8">
            {/* ── Tokens & Coûts ─────────────────────────────────────────── */}
            <section className="space-y-4">
              <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                <Coins className="h-5 w-5 text-primary" />
                Tokens OpenAI
              </h2>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Générations</CardTitle>
                    <Bot className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{statsData?.stats.count ?? 0}</p>
                    <p className="text-xs text-muted-foreground">sur la période</p>
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
                    <p className="text-xs text-muted-foreground mt-1">
                      moy. {statsData?.stats.average_tokens.toFixed(0) ?? 0} / génération
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Coût estimé</CardTitle>
                    <Coins className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {formatCost(statsData?.stats.total_cost ?? 0)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">USD — estimation</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Résumé du jour</CardTitle>
                    <Bot className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    {Object.keys(statsData?.daily_summary ?? {}).length === 0 ? (
                      <p className="text-sm text-muted-foreground">Aucune donnée</p>
                    ) : (
                      <ul className="space-y-1">
                        {Object.entries(statsData?.daily_summary ?? {}).map(([type, totals]) => (
                          <li key={type} className="flex justify-between text-xs">
                            <span className="text-muted-foreground capitalize">{type}</span>
                            <span className="font-medium">{formatCost(totals.cost)}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </CardContent>
                </Card>
              </div>

              {Object.keys(statsData?.stats.by_type ?? {}).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="h-5 w-5" />
                      Coût par type de défi
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-muted/50">
                            <th className="px-4 py-3 text-left font-medium">Type</th>
                            <th className="px-4 py-3 text-right font-medium">Générations</th>
                            <th className="px-4 py-3 text-right font-medium">Tokens moy.</th>
                            <th className="px-4 py-3 text-right font-medium">Coût total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(statsData?.stats.by_type ?? {}).map(([type, s]) => (
                            <tr key={type} className="border-b last:border-0 hover:bg-muted/50">
                              <td className="px-4 py-3 capitalize">{type}</td>
                              <td className="px-4 py-3 text-right">{s.count}</td>
                              <td className="px-4 py-3 text-right">
                                {s.average_tokens.toFixed(0)}
                              </td>
                              <td className="px-4 py-3 text-right">{formatCost(s.total_cost)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {Object.keys(statsData?.stats.by_model ?? {}).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Bot className="h-5 w-5" />
                      Répartition par modèle IA
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Coûts réels selon le modèle utilisé — o3 pour les défis complexes, o3-mini /
                      gpt-4o-mini pour les types simples
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-muted/50">
                            <th className="px-4 py-3 text-left font-medium">Modèle</th>
                            <th className="px-4 py-3 text-right font-medium">Appels</th>
                            <th className="px-4 py-3 text-right font-medium">Tokens totaux</th>
                            <th className="px-4 py-3 text-right font-medium">Coût estimé</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(statsData?.stats.by_model ?? {}).map(([model, s]) => (
                            <tr key={model} className="border-b last:border-0 hover:bg-muted/50">
                              <td className="px-4 py-3 font-mono text-xs">{model}</td>
                              <td className="px-4 py-3 text-right">{s.count}</td>
                              <td className="px-4 py-3 text-right">
                                {s.total_tokens.toLocaleString()}
                              </td>
                              <td className="px-4 py-3 text-right">{formatCost(s.total_cost)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </section>

            {/* ── Qualité des générations ─────────────────────────────── */}
            <section className="space-y-4">
              <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary" />
                Qualité des générations
              </h2>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Taux de succès</CardTitle>
                    <CheckCircle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {formatRate(metricsData?.summary.success_rate ?? 0)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">générations valides</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Échecs validation</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {formatRate(metricsData?.summary.validation_failure_rate ?? 0)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">défis rejetés</p>
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
                    <p className="text-xs text-muted-foreground mt-1">retries automatiques</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">Durée moyenne</CardTitle>
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {formatDuration(metricsData?.summary.average_duration ?? 0)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">par génération</p>
                  </CardContent>
                </Card>
              </div>

              {Object.keys(metricsData?.summary.by_type ?? {}).length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5" />
                      Détail par type de défi
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-muted/50">
                            <th className="px-4 py-3 text-left font-medium">Type</th>
                            <th className="px-4 py-3 text-right font-medium">Générations</th>
                            <th className="px-4 py-3 text-right font-medium">Succès</th>
                            <th className="px-4 py-3 text-right font-medium">Validation KO</th>
                            <th className="px-4 py-3 text-right font-medium">Auto-corr.</th>
                            <th className="px-4 py-3 text-right font-medium">Durée moy.</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(metricsData?.summary.by_type ?? {}).map(([type, m]) => (
                            <tr key={type} className="border-b last:border-0 hover:bg-muted/50">
                              <td className="px-4 py-3 capitalize">{type}</td>
                              <td className="px-4 py-3 text-right">{m.total_generations}</td>
                              <td className="px-4 py-3 text-right">{formatRate(m.success_rate)}</td>
                              <td className="px-4 py-3 text-right">
                                {formatRate(m.validation_failure_rate)}
                              </td>
                              <td className="px-4 py-3 text-right">
                                {formatRate(m.auto_correction_rate)}
                              </td>
                              <td className="px-4 py-3 text-right">
                                {formatDuration(m.average_duration)}
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
                      <p>Aucune génération IA enregistrée sur cette période.</p>
                      <p className="mt-1 text-sm">
                        Les données s&apos;accumulent au fil des générations de défis.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </section>
          </div>
        )}
      </PageSection>
    </div>
  );
}
