"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useLeaderboard } from "@/hooks/useLeaderboard";
import { useAgeGroupDisplay } from "@/hooks/useChallengeTranslations";
import { Trophy, Medal, User } from "lucide-react";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState } from "@/components/layout";
import { cn } from "@/lib/utils/cn";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";
import { AGE_GROUPS } from "@/lib/constants/exercises";

const RANK_ICONS: Record<number, string> = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

function getJediRankIcon(rank: string): string {
  const icons: Record<string, string> = {
    youngling: "🌟",
    padawan: "⚔️",
    knight: "🗡️",
    master: "👑",
    grand_master: "✨",
  };
  return icons[rank] ?? "🌟";
}

export default function LeaderboardPage() {
  const t = useTranslations("leaderboard");
  const { user } = useAuth();
  const getAgeDisplay = useAgeGroupDisplay();
  const [ageFilter, setAgeFilter] = useState<string>("all");
  const effectiveAgeGroup = ageFilter === "all" ? undefined : ageFilter;
  const { leaderboard, isLoading, error } = useLeaderboard(50, effectiveAgeGroup);

  return (
    <ProtectedRoute>
      <PageLayout>
        <PageHeader title={t("title")} description={t("description")} icon={Trophy} />

        <PageSection>
          {error ? (
            <Card className="card-spatial-depth">
              <CardContent className="py-12">
                <p className="text-center text-destructive">
                  {t("error") ?? "Erreur de chargement"}
                </p>
              </CardContent>
            </Card>
          ) : isLoading ? (
            <LoadingState message={t("loading")} />
          ) : leaderboard.length === 0 ? (
            <Card className="card-spatial-depth">
              <CardContent className="py-12">
                <p className="text-center text-muted-foreground">{t("empty")}</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="card-spatial-depth">
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <CardTitle className="flex items-center gap-2">
                    <Medal className="h-5 w-5" aria-hidden />
                    {t("ranking")}
                  </CardTitle>
                  <Select
                      value={ageFilter}
                      onValueChange={setAgeFilter}
                      aria-label={t("filterByAge", { default: "Filtrer par groupe d'âge" })}
                    >
                      <SelectTrigger className="w-[200px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{t("allAges", { default: "Tous les âges" })}</SelectItem>
                        {Object.values(AGE_GROUPS)
                          .filter((g) => g !== AGE_GROUPS.ALL_AGES)
                          .map((group) => (
                            <SelectItem key={group} value={group}>
                              {getAgeDisplay(group as keyof typeof AGE_GROUPS)}
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2" role="list">
                  {leaderboard.map((entry: LeaderboardEntry) => (
                    <li
                      key={entry.username}
                      className={cn(
                        "flex items-center gap-4 rounded-lg px-4 py-3",
                        entry.is_current_user && "bg-primary/10 ring-1 ring-primary/30"
                      )}
                    >
                      <span className="w-10 text-2xl">
                        {RANK_ICONS[entry.rank] ?? `#${entry.rank}`}
                      </span>
                      <span className="w-8 text-sm text-muted-foreground">#{entry.rank}</span>
                      <User className="h-4 w-4 text-muted-foreground" aria-hidden />
                      <span className="flex-1 font-medium">{entry.username}</span>
                      <span>{getJediRankIcon(entry.jedi_rank)}</span>
                      <span className="text-sm text-muted-foreground">
                        {t("level")} {entry.current_level}
                      </span>
                      <span className="font-semibold text-primary">{entry.total_points} pts</span>
                      {entry.is_current_user && (
                        <span
                          className="text-xs bg-primary/20 px-2 py-0.5 rounded"
                          aria-label={t("you")}
                        >
                          {t("you")}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
