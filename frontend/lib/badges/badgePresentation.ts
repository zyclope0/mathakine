/**
 * Pure presentation helpers for badge UI (FFI-L20D) — no React, no i18n.
 */
import type { Badge, UserBadge } from "@/types/api";
import type {
  BadgeProgressSnapshot,
  BadgeSortBy,
  RarityInfo,
  SuccessRateProgressDetail,
} from "@/lib/badges/types";

export interface DifficultyPresentationClasses {
  bg: string;
  text: string;
  border: string;
}

const DEFAULT_DIFFICULTY_PRESENTATION: DifficultyPresentationClasses = {
  bg: "bg-amber-500/20",
  text: "text-amber-400",
  border: "border-amber-500/30",
};

const DIFFICULTY_PRESENTATION: Record<string, DifficultyPresentationClasses> = {
  bronze: DEFAULT_DIFFICULTY_PRESENTATION,
  silver: {
    bg: "bg-gray-400/20",
    text: "text-gray-300",
    border: "border-gray-400/30",
  },
  gold: {
    bg: "bg-yellow-500/20",
    text: "text-yellow-400",
    border: "border-yellow-500/30",
  },
  legendary: {
    bg: "bg-amber-400/25",
    text: "text-amber-300",
    border: "border-amber-400/40",
  },
};

/** Glow color token behind badge icon (Tailwind class). */
export const GLOW_COLOR_BY_DIFFICULTY: Record<string, string> = {
  bronze: "bg-orange-500",
  silver: "bg-slate-300",
  gold: "bg-yellow-400",
  legendary: "bg-amber-400",
};

const MEDAL_SVG_BY_DIFFICULTY: Record<string, string> = {
  bronze: "/badges/svg/medal-bronze.svg",
  silver: "/badges/svg/medal-silver.svg",
  gold: "/badges/svg/medal.svg",
  legendary: "/badges/svg/medal-diamond.svg",
};

const DEFAULT_MEDAL_SVG = "/badges/svg/medal-bronze.svg";

const CATEGORY_SORT_ORDER: Record<string, number> = {
  progression: 0,
  mastery: 1,
  special: 2,
};

const DIFFICULTY_SORT_ORDER: Record<string, number> = {
  bronze: 0,
  silver: 1,
  gold: 2,
  legendary: 3,
};

export function getDifficultyPresentationClasses(
  difficulty: string | null | undefined
): DifficultyPresentationClasses {
  if (!difficulty) {
    return DEFAULT_DIFFICULTY_PRESENTATION;
  }
  return DIFFICULTY_PRESENTATION[difficulty] ?? DEFAULT_DIFFICULTY_PRESENTATION;
}

export function resolveIconGlowClass(difficulty: string | null | undefined): string {
  if (!difficulty) {
    return "bg-primary";
  }
  return GLOW_COLOR_BY_DIFFICULTY[difficulty] ?? "bg-primary";
}

export function resolveMedalSvgPath(difficulty: string | null | undefined): string {
  if (!difficulty) {
    return DEFAULT_MEDAL_SVG;
  }
  return MEDAL_SVG_BY_DIFFICULTY[difficulty] ?? DEFAULT_MEDAL_SVG;
}

/** True when a medal asset exists for this difficulty (BadgeCard hides medal otherwise). */
export function hasPresentationMedal(difficulty: string | null | undefined): boolean {
  return (
    typeof difficulty === "string" &&
    Object.prototype.hasOwnProperty.call(MEDAL_SVG_BY_DIFFICULTY, difficulty)
  );
}

export function isRareRarityInfo(rarity: RarityInfo | null | undefined): boolean {
  return rarity?.rarity === "rare";
}

export function filterBadgesWithNameOrCode(badges: Badge[]): Badge[] {
  return badges.filter((b) => Boolean(b.name || b.code));
}

export function buildEarnedUserBadgeMap(earnedBadges: UserBadge[]): Map<number, UserBadge> {
  const map = new Map<number, UserBadge>();
  earnedBadges.forEach((ub) => {
    map.set(ub.id, ub);
  });
  return map;
}

/**
 * Sort badges for grid display (same ordering rules as legacy BadgeGrid).
 */
export function sortBadgesForGrid(
  badges: Badge[],
  earnedMap: Map<number, UserBadge>,
  progressMap: Record<number, BadgeProgressSnapshot> | undefined,
  sortBy: BadgeSortBy
): Badge[] {
  return [...badges].sort((a, b) => {
    const aEarned = earnedMap.has(a.id);
    const bEarned = earnedMap.has(b.id);

    if (sortBy === "progress") {
      const aProg = progressMap?.[a.id]?.progress ?? (aEarned ? 1 : 0);
      const bProg = progressMap?.[b.id]?.progress ?? (bEarned ? 1 : 0);
      return bProg - aProg;
    }
    if (sortBy === "date") {
      const aDate = earnedMap.get(a.id)?.earned_at ?? "";
      const bDate = earnedMap.get(b.id)?.earned_at ?? "";
      if (aDate && bDate) return new Date(bDate).getTime() - new Date(aDate).getTime();
      if (aDate) return -1;
      if (bDate) return 1;
      return 0;
    }
    if (sortBy === "points") {
      const aPt = a.points_reward ?? (a as UserBadge).points ?? 0;
      const bPt = b.points_reward ?? (b as UserBadge).points ?? 0;
      return bPt - aPt;
    }

    if (aEarned && !bEarned) return -1;
    if (!aEarned && bEarned) return 1;
    const aCategory = a.category || "";
    const bCategory = b.category || "";
    const categoryDiff =
      (CATEGORY_SORT_ORDER[aCategory] ?? 999) - (CATEGORY_SORT_ORDER[bCategory] ?? 999);
    if (categoryDiff !== 0) return categoryDiff;
    const aDifficulty = a.difficulty || "";
    const bDifficulty = b.difficulty || "";
    return (
      (DIFFICULTY_SORT_ORDER[aDifficulty] ?? 999) - (DIFFICULTY_SORT_ORDER[bDifficulty] ?? 999)
    );
  });
}

/** Remaining correct answers needed for success-rate rule (ceil path, matches BadgeCard). */
export function successRateRemainingCorrectNeeded(detail: SuccessRateProgressDetail): number {
  return Math.ceil((detail.total * detail.required_rate_pct) / 100) - detail.correct;
}

export type CompactInProgressMotivation =
  | { kind: "tuApproches" }
  | { kind: "plusQueCorrect"; count: number }
  | { kind: "plusQue"; count: number };

/**
 * High-motivation line when progress >= 0.5 and target > 0 (in-progress tab row + BadgeCard locked).
 */
export function resolveCompactHighProgressMotivation(
  current: number,
  target: number,
  progress: number,
  detail: SuccessRateProgressDetail | null | undefined
): CompactInProgressMotivation | null {
  if (target <= 0 || progress < 0.5) {
    return null;
  }
  if (detail?.type === "success_rate") {
    if (detail.rate_pct >= detail.required_rate_pct) {
      return { kind: "tuApproches" };
    }
    return { kind: "plusQueCorrect", count: successRateRemainingCorrectNeeded(detail) };
  }
  const remaining = target - current;
  if (remaining > 0) {
    return { kind: "plusQue", count: remaining };
  }
  return { kind: "tuApproches" };
}

/** Locked BadgeCard: subtle "plus que" line when 0 < progress < 0.5 (non success-rate). */
export function shouldShowLockedMidMotivationLine(
  current: number,
  target: number,
  progress: number,
  detail: SuccessRateProgressDetail | null | undefined
): boolean {
  return (
    target > 0 &&
    progress > 0 &&
    progress < 0.5 &&
    detail?.type !== "success_rate" &&
    target - current > 0
  );
}

export function shouldShowLockedZeroMotivationLine(progress: number, target: number): boolean {
  return target > 0 && progress === 0;
}
