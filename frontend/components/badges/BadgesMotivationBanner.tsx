"use client";

/**
 * BadgesMotivationBanner — bandeau motivationnel de célébration.
 * Composant purement visuel.
 * FFI-L12.
 */

import { Sparkles } from "lucide-react";
import type { MotivationInfo } from "@/lib/badges/badgesPage";

interface BadgesMotivationBannerProps {
  motivationInfo: MotivationInfo;
  earnedCount: number;
  /** t("badgesUnlockedPlural", { count, msg }) */
  labelPlural: string;
  /** t("badgesUnlocked", { count, msg }) */
  labelSingular: string;
  /** t(`motivationIcon.${motivationInfo.key}`) */
  icon: string;
}

export function BadgesMotivationBanner({
  motivationInfo,
  earnedCount,
  labelPlural,
  labelSingular,
  icon,
}: BadgesMotivationBannerProps) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-xl border bg-gradient-to-r ${motivationInfo.color} animate-fade-in-up`}
      role="status"
      aria-live="polite"
    >
      <Sparkles className="h-5 w-5 shrink-0" aria-hidden="true" />
      <span className="text-sm font-semibold">
        <span className="mr-1.5" aria-hidden="true">
          {icon}
        </span>
        {earnedCount > 1 ? labelPlural : labelSingular}
      </span>
    </div>
  );
}
