"use client";

import { CardHeader } from "@/components/ui/card";
import { CheckCircle, Heart, Trophy } from "lucide-react";
import type { BadgeWithCriteria } from "@/lib/badges/types";
import { resolveIconGlowClass } from "@/lib/badges/badgePresentation";
import { cn } from "@/lib/utils";
import { BadgeIcon } from "@/components/badges/BadgeIcon";
import { BadgeCardDifficultyMedal } from "@/components/badges/badgeCard/BadgeCardDifficultyMedal";

/** Aligné sur la forme des `values` acceptés par `useTranslations("badges")` (next-intl). */
export type BadgeCardBadgesT = (
  key: string,
  values?: Record<string, string | number | Date>
) => string;

interface BadgeCardCompactEarnedHeaderProps {
  badge: BadgeWithCriteria;
  canPin?: boolean | undefined;
  onTogglePin?: ((badgeId: number) => void) | undefined;
  isPinned?: boolean | undefined;
  t: BadgeCardBadgesT;
}

export function BadgeCardCompactEarnedHeader({
  badge,
  canPin,
  onTogglePin,
  isPinned,
  t,
}: BadgeCardCompactEarnedHeaderProps) {
  return (
    <CardHeader className="relative p-3 pt-4 flex flex-col items-center text-center gap-1.5">
      <div className="absolute top-2 right-2 flex items-center gap-0.5">
        {canPin && onTogglePin && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onTogglePin(badge.id);
            }}
            className={cn(
              "p-1 rounded-full transition-all",
              isPinned
                ? "text-rose-400"
                : "text-muted-foreground/50 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 hover:text-rose-400"
            )}
            aria-label={isPinned ? t("unpin") : t("pin")}
            title={isPinned ? t("unpin") : t("pin")}
          >
            <Heart className={cn("h-3.5 w-3.5", isPinned && "fill-rose-400")} aria-hidden="true" />
          </button>
        )}
        <CheckCircle className="h-3.5 w-3.5 text-green-400 shrink-0" aria-hidden="true" />
      </div>

      <div className="relative flex items-center justify-center mt-1">
        <div className={cn("badge-icon-glow", resolveIconGlowClass(badge.difficulty))} />
        <BadgeIcon
          code={badge.code}
          iconUrl={badge.icon_url}
          category={badge.category}
          difficulty={badge.difficulty}
          size="md"
          isEarned
        />
      </div>

      <p
        className="text-xs font-semibold leading-tight line-clamp-1 w-full px-1"
        title={badge.name || badge.code || ""}
      >
        {badge.name || badge.code || t("noName")}
      </p>
      <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
        <BadgeCardDifficultyMedal difficulty={badge.difficulty} size="xs" />
        <Trophy className="h-3 w-3 text-yellow-500 shrink-0" aria-hidden="true" />
        <span className="tabular-nums">{badge.points_reward} pts</span>
      </div>
    </CardHeader>
  );
}
