"use client";

import { CardContent, CardDescription } from "@/components/ui/card";
import { Badge as BadgeComponent } from "@/components/ui/badge";
import { Trophy } from "lucide-react";
import type { UserBadge } from "@/types/api";
import type { BadgeProgressSnapshot, BadgeWithCriteria, RarityInfo } from "@/lib/badges/types";
import { isRareRarityInfo, type CompactInProgressMotivation } from "@/lib/badges/badgePresentation";
import { cn } from "@/lib/utils";
import type { BadgeCardBadgesT } from "@/components/badges/badgeCard/BadgeCardCompactEarnedHeader";

interface BadgeCardCardContentProps {
  compact: boolean;
  isEarned: boolean;
  badge: BadgeWithCriteria;
  userBadge?: UserBadge | null | undefined;
  progress?: BadgeProgressSnapshot | null | undefined;
  rarity?: RarityInfo | null | undefined;
  thematicLine: string;
  locale: string;
  lockedHighMotivation: CompactInProgressMotivation | null;
  lockedMidMotivationVisible: boolean;
  lockedZeroMotivationVisible: boolean;
  t: BadgeCardBadgesT;
}

export function BadgeCardCardContent({
  compact,
  isEarned,
  badge,
  userBadge,
  progress,
  rarity,
  thematicLine,
  locale,
  lockedHighMotivation,
  lockedMidMotivationVisible,
  lockedZeroMotivationVisible,
  t,
}: BadgeCardCardContentProps) {
  return (
    <CardContent
      className={cn(
        "space-y-4",
        compact ? "flex-1 px-3 pb-0 pt-0" : "flex-1 flex flex-col min-h-0"
      )}
    >
      {isEarned ? (
        <div className="badge-card-expandable space-y-4">
          {thematicLine && (
            <CardDescription className="text-primary-on-dark italic text-sm">
              {thematicLine}
            </CardDescription>
          )}
          {isRareRarityInfo(rarity) && (
            <BadgeComponent
              variant="outline"
              className="border-amber-500/50 bg-amber-500/20 text-amber-400 text-xs font-medium shrink-0 w-fit"
              aria-label={t("rarity.rare")}
            >
              ✨ {t("rarity.rare")}
            </BadgeComponent>
          )}
          <div className="rounded-lg border border-border/40 bg-muted/30 px-3 py-2.5">
            {badge.description ? (
              <p className="text-sm text-muted-foreground leading-relaxed">{badge.description}</p>
            ) : (
              <p className="text-sm text-muted-foreground/60 italic leading-relaxed">
                {t("noDescription")}
              </p>
            )}
          </div>
          {rarity && (
            <div
              className="inline-flex w-fit rounded-full border border-border/50 bg-background/50 px-3 py-1 text-xs text-muted-foreground"
              role="status"
            >
              {t("socialProof", { percent: rarity.unlock_percent })}
            </div>
          )}
          <div className="flex items-center justify-between rounded-lg border border-border/40 bg-muted/20 px-3 py-2.5">
            <div className="flex items-center gap-2 text-base font-semibold">
              <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
              <span className="text-foreground">{badge.points_reward}</span>
              <span className="text-muted-foreground text-sm">pts</span>
            </div>
            {userBadge?.earned_at && (
              <div className="text-xs text-muted-foreground bg-green-500/10 px-2 py-1 rounded-md">
                {t("earnedOn", {
                  date: new Date(userBadge.earned_at as string).toLocaleDateString(locale),
                })}
              </div>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="rounded-lg border border-border/40 bg-muted/30 px-3 py-2.5">
            {badge.description ? (
              <p className="text-sm md:text-base text-muted-foreground leading-relaxed line-clamp-3">
                {badge.description}
              </p>
            ) : (
              <p className="text-sm md:text-base text-muted-foreground/60 italic leading-relaxed line-clamp-3">
                {t("noDescription")}
              </p>
            )}
          </div>
          {rarity && (
            <div
              className="inline-flex w-fit rounded-full border border-border/50 bg-background/50 px-3 py-1 text-xs text-muted-foreground"
              role="status"
            >
              {t("socialProof", { percent: rarity.unlock_percent })}
            </div>
          )}
        </>
      )}

      {!isEarned && (badge.criteria_text || progress) && (
        <div className="space-y-2 pt-2 border-t border-border/50">
          {badge.criteria_text && (
            <p className="text-sm font-medium">
              <span className="text-foreground">{badge.criteria_text}</span>
              {progress && progress.target > 0 && (
                <span className="text-foreground font-semibold ml-1 tabular-nums">
                  {progress.progress_detail?.type === "success_rate" ? (
                    <>
                      {" "}
                      —{" "}
                      {t("successRateDisplay", {
                        correct: progress.progress_detail.correct,
                        total: progress.progress_detail.total,
                        rate: progress.progress_detail.rate_pct,
                      })}
                    </>
                  ) : (
                    <>
                      {" "}
                      —{" "}
                      {t("progressLabel", {
                        current: progress.current,
                        target: progress.target,
                      })}
                    </>
                  )}
                </span>
              )}
            </p>
          )}
          {lockedHighMotivation && (
            <p className="text-sm font-semibold text-amber-500/90" role="status">
              {lockedHighMotivation.kind === "tuApproches" && t("tuApproches")}
              {lockedHighMotivation.kind === "plusQueCorrect" &&
                t("plusQueCorrect", { count: lockedHighMotivation.count })}
              {lockedHighMotivation.kind === "plusQue" &&
                t("plusQue", { count: lockedHighMotivation.count })}
            </p>
          )}
          {lockedMidMotivationVisible && progress && (
            <p className="text-xs text-muted-foreground" role="status">
              {t("plusQue", { count: progress.target - progress.current })}
            </p>
          )}
          {lockedZeroMotivationVisible && progress && (
            <p className="text-xs text-muted-foreground" role="status">
              {progress.progress_detail?.type === "success_rate"
                ? t("successRateTarget", {
                    rate: progress.progress_detail.required_rate_pct,
                    min: progress.progress_detail.min_attempts,
                  })
                : t("plusQue", { count: progress.target })}
            </p>
          )}
          {progress && progress.target > 0 && (
            <div
              className="w-full bg-muted rounded-full h-3 overflow-hidden ring-1 ring-inset ring-border/60"
              role="progressbar"
              aria-valuenow={Math.round(progress.progress * 100)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${badge.name || badge.code || t("noName")}: ${Math.round(progress.progress * 100)}%`}
            >
              <div
                className="bg-primary h-3 rounded-full transition-all duration-500 min-w-[2px]"
                style={{ width: `${Math.max(progress.progress * 100, 2)}%` }}
              />
            </div>
          )}
          {!progress && badge.criteria_text && (
            <p className="text-xs text-muted-foreground/70 italic" role="status">
              {t("noProgressYet")}
            </p>
          )}
        </div>
      )}

      {!isEarned && (
        <div className="flex items-center justify-between pt-3 mt-auto rounded-lg border border-border/40 bg-muted/20 px-3 py-2.5">
          <div className="flex items-center gap-2 text-base font-semibold">
            <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
            <span className="text-foreground">{badge.points_reward}</span>
            <span className="text-muted-foreground text-sm">pts</span>
          </div>
        </div>
      )}
    </CardContent>
  );
}
