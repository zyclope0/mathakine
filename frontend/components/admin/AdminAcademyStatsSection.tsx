"use client";

import { BookOpen, Brain, Puzzle, Target } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAcademyStats } from "@/hooks/useAcademyStats";

function getTopEntries<T extends { count: number }>(items: Record<string, T>, limit: number) {
  return Object.values(items)
    .sort((left, right) => right.count - left.count)
    .slice(0, limit);
}

export function AdminAcademyStatsSection() {
  const { stats, isLoading, error } = useAcademyStats();

  if (error || (!isLoading && !stats)) {
    return (
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Statistiques academie</CardTitle>
          <p className="text-sm text-muted-foreground">
            Endpoint reutilise : <code>/api/exercises/stats</code>
          </p>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Statistiques globales indisponibles pour le moment.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (isLoading || !stats) {
    return (
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Statistiques academie</CardTitle>
          <p className="text-sm text-muted-foreground">
            Endpoint reutilise : <code>/api/exercises/stats</code>
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map((item) => (
              <div key={item} className="rounded-lg border p-3 space-y-2">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-8 w-16" />
              </div>
            ))}
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border p-4 space-y-2">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
            </div>
            <div className="rounded-lg border p-4 space-y-2">
              <Skeleton className="h-5 w-28" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const topDisciplines = getTopEntries(stats.by_discipline, 3);
  const topRanks = getTopEntries(stats.by_rank, 3);
  const statItems = [
    {
      key: "total_exercises",
      label: "Exercices",
      value: stats.academy_statistics.total_exercises,
      icon: BookOpen,
    },
    {
      key: "total_challenges",
      label: "Defis",
      value: stats.academy_statistics.total_challenges,
      icon: Puzzle,
    },
    {
      key: "ai_generated",
      label: "Contenus IA",
      value: stats.academy_statistics.ai_generated,
      icon: Brain,
    },
    {
      key: "total_attempts",
      label: "Tentatives",
      value: stats.global_performance.total_attempts,
      icon: Target,
    },
  ];

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Statistiques academie</CardTitle>
        <p className="text-sm text-muted-foreground">
          Vue globale reutilisant <code>/api/exercises/stats</code> sans nouveau backend.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {statItems.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.key} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs text-muted-foreground">{item.label}</p>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </div>
                <p className="mt-2 text-2xl font-bold">{item.value}</p>
              </div>
            );
          })}
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-medium">Disciplines dominantes</h3>
            <div className="mt-3 space-y-2">
              {topDisciplines.length > 0 ? (
                topDisciplines.map((discipline) => (
                  <div
                    key={discipline.discipline_name}
                    className="flex items-center justify-between gap-3 text-sm"
                  >
                    <span>{discipline.discipline_name}</span>
                    <span className="text-muted-foreground">
                      {discipline.count} ({Math.round(discipline.percentage)}%)
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Aucune discipline disponible.</p>
              )}
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-medium">Repartition par rang</h3>
            <div className="mt-3 space-y-2">
              {topRanks.length > 0 ? (
                topRanks.map((rank) => (
                  <div
                    key={rank.rank_name}
                    className="flex items-center justify-between gap-3 text-sm"
                  >
                    <span>{rank.rank_name}</span>
                    <span className="text-muted-foreground">
                      {rank.count} ({Math.round(rank.percentage)}%)
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Aucun rang disponible.</p>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
