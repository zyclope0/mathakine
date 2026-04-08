"use client";

import { BadgeCard } from "./BadgeCard";
import type { Badge, UserBadge } from "@/types/api";
import { LoadingState } from "@/components/layout/LoadingState";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { cn } from "@/lib/utils";
import type { BadgeProgressSnapshot, BadgeSortBy, RarityInfo } from "@/lib/badges/types";
import {
  buildEarnedUserBadgeMap,
  filterBadgesWithNameOrCode,
  sortBadgesForGrid,
} from "@/lib/badges/badgePresentation";

export type { BadgeSortBy, RarityInfo } from "@/lib/badges/types";

interface BadgeGridProps {
  badges: Badge[];
  earnedBadges: UserBadge[];
  progressMap?: Record<number, BadgeProgressSnapshot>;
  isLoading?: boolean;
  sortBy?: BadgeSortBy;
  rarityMap?: Record<string, RarityInfo>;
  pinnedBadgeIds?: number[];
  onTogglePin?: (badgeId: number) => void;
  compactEarned?: boolean;
  /** Limite le nombre de badges affichés (pour tiroir replié) */
  limit?: number;
}

export function BadgeGrid({
  badges,
  earnedBadges,
  progressMap,
  isLoading,
  sortBy = "category",
  rarityMap,
  pinnedBadgeIds,
  onTogglePin,
  compactEarned = false,
  limit,
}: BadgeGridProps) {
  const { shouldReduceMotion } = useAccessibleAnimation();

  const earnedBadgeMap = buildEarnedUserBadgeMap(earnedBadges);

  if (isLoading) {
    return <LoadingState className="min-h-0 py-12" />;
  }

  const validBadges = filterBadgesWithNameOrCode(badges);

  if (validBadges.length === 0) {
    return (
      <div className="text-center py-12" role="status" aria-live="polite">
        <p className="text-muted-foreground text-base">Aucun badge disponible pour le moment.</p>
      </div>
    );
  }

  const sortedBadges = sortBadgesForGrid(validBadges, earnedBadgeMap, progressMap, sortBy);

  const displayBadges = limit != null ? sortedBadges.slice(0, limit) : sortedBadges;

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.05,
        delayChildren: 0.1,
      },
    },
  };

  return (
    <motion.div
      className={cn(
        "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 min-[1600px]:grid-cols-6 items-stretch",
        compactEarned ? "gap-3" : "gap-4"
      )}
      variants={containerVariants}
      initial="hidden"
      animate="show"
      role="list"
      aria-label="Collection de badges"
    >
      {displayBadges.map((badge, index) => {
        const userBadge = earnedBadgeMap.get(badge.id);
        const badgeProgress = progressMap?.[badge.id];
        return (
          <BadgeCard
            key={badge.id}
            badge={badge}
            userBadge={userBadge ?? null}
            isEarned={!!userBadge}
            progress={badgeProgress ?? null}
            index={index}
            rarity={rarityMap?.[String(badge.id)] ?? null}
            isPinned={pinnedBadgeIds?.includes(badge.id) ?? false}
            compact={compactEarned && !!userBadge}
            {...(onTogglePin != null && { onTogglePin })}
            canPin={
              pinnedBadgeIds != null &&
              (pinnedBadgeIds?.includes(badge.id) || (pinnedBadgeIds?.length ?? 0) < 3)
            }
          />
        );
      })}
    </motion.div>
  );
}
