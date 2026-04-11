"use client";

import React from "react";
import { motion, type Variants } from "framer-motion";
import type { LeaderboardEntry } from "@/hooks/useLeaderboard";
import { LeaderboardRow } from "@/components/leaderboard/LeaderboardRow";
import { LeaderboardSectionSeparator } from "@/components/leaderboard/LeaderboardSectionSeparator";

export interface LeaderboardListProps {
  leaderboard: LeaderboardEntry[];
  showMyRankFooter: boolean;
  listVariants: Variants;
  rowVariants: Variants;
  shouldReduceMotion: boolean;
  progressionRankLabel: (bucket: string) => string;
  tRankingAria: string;
  tLevel: string;
  tYou: string;
  tRank: string;
  tStreak: string;
  tBadges: string;
  podiumSeparator: string;
  topTenSeparator: string;
  restSeparator: string;
}

export function LeaderboardList({
  leaderboard,
  showMyRankFooter,
  listVariants,
  rowVariants,
  shouldReduceMotion,
  progressionRankLabel,
  tRankingAria,
  tLevel,
  tYou,
  tRank,
  tStreak,
  tBadges,
  podiumSeparator,
  topTenSeparator,
  restSeparator,
}: LeaderboardListProps) {
  return (
    <motion.ul
      role="list"
      aria-label={tRankingAria}
      variants={listVariants}
      initial="hidden"
      animate="show"
      className="list-none m-0 p-0"
    >
      {leaderboard.flatMap((entry: LeaderboardEntry, idx: number) => {
        const isLastEntry = idx === leaderboard.length - 1 && !showMyRankFooter;
        const nodes: React.ReactNode[] = [];

        if (idx === 0)
          nodes.push(<LeaderboardSectionSeparator key="sep-podium" label={podiumSeparator} />);
        if (entry.rank === 4)
          nodes.push(<LeaderboardSectionSeparator key="sep-top10" label={topTenSeparator} />);
        if (entry.rank === 11)
          nodes.push(<LeaderboardSectionSeparator key="sep-rest" label={restSeparator} />);

        nodes.push(
          <LeaderboardRow
            key={`${entry.rank}-${entry.username}`}
            entry={entry}
            isLast={isLastEntry}
            tLevel={tLevel}
            tYou={tYou}
            tRank={tRank}
            tStreak={tStreak}
            tBadges={tBadges}
            rowVariants={rowVariants}
            shouldReduceMotion={shouldReduceMotion}
            progressionRankLabel={progressionRankLabel}
          />
        );

        return nodes;
      })}
    </motion.ul>
  );
}
