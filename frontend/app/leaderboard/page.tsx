"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useLeaderboard } from "@/hooks/useLeaderboard";
import { Trophy, Medal, Flame, Award } from "lucide-react";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState, EmptyState } from "@/components/layout";
import { cn } from "@/lib/utils";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";
import { RANK_MEDALS, JEDI_RANK_ICONS } from "@/lib/constants/leaderboard";
import { UserAvatar } from "@/components/ui/UserAvatar";

// ─── Sous-composants ──────────────────────────────────────────────────────────

function RankBadge({ rank, label }: { rank: number; label: string }) {
  if (RANK_MEDALS[rank]) {
    return (
      <span className="flex-shrink-0 w-10 text-center text-2xl leading-none" aria-label={label}>
        {RANK_MEDALS[rank]}
      </span>
    );
  }
  return (
    <span className="flex-shrink-0 w-10 flex items-center justify-center" aria-label={label}>
      <span className="h-8 w-8 rounded-full bg-white/5 flex items-center justify-center font-mono text-sm text-muted-foreground">
        {rank}
      </span>
    </span>
  );
}

interface LeaderboardRowProps {
  entry: LeaderboardEntry;
  isLast: boolean;
  tLevel: string;
  tYou: string;
  tRank: string;
  tStreak: string;
  tBadges: string;
}

function LeaderboardRow({
  entry,
  isLast,
  tLevel,
  tYou,
  tRank,
  tStreak,
  tBadges,
}: LeaderboardRowProps) {
  return (
    <li
      className={cn(
        "flex items-center gap-4 px-4 py-3",
        "hover:bg-white/5 transition-colors duration-150 cursor-pointer",
        !isLast && "border-b border-white/5",
        entry.is_current_user
          ? "bg-primary/10 border-l-4 border-l-primary"
          : "border-l-4 border-l-transparent"
      )}
    >
      <RankBadge rank={entry.rank} label={`${tRank} ${entry.rank}`} />

      <UserAvatar username={entry.username} size="md" avatarUrl={entry.avatar_url} />

      <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
        <span
          className={cn(
            "font-semibold truncate",
            entry.is_current_user ? "text-foreground" : "text-foreground/90"
          )}
        >
          {entry.username}
        </span>
        <span
          className="flex-shrink-0 text-base leading-none"
          title={entry.jedi_rank}
          aria-label={entry.jedi_rank}
        >
          {JEDI_RANK_ICONS[entry.jedi_rank] ?? "🌟"}
        </span>
        {entry.is_current_user && (
          <span
            className="flex-shrink-0 text-xs bg-primary text-primary-foreground font-bold px-2 py-0.5 rounded-full"
            aria-label={tYou}
          >
            {tYou}
          </span>
        )}
        {entry.current_streak > 0 && (
          <span
            className="flex items-center gap-0.5 flex-shrink-0 text-xs text-muted-foreground"
            title={tStreak}
            aria-label={tStreak}
          >
            <Flame className="h-3.5 w-3.5 text-orange-400 shrink-0" aria-hidden />
            {entry.current_streak}
          </span>
        )}
        {entry.badges_count > 0 && (
          <span
            className="flex items-center gap-0.5 flex-shrink-0 text-xs text-muted-foreground"
            title={tBadges}
            aria-label={tBadges}
          >
            <Award className="h-3.5 w-3.5 text-amber-500/90 shrink-0" aria-hidden />
            {entry.badges_count}
          </span>
        )}
      </div>

      <span className="hidden sm:block flex-shrink-0 text-sm text-muted-foreground">
        {tLevel} {entry.current_level}
      </span>

      <span className="flex-shrink-0 text-base font-bold text-amber-400 tabular-nums">
        {entry.total_points.toLocaleString()}
        <span className="text-xs font-normal text-amber-400/70 ml-0.5">pts</span>
      </span>
    </li>
  );
}

// ─── Page principale ──────────────────────────────────────────────────────────

export default function LeaderboardPage() {
  const t = useTranslations("leaderboard");
  useAuth();
  const { leaderboard, isLoading, error } = useLeaderboard(50);

  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout>
        <PageHeader title={t("title")} description={t("description")} icon={Trophy} />

        <PageSection>
          <Card className="card-spatial-depth overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Medal className="h-5 w-5 text-amber-400" aria-hidden />
                {t("ranking")}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 min-h-[120px]">
              {error ? (
                <div className="p-6">
                  <EmptyState title={t("error") ?? "Erreur de chargement"} description="" icon={Trophy} />
                </div>
              ) : isLoading ? (
                <div className="p-6">
                  <LoadingState message={t("loading")} />
                </div>
              ) : leaderboard.length === 0 ? (
                <div className="p-6">
                  <EmptyState title={t("empty")} description="" icon={Medal} />
                </div>
              ) : (
                <ul role="list" aria-label={t("ranking")}>
                  {leaderboard.map((entry: LeaderboardEntry, idx: number) => (
                    <LeaderboardRow
                      key={`${entry.rank}-${entry.username}`}
                      entry={entry}
                      isLast={idx === leaderboard.length - 1}
                      tLevel={t("level")}
                      tYou={t("you")}
                      tRank={t("rank", { default: "Rang" })}
                      tStreak={t("streakStat", { default: "Série en jours" })}
                      tBadges={t("badgesStat", { default: "Badges obtenus" })}
                    />
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
