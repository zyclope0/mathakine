"use client";

import { CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge as BadgeComponent } from "@/components/ui/badge";
import { Trophy, Lock, CheckCircle, Heart } from "lucide-react";
import type { BadgeWithCriteria, RarityInfo } from "@/lib/badges/types";
import type { DifficultyPresentationClasses } from "@/lib/badges/badgePresentation";
import { getDifficultyPresentationClasses, isRareRarityInfo } from "@/lib/badges/badgePresentation";
import { cn } from "@/lib/utils";
import { BadgeIcon } from "@/components/badges/BadgeIcon";
import { BadgeCardDifficultyMedal } from "@/components/badges/badgeCard/BadgeCardDifficultyMedal";
import type { BadgeCardBadgesT } from "@/components/badges/badgeCard/BadgeCardCompactEarnedHeader";

interface BadgeCardStandardHeaderProps {
  badge: BadgeWithCriteria;
  isEarned: boolean;
  thematicLine: string;
  rarity?: RarityInfo | null | undefined;
  canPin?: boolean | undefined;
  onTogglePin?: ((badgeId: number) => void) | undefined;
  isPinned?: boolean | undefined;
  t: BadgeCardBadgesT;
}

export function BadgeCardStandardHeader({
  badge,
  isEarned,
  thematicLine,
  rarity,
  canPin,
  onTogglePin,
  isPinned,
  t,
}: BadgeCardStandardHeaderProps) {
  const difficultyColor: DifficultyPresentationClasses = getDifficultyPresentationClasses(
    badge.difficulty
  );

  return (
    <CardHeader className={cn("pb-4", isEarned && "pb-2")}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <CardTitle
            className={cn(
              "flex items-center gap-2 font-bold",
              isEarned ? "text-base md:text-lg" : "text-lg md:text-xl"
            )}
          >
            {!isEarned ? (
              <div className="relative shrink-0">
                <BadgeIcon
                  code={badge.code}
                  iconUrl={badge.icon_url}
                  category={badge.category}
                  difficulty={badge.difficulty}
                  size="md"
                  isEarned={false}
                />
                <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-background/50">
                  <Lock className="h-4 w-4 text-muted-foreground/70" aria-hidden="true" />
                </div>
              </div>
            ) : (
              <BadgeIcon
                code={badge.code}
                iconUrl={badge.icon_url}
                category={badge.category}
                difficulty={badge.difficulty}
                size="sm"
                isEarned
              />
            )}
            <span className="break-words">{badge.name || badge.code || t("noName")}</span>
          </CardTitle>
          {!isEarned && thematicLine && (
            <CardDescription className="mt-2 text-primary-on-dark italic text-sm">
              {thematicLine}
            </CardDescription>
          )}
          {isEarned && (
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <BadgeCardDifficultyMedal difficulty={badge.difficulty} size="sm" />
              <span>
                <Trophy className="inline h-3.5 w-3.5 text-yellow-500 mr-0.5" aria-hidden="true" />
                {badge.points_reward} pts
              </span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
          {isEarned && (
            <>
              {canPin && onTogglePin && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    onTogglePin(badge.id);
                  }}
                  className={cn(
                    "p-1.5 rounded-full transition-all shrink-0",
                    isPinned
                      ? "bg-rose-500/20 text-rose-400 opacity-100"
                      : "text-muted-foreground hover:text-rose-400 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                  )}
                  aria-label={isPinned ? t("unpin") : t("pin")}
                  title={isPinned ? t("unpin") : t("pin")}
                >
                  <Heart
                    className={cn("h-4.5 w-4.5", isPinned && "fill-rose-400")}
                    aria-hidden="true"
                  />
                </button>
              )}
              <CheckCircle className="h-5 w-5 text-green-400 shrink-0" aria-hidden="true" />
            </>
          )}
          {!isEarned && isRareRarityInfo(rarity) && (
            <BadgeComponent
              variant="outline"
              className="border-amber-500/50 bg-amber-500/20 text-amber-400 text-xs font-medium shrink-0"
              aria-label={t("rarity.rare")}
            >
              ✨ {t("rarity.rare")}
            </BadgeComponent>
          )}
          {!isEarned && (
            <BadgeComponent
              variant="outline"
              className={cn(
                "badge-sweep shrink-0 text-sm inline-flex items-center gap-1",
                difficultyColor.bg,
                difficultyColor.text,
                difficultyColor.border
              )}
              aria-label={`Difficulté: ${badge.difficulty}`}
            >
              <BadgeCardDifficultyMedal difficulty={badge.difficulty} />
            </BadgeComponent>
          )}
        </div>
      </div>
    </CardHeader>
  );
}
