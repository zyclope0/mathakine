"use client";

/**
 * BadgesClosestSection — badges proches du déblocage ("À portée de main").
 * Composant purement visuel.
 * FFI-L12.
 */

import { Flame } from "lucide-react";
import { PageSection } from "@/components/layout";
import { BadgeIcon } from "@/components/badges/BadgeIcon";
import type { Badge } from "@/types/api";
import type { BadgeProgressItem } from "@/hooks/useBadgesProgress";

interface BadgesClosestSectionProps {
  closestBadges: BadgeProgressItem[];
  availableBadges: Badge[];
  /** t("closestTitle") */
  title: string;
  /** t("remainingPlural", { count }) */
  formatRemainingPlural: (count: number) => string;
  /** t("remaining", { count }) */
  formatRemaining: (count: number) => string;
  /** t("almostThere") */
  almostThere: string;
}

export function BadgesClosestSection({
  closestBadges,
  availableBadges,
  title,
  formatRemainingPlural,
  formatRemaining,
  almostThere,
}: BadgesClosestSectionProps) {
  if (closestBadges.length === 0) return null;

  return (
    <PageSection className="space-y-3 animate-fade-in-up">
      <div className="flex items-center gap-2">
        <Flame className="h-4 w-4 text-accent" aria-hidden="true" />
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
          {title}
        </h2>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {closestBadges.map((badge) => {
          const fullBadge = availableBadges.find((b) => b.id === badge.id);
          const remaining = (badge.target ?? 0) - (badge.current ?? 0);
          const pct = Math.round((badge.progress ?? 0) * 100);
          return (
            <div
              key={badge.id}
              className="flex items-center gap-3 rounded-lg border border-accent/30 bg-accent/10 px-3 py-2.5"
            >
              <BadgeIcon
                code={fullBadge?.code}
                iconUrl={fullBadge?.icon_url}
                category={fullBadge?.category}
                size="sm"
                isEarned={false}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{badge.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div
                    className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden"
                    role="progressbar"
                    aria-valuenow={pct}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${badge.name}: ${pct}%`}
                  >
                    <div
                      className="bg-accent h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-xs text-accent font-semibold tabular-nums shrink-0">
                    {remaining > 0
                      ? remaining > 1
                        ? formatRemainingPlural(remaining)
                        : formatRemaining(remaining)
                      : almostThere}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </PageSection>
  );
}
