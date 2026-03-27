"use client";

import { useMemo, useState } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useLeaderboard, type LeaderboardPeriod } from "@/hooks/useLeaderboard";
import { useMyLeaderboardRank } from "@/hooks/useMyLeaderboardRank";
import { Trophy, Medal, Flame, Award } from "lucide-react";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState, EmptyState } from "@/components/layout";
import { cn } from "@/lib/utils";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";
import {
  RANK_MEDALS,
  PROGRESSION_RANK_ICONS,
  PROGRESSION_RANK_TEXT_CLASS,
  leaderboardPodiumSurfaceClass,
} from "@/lib/constants/leaderboard";
import {
  canonicalProgressionRankBucket,
  isKnownProgressionRankBucket,
} from "@/lib/gamification/progressionRankLabel";
import { UserAvatar } from "@/components/ui/UserAvatar";
import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

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
  rowVariants: Variants;
  shouldReduceMotion: boolean;
  progressionRankLabel: (bucket: string) => string;
}

function LeaderboardRow({
  entry,
  isLast,
  tLevel,
  tYou,
  tRank,
  tStreak,
  tBadges,
  rowVariants,
  shouldReduceMotion,
  progressionRankLabel,
}: LeaderboardRowProps) {
  const rankCanon = canonicalProgressionRankBucket(entry.jedi_rank);
  const rankClass = PROGRESSION_RANK_TEXT_CLASS[rankCanon] ?? "text-muted-foreground";
  const rankReadable = progressionRankLabel(entry.jedi_rank);

  return (
    <motion.li
      variants={rowVariants}
      custom={entry.rank}
      {...(!shouldReduceMotion ? { whileHover: { y: -2 } } : {})}
      className={cn(
        "flex flex-wrap sm:flex-nowrap items-center gap-2 sm:gap-4 px-3 sm:px-4 py-3",
        "cursor-default transition-shadow duration-300",
        "hover:shadow-md hover:shadow-primary/5",
        !isLast && "border-b border-border/40",
        entry.is_current_user
          ? "bg-primary/10 border-l-4 border-l-primary"
          : cn(leaderboardPodiumSurfaceClass(entry.rank), "border-l-4 border-l-transparent")
      )}
    >
      <RankBadge rank={entry.rank} label={`${tRank} ${entry.rank}`} />

      <UserAvatar username={entry.username} size="md" avatarUrl={entry.avatar_url} />

      <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
        <span
          className={cn(
            "font-semibold truncate max-w-[40vw] sm:max-w-none",
            entry.is_current_user ? "text-foreground" : "text-foreground/90"
          )}
        >
          {entry.username}
        </span>
        <span
          className={cn("flex-shrink-0 text-base leading-none", rankClass)}
          title={rankReadable}
          aria-label={rankReadable}
        >
          {PROGRESSION_RANK_ICONS[rankCanon] ?? "🌟"}
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

      <span className="flex-shrink-0 text-sm sm:text-base font-bold text-amber-400 tabular-nums">
        {entry.total_points.toLocaleString()}
        <span className="text-xs font-normal text-amber-400/70 ml-0.5">pts</span>
      </span>
    </motion.li>
  );
}

// ─── Page principale ──────────────────────────────────────────────────────────

export default function LeaderboardPage() {
  const t = useTranslations("leaderboard");
  const tProgRank = useTranslations("progressionRanks");
  const progressionRankLabel = (bucket: string) => {
    const c = canonicalProgressionRankBucket(bucket);
    return isKnownProgressionRankBucket(bucket) ? tProgRank(c) : bucket;
  };
  const { user } = useAuth();
  const [period, setPeriod] = useState<LeaderboardPeriod>("all");
  const { leaderboard, isLoading, error } = useLeaderboard(50, period);
  const { shouldReduceMotion } = useAccessibleAnimation();

  const inTop = useMemo(() => leaderboard.some((e) => e.is_current_user), [leaderboard]);
  const fetchMyRankEnabled = !isLoading && !error && leaderboard.length > 0 && !inTop;
  const {
    data: myRank,
    isLoading: myRankLoading,
    isError: myRankError,
  } = useMyLeaderboardRank(fetchMyRankEnabled, period);

  const showMyRankFooter =
    fetchMyRankEnabled && Boolean(user) && Boolean(myRank) && !myRankLoading && !myRankError;

  const listVariants: Variants = shouldReduceMotion
    ? { hidden: {}, show: {} }
    : {
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: { staggerChildren: 0.055, delayChildren: 0.03 },
        },
      };

  const rowVariants: Variants = shouldReduceMotion
    ? { hidden: { opacity: 0 }, show: { opacity: 1 } }
    : {
        hidden: { opacity: 0, y: 10, scale: 0.98 },
        show: (rank: number) => ({
          opacity: 1,
          y: 0,
          scale: typeof rank === "number" && rank >= 1 && rank <= 3 ? 1.02 : 1,
          transition: { duration: 0.22, ease: [0.4, 0, 0.2, 1] },
        }),
      };

  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout>
        <PageHeader title={t("title")} description={t("description")} icon={Trophy} />

        <PageSection>
          <Card className="card-spatial-depth overflow-hidden">
            <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4 space-y-0">
              <CardTitle className="flex items-center gap-2">
                <Medal className="h-5 w-5 text-amber-400" aria-hidden />
                {t("ranking")}
              </CardTitle>
              <div className="flex w-full flex-col gap-1.5 sm:w-auto sm:min-w-[220px]">
                <span className="text-xs text-muted-foreground" id="leaderboard-period-label">
                  {t("period.label")}
                </span>
                <Select
                  value={period}
                  onValueChange={(value) => setPeriod(value as LeaderboardPeriod)}
                >
                  <SelectTrigger
                    aria-labelledby="leaderboard-period-label"
                    className="w-full"
                    size="sm"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">{t("period.all")}</SelectItem>
                    <SelectItem value="week">{t("period.week")}</SelectItem>
                    <SelectItem value="month">{t("period.month")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent className="p-0 min-h-[120px]">
              {error ? (
                <div className="p-6">
                  <EmptyState
                    title={t("error") ?? "Erreur de chargement"}
                    description=""
                    icon={Trophy}
                  />
                </div>
              ) : isLoading ? (
                <div className="p-6">
                  <LoadingState message={t("loading")} />
                </div>
              ) : leaderboard.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    title={t("emptyState.title")}
                    description={t("emptyState.description")}
                    icon={Medal}
                    action={
                      <Button asChild variant="default">
                        <Link href="/challenges">{t("emptyState.cta")}</Link>
                      </Button>
                    }
                  />
                </div>
              ) : (
                <>
                  <motion.ul
                    role="list"
                    aria-label={t("ranking")}
                    variants={listVariants}
                    initial="hidden"
                    animate="show"
                    className="list-none m-0 p-0"
                  >
                    {leaderboard.map((entry: LeaderboardEntry, idx: number) => (
                      <LeaderboardRow
                        key={`${entry.rank}-${entry.username}`}
                        entry={entry}
                        isLast={idx === leaderboard.length - 1 && !showMyRankFooter}
                        tLevel={t("level")}
                        tYou={t("you")}
                        tRank={t("rank")}
                        tStreak={t("streakStat")}
                        tBadges={t("badgesStat")}
                        rowVariants={rowVariants}
                        shouldReduceMotion={Boolean(shouldReduceMotion)}
                        progressionRankLabel={progressionRankLabel}
                      />
                    ))}
                  </motion.ul>
                  {showMyRankFooter && user && myRank ? (
                    <div className="border-t border-border/50 bg-muted/20">
                      <div
                        className="px-3 sm:px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wide"
                        role="separator"
                      >
                        {t("yourRank.separator")}
                      </div>
                      <div
                        className={cn(
                          "flex flex-wrap sm:flex-nowrap items-center gap-2 sm:gap-4 px-3 sm:px-4 py-3",
                          "bg-primary/10 border-l-4 border-l-primary"
                        )}
                      >
                        <RankBadge
                          rank={myRank.rank}
                          label={`${t("rank", { default: "Rang" })} ${myRank.rank}`}
                        />
                        <UserAvatar username={user.username} size="md" />
                        <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
                          <span className="font-semibold truncate max-w-[40vw] sm:max-w-none text-foreground">
                            {user.username}
                          </span>
                          {user.jedi_rank ? (
                            <span
                              className={cn(
                                "flex-shrink-0 text-base leading-none",
                                PROGRESSION_RANK_TEXT_CLASS[
                                  canonicalProgressionRankBucket(user.jedi_rank)
                                ] ?? "text-muted-foreground"
                              )}
                              title={progressionRankLabel(user.jedi_rank)}
                              aria-label={progressionRankLabel(user.jedi_rank)}
                            >
                              {PROGRESSION_RANK_ICONS[
                                canonicalProgressionRankBucket(user.jedi_rank)
                              ] ?? "🌟"}
                            </span>
                          ) : null}
                          <span
                            className="flex-shrink-0 text-xs bg-primary text-primary-foreground font-bold px-2 py-0.5 rounded-full"
                            aria-label={t("you")}
                          >
                            {t("you")}
                          </span>
                        </div>
                        <span className="hidden sm:block flex-shrink-0 text-sm text-muted-foreground">
                          {t("level")} {user.current_level ?? "—"}
                        </span>
                        <span className="flex-shrink-0 text-sm sm:text-base font-bold text-amber-400 tabular-nums">
                          {myRank.total_points.toLocaleString()}
                          <span className="text-xs font-normal text-amber-400/70 ml-0.5">pts</span>
                        </span>
                      </div>
                    </div>
                  ) : null}
                </>
              )}
            </CardContent>
          </Card>
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
