"use client";

import type { PublicRankBucketSource } from "@/lib/gamification/progressionRankLabel";
import { canonicalProgressionRankBucket } from "@/lib/gamification/progressionRankLabel";
import { UserAvatar } from "@/components/ui/UserAvatar";
import { cn } from "@/lib/utils";
import { PROGRESSION_RANK_ICONS, PROGRESSION_RANK_TEXT_CLASS } from "@/lib/constants/leaderboard";
import { LeaderboardRankBadge } from "@/components/leaderboard/LeaderboardRankBadge";
import { LeaderboardAnimatedPoints } from "@/components/leaderboard/LeaderboardAnimatedPoints";

export interface MyRankFooterUser extends PublicRankBucketSource {
  username: string;
  current_level?: number | null;
}

export interface LeaderboardCurrentUserFooterProps {
  user: MyRankFooterUser;
  myRank: { rank: number; total_points: number };
  myRankBucketRaw: string;
  tSeparator: string;
  tYou: string;
  tLevel: string;
  rankBadgeAriaPrefix: string;
  progressionRankLabel: (bucket: string) => string;
}

export function LeaderboardCurrentUserFooter({
  user,
  myRank,
  myRankBucketRaw,
  tSeparator,
  tYou,
  tLevel,
  rankBadgeAriaPrefix,
  progressionRankLabel,
}: LeaderboardCurrentUserFooterProps) {
  return (
    <div className="border-t border-border/50 bg-muted/20">
      <div
        className="px-3 sm:px-4 py-2 text-xs font-semibold text-muted-foreground tracking-normal"
        role="separator"
      >
        {tSeparator}
      </div>
      <div
        className={cn(
          "flex flex-wrap sm:flex-nowrap items-center gap-2 sm:gap-4 px-3 sm:px-4 py-3",
          "bg-primary/10 border-l-4 border-l-primary lb-row-self"
        )}
      >
        <LeaderboardRankBadge rank={myRank.rank} label={`${rankBadgeAriaPrefix} ${myRank.rank}`} />
        <UserAvatar username={user.username} size="md" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="font-semibold truncate max-w-[40vw] sm:max-w-none text-foreground text-sm">
              {user.username}
            </span>
            <span
              className="flex-shrink-0 text-xs bg-primary text-primary-foreground font-bold px-2 py-0.5 rounded-full"
              aria-label={tYou}
            >
              {tYou}
            </span>
          </div>
          {myRankBucketRaw ? (
            <div className="flex items-center gap-1.5 mt-0.5">
              <span
                className={cn(
                  "text-xs leading-none",
                  PROGRESSION_RANK_TEXT_CLASS[canonicalProgressionRankBucket(myRankBucketRaw)] ??
                    "text-muted-foreground"
                )}
                aria-label={progressionRankLabel(myRankBucketRaw)}
              >
                {PROGRESSION_RANK_ICONS[canonicalProgressionRankBucket(myRankBucketRaw)] ?? "🌟"}
              </span>
              <span className="text-xs text-muted-foreground">
                {progressionRankLabel(myRankBucketRaw)}
              </span>
              {user.current_level != null && (
                <>
                  <span className="text-xs text-muted-foreground/50 hidden sm:inline">·</span>
                  <span className="hidden sm:inline text-xs text-muted-foreground">
                    {tLevel} {user.current_level}
                  </span>
                </>
              )}
            </div>
          ) : null}
        </div>
        <LeaderboardAnimatedPoints value={myRank.total_points} rank={myRank.rank} />
      </div>
    </div>
  );
}
