"use client";

import { motion, type Variants } from "framer-motion";
import { Flame, Award } from "lucide-react";
import { UserAvatar } from "@/components/ui/UserAvatar";
import { cn } from "@/lib/utils";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";
import {
  PROGRESSION_RANK_ICONS,
  PROGRESSION_RANK_TEXT_CLASS,
  leaderboardPodiumSurfaceClass,
} from "@/lib/constants/leaderboard";
import {
  canonicalProgressionRankBucket,
  readPublicProgressionRankRaw,
} from "@/lib/gamification/progressionRankLabel";
import { LeaderboardRankBadge } from "@/components/leaderboard/LeaderboardRankBadge";
import { LeaderboardAnimatedPoints } from "@/components/leaderboard/LeaderboardAnimatedPoints";

export interface LeaderboardRowProps {
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

export function LeaderboardRow({
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
  const bucketRaw = readPublicProgressionRankRaw(entry);
  const rankCanon = canonicalProgressionRankBucket(bucketRaw);
  const rankClass = PROGRESSION_RANK_TEXT_CLASS[rankCanon] ?? "text-muted-foreground";
  const rankReadable = progressionRankLabel(bucketRaw);
  const isPodium = entry.rank >= 1 && entry.rank <= 3;

  const avatarHaloClass =
    entry.rank === 1
      ? "lb-avatar-halo-1"
      : entry.rank === 2
        ? "lb-avatar-halo-2"
        : entry.rank === 3
          ? "lb-avatar-halo-3"
          : undefined;

  return (
    <motion.li
      variants={rowVariants}
      custom={entry.rank}
      {...(!shouldReduceMotion ? { whileHover: { y: -1 } } : {})}
      className={cn(
        "lb-row-reveal",
        "flex flex-wrap sm:flex-nowrap items-center gap-2 sm:gap-4 px-3 sm:px-4",
        isPodium ? "py-4" : "py-3",
        "transition-colors duration-200",
        !isLast && "border-b border-border/40",
        "border-l-4",
        entry.is_current_user
          ? "bg-primary/10 border-l-primary lb-row-self"
          : cn(leaderboardPodiumSurfaceClass(entry.rank), "border-l-transparent")
      )}
    >
      <LeaderboardRankBadge rank={entry.rank} label={`${tRank} ${entry.rank}`} />

      {avatarHaloClass ? (
        <span className={cn("inline-flex flex-shrink-0", avatarHaloClass)}>
          <UserAvatar username={entry.username} size="md" avatarUrl={entry.avatar_url} />
        </span>
      ) : (
        <UserAvatar username={entry.username} size="md" avatarUrl={entry.avatar_url} />
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span
            className={cn(
              "font-semibold truncate max-w-[40vw] sm:max-w-none",
              isPodium ? "text-base" : "text-sm",
              entry.is_current_user ? "text-foreground" : "text-foreground/90"
            )}
          >
            {entry.username}
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
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className={cn("text-xs leading-none", rankClass)} aria-label={rankReadable}>
            {PROGRESSION_RANK_ICONS[rankCanon] ?? "🌟"}
          </span>
          <span className="text-xs text-muted-foreground">{rankReadable}</span>
          <span className="text-xs text-muted-foreground/50 hidden sm:inline">·</span>
          <span className="hidden sm:inline text-xs text-muted-foreground">
            {tLevel} {entry.current_level}
          </span>
        </div>
      </div>

      <LeaderboardAnimatedPoints value={entry.total_points} rank={entry.rank} />
    </motion.li>
  );
}
