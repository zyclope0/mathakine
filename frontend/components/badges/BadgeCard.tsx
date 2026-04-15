"use client";

import { Card } from "@/components/ui/card";
import { useTranslations, useLocale } from "next-intl";
import type { UserBadge } from "@/types/api";
import type { BadgeProgressSnapshot, BadgeWithCriteria, RarityInfo } from "@/lib/badges/types";
import {
  resolveCompactHighProgressMotivation,
  shouldShowLockedMidMotivationLine,
  shouldShowLockedZeroMotivationLine,
} from "@/lib/badges/badgePresentation";
import { cn } from "@/lib/utils";
import { motion, type Variants, type Transition } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { readBadgeThematicTitleRaw } from "@/lib/gamification/badgeThematicTitle";
import { BadgeCardCompactEarnedHeader } from "@/components/badges/badgeCard/BadgeCardCompactEarnedHeader";
import { BadgeCardStandardHeader } from "@/components/badges/badgeCard/BadgeCardStandardHeader";
import { BadgeCardCardContent } from "@/components/badges/badgeCard/BadgeCardCardContent";

export interface BadgeCardProps {
  badge: BadgeWithCriteria;
  userBadge?: UserBadge | null;
  isEarned: boolean;
  progress?: BadgeProgressSnapshot | null;
  index?: number;
  rarity?: RarityInfo | null;
  isPinned?: boolean;
  onTogglePin?: (badgeId: number) => void;
  canPin?: boolean;
  compact?: boolean;
}

export function BadgeCard({
  badge,
  userBadge,
  isEarned,
  progress,
  index = 0,
  rarity,
  isPinned,
  onTogglePin,
  canPin,
  compact = false,
}: BadgeCardProps) {
  const t = useTranslations("badges");
  const locale = useLocale();
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  const thematicLine = readBadgeThematicTitleRaw(badge);

  const lockedHighMotivation =
    progress != null && progress.target > 0 && progress.progress >= 0.5
      ? resolveCompactHighProgressMotivation(
          progress.current,
          progress.target,
          progress.progress,
          progress.progress_detail
        )
      : null;

  const lockedMidMotivationVisible =
    progress != null &&
    shouldShowLockedMidMotivationLine(
      progress.current,
      progress.target,
      progress.progress,
      progress.progress_detail
    );

  const lockedZeroMotivationVisible =
    progress != null && shouldShowLockedZeroMotivationLine(progress.progress, progress.target);

  const variants = createVariants({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  });

  const transition = createTransition({
    duration: 0.3,
    delay: index * 0.05,
  });

  return (
    <motion.div
      variants={variants as Variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition as Transition}
      className="h-full"
    >
      <Card
        className={cn(
          "card-spatial-depth badge-card-glass relative overflow-hidden transition-[transform,opacity,box-shadow] duration-300 h-full flex flex-col",
          "motion-reduce:transition-none",
          isEarned ? "cursor-pointer" : "opacity-60",
          isEarned &&
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-xl",
          isEarned && "badge-card-earned-compact group",
          badge.difficulty === "gold" && "shadow-lg shadow-yellow-500/10",
          badge.difficulty === "legendary" &&
            "ring-1 ring-amber-400/20 shadow-lg shadow-amber-400/15"
        )}
        role="article"
        aria-label={t("ariaLabel", {
          name: badge.name || t("noName"),
          status: isEarned ? t("earned") : t("locked"),
        })}
        tabIndex={isEarned ? 0 : undefined}
        title={isEarned ? t("expandHint") : undefined}
      >
        {compact && isEarned ? (
          <BadgeCardCompactEarnedHeader
            badge={badge}
            canPin={canPin}
            onTogglePin={onTogglePin}
            isPinned={isPinned}
            t={t}
          />
        ) : (
          <BadgeCardStandardHeader
            badge={badge}
            isEarned={isEarned}
            thematicLine={thematicLine}
            rarity={rarity}
            canPin={canPin}
            onTogglePin={onTogglePin}
            isPinned={isPinned}
            t={t}
          />
        )}
        <BadgeCardCardContent
          compact={compact}
          isEarned={isEarned}
          badge={badge}
          userBadge={userBadge}
          progress={progress}
          rarity={rarity}
          thematicLine={thematicLine}
          locale={locale}
          lockedHighMotivation={lockedHighMotivation}
          lockedMidMotivationVisible={lockedMidMotivationVisible}
          lockedZeroMotivationVisible={lockedZeroMotivationVisible}
          t={t}
        />
        {isEarned && !shouldReduceMotion && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-shimmer pointer-events-none" />
        )}
      </Card>
    </motion.div>
  );
}
