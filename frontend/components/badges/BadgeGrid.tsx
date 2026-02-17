"use client";

import { BadgeCard } from "./BadgeCard";
import type { Badge, UserBadge } from "@/types/api";
import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

interface BadgeProgress {
  current: number;
  target: number;
  progress: number;
}

export type BadgeSortBy = "progress" | "date" | "points" | "category";

export interface RarityInfo {
  unlock_count: number;
  unlock_percent: number;
  rarity: string;
}

interface BadgeGridProps {
  badges: Badge[];
  earnedBadges: UserBadge[];
  progressMap?: Record<number, BadgeProgress>;
  isLoading?: boolean;
  sortBy?: BadgeSortBy;
  rarityMap?: Record<string, RarityInfo>;
  pinnedBadgeIds?: number[];
  onTogglePin?: (badgeId: number) => void;
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
}: BadgeGridProps) {
  const { shouldReduceMotion, createTransition } = useAccessibleAnimation();

  // Créer un map des badges obtenus pour accès rapide (par ID)
  const earnedBadgeMap = new Map<number, UserBadge>();
  earnedBadges.forEach((userBadge) => {
    earnedBadgeMap.set(userBadge.id, userBadge);
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Filtrer les badges invalides (sans nom ou code)
  const validBadges = badges.filter((badge) => {
    return badge.name || badge.code;
  });

  if (validBadges.length === 0) {
    return (
      <div className="text-center py-12" role="status" aria-live="polite">
        <p className="text-muted-foreground text-base">Aucun badge disponible pour le moment.</p>
      </div>
    );
  }

  // Trier les badges selon sortBy (A-3)
  const sortedBadges = [...validBadges].sort((a, b) => {
    const aEarned = earnedBadgeMap.has(a.id);
    const bEarned = earnedBadgeMap.has(b.id);

    if (sortBy === "progress") {
      const aProg = progressMap?.[a.id]?.progress ?? (aEarned ? 1 : 0);
      const bProg = progressMap?.[b.id]?.progress ?? (bEarned ? 1 : 0);
      return bProg - aProg;
    }
    if (sortBy === "date") {
      const aDate = earnedBadgeMap.get(a.id)?.earned_at ?? "";
      const bDate = earnedBadgeMap.get(b.id)?.earned_at ?? "";
      if (aDate && bDate) return new Date(bDate).getTime() - new Date(aDate).getTime();
      if (aDate) return -1;
      if (bDate) return 1;
      return 0;
    }
    if (sortBy === "points") {
      const aPt = a.points_reward ?? a.points ?? 0;
      const bPt = b.points_reward ?? b.points ?? 0;
      return bPt - aPt;
    }

    // category (défaut) : obtenus en premier, puis catégorie, difficulté
    if (aEarned && !bEarned) return -1;
    if (!aEarned && bEarned) return 1;
    const categoryOrder: Record<string, number> = { progression: 0, mastery: 1, special: 2 };
    const aCategory = a.category || "";
    const bCategory = b.category || "";
    const categoryDiff = (categoryOrder[aCategory] ?? 999) - (categoryOrder[bCategory] ?? 999);
    if (categoryDiff !== 0) return categoryDiff;
    const difficultyOrder: Record<string, number> = { bronze: 0, silver: 1, gold: 2, legendary: 3 };
    const aDifficulty = a.difficulty || "";
    const bDifficulty = b.difficulty || "";
    return (difficultyOrder[aDifficulty] ?? 999) - (difficultyOrder[bDifficulty] ?? 999);
  });

  // Variantes pour le conteneur avec staggerChildren
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
      className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 items-stretch"
      variants={containerVariants}
      initial="hidden"
      animate="show"
      role="list"
      aria-label="Collection de badges"
    >
      {sortedBadges.map((badge, index) => {
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
            rarity={rarityMap?.[String(badge.id)]}
            isPinned={pinnedBadgeIds?.includes(badge.id)}
            onTogglePin={onTogglePin}
            canPin={pinnedBadgeIds != null && (pinnedBadgeIds?.includes(badge.id) || (pinnedBadgeIds?.length ?? 0) < 3)}
          />
        );
      })}
    </motion.div>
  );
}
