/**
 * lib/badges/badgesPage.ts
 *
 * Helpers purs du domaine badges — page.
 * Zéro React, zéro side-effect.
 *
 * FFI-L12 — extraction depuis app/badges/page.tsx.
 */

import { PROGRESSION_RANK_ICONS, PROGRESSION_RANK_TEXT_CLASS } from "@/lib/constants/leaderboard";
import {
  canonicalProgressionRankBucket,
  isKnownProgressionRankBucket,
} from "@/lib/gamification/progressionRankLabel";
import type { Badge, UserBadge } from "@/types/api";
import type { BadgeProgressItem, ProgressMapEntry } from "@/lib/badges/types";

// ─── Types exportés ───────────────────────────────────────────────────────────

export type FilterStatus = "all" | "earned" | "locked" | "close";
export type SortBy = "progress" | "date" | "points" | "category";

export type { ProgressMapEntry } from "@/lib/badges/types";

export interface RankInfo {
  title: string;
  icon: string;
  color: string;
}

export interface MotivationInfo {
  key: string;
  color: string;
}

export interface FilteredBadgesResult {
  filteredEarned: Badge[];
  filteredLocked: Badge[];
  categories: string[];
  difficulties: string[];
}

// ─── Helpers purs ─────────────────────────────────────────────────────────────

/**
 * Retourne le titre, l'icône et la couleur CSS du rang de progression.
 * Utilise les constantes leaderboard existantes — pas de duplication.
 */
export function getProgressionRankInfo(rank: string, tRank: (key: string) => string): RankInfo {
  const canon = canonicalProgressionRankBucket(rank);
  const safe = isKnownProgressionRankBucket(rank) ? canon : "cadet";
  return {
    title: tRank(safe),
    icon: PROGRESSION_RANK_ICONS[safe] ?? "🌟",
    color: PROGRESSION_RANK_TEXT_CLASS[safe] ?? "text-slate-400",
  };
}

/**
 * Calcule le pourcentage de progression badges.
 */
export function calcProgressPercent(earnedCount: number, totalCount: number): number {
  return totalCount > 0 ? (earnedCount / totalCount) * 100 : 0;
}

/**
 * Construit la progressMap à partir de la liste `inProgress`.
 * Exclut les badges sans target valide.
 */
export function buildProgressMap(
  inProgress: BadgeProgressItem[]
): Record<number, ProgressMapEntry> {
  return inProgress.reduce(
    (acc, b) => {
      if (b.target != null && b.target > 0) {
        acc[b.id] = {
          current: b.current ?? 0,
          target: b.target,
          progress: b.progress ?? 0,
          ...(b.progress_detail != null && { progress_detail: b.progress_detail }),
        };
      }
      return acc;
    },
    {} as Record<number, ProgressMapEntry>
  );
}

/**
 * Filtre et trie les badges earned/locked selon les filtres actifs.
 * Extrait aussi les listes de catégories et difficultés disponibles.
 */
export function filterBadges(params: {
  availableBadges: Badge[];
  earnedBadgeIds: Set<number>;
  filterStatus: FilterStatus;
  filterCategory: string;
  filterDifficulty: string;
  progressMap: Record<number, ProgressMapEntry>;
}): FilteredBadgesResult {
  const {
    availableBadges,
    earnedBadgeIds,
    filterStatus,
    filterCategory,
    filterDifficulty,
    progressMap,
  } = params;

  const catSet = new Set<string>();
  const diffSet = new Set<string>();
  availableBadges.forEach((b) => {
    if (b.category) catSet.add(b.category);
    if (b.difficulty) diffSet.add(b.difficulty);
  });
  const categories = Array.from(catSet).sort();
  const difficulties = Array.from(diffSet).sort();

  const earnedBadgesList = availableBadges.filter((b) => earnedBadgeIds.has(b.id));
  const lockedBadgesList = availableBadges.filter(
    (b) => !earnedBadgeIds.has(b.id) && !(b.is_secret === true)
  );

  const matchesCategory = (b: Badge) =>
    filterCategory === "all" || (b.category ?? "") === filterCategory;
  const matchesDifficulty = (b: Badge) =>
    filterDifficulty === "all" || (b.difficulty ?? "") === filterDifficulty;

  let earned = earnedBadgesList.filter((b) => matchesCategory(b) && matchesDifficulty(b));
  let locked = lockedBadgesList.filter((b) => matchesCategory(b) && matchesDifficulty(b));

  if (filterStatus === "earned") {
    locked = [];
  } else if (filterStatus === "locked") {
    earned = [];
  } else if (filterStatus === "close") {
    earned = [];
    locked = locked.filter((b) => {
      const p = progressMap[b.id];
      return p && p.progress >= 0.5;
    });
  }

  return { filteredEarned: earned, filteredLocked: locked, categories, difficulties };
}

/**
 * Compte les badges "proches" (progression >= 50% parmi les locked).
 */
export function countCloseBadges(
  lockedBadgesList: Badge[],
  progressMap: Record<number, ProgressMapEntry>
): number {
  return lockedBadgesList.filter((b) => {
    const p = progressMap[b.id];
    return p && p.progress >= 0.5;
  }).length;
}

/**
 * Indique si des filtres non-défaut sont actifs.
 */
export function hasActiveFilters(
  filterStatus: FilterStatus,
  filterCategory: string,
  filterDifficulty: string,
  sortBy: SortBy
): boolean {
  return (
    filterStatus !== "all" ||
    filterCategory !== "all" ||
    filterDifficulty !== "all" ||
    sortBy !== "category"
  );
}

/**
 * Retourne les badges les plus proches du déblocage (progression >= 50%),
 * triés par progression décroissante, limités à 3.
 */
export function getClosestBadges(inProgressWithTarget: BadgeProgressItem[]): BadgeProgressItem[] {
  return inProgressWithTarget
    .filter((b) => (b.progress ?? 0) >= 0.5)
    .sort((a, b) => (b.progress ?? 0) - (a.progress ?? 0))
    .slice(0, 3);
}

/**
 * Retourne les 4 derniers badges obtenus, triés par date décroissante.
 */
export function getLastExploits(earnedBadgesList: Badge[], earnedBadges: UserBadge[]): Badge[] {
  const withEarnedAt = earnedBadgesList
    .map((b) => {
      const ub = earnedBadges.find((eb) => eb.id === b.id);
      return { badge: b, earned_at: ub?.earned_at ?? "" };
    })
    .filter((x) => x.earned_at);

  return withEarnedAt
    .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
    .slice(0, 4)
    .map((x) => x.badge);
}

/**
 * Retourne le message motivationnel selon le pourcentage de progression.
 * null si aucun badge obtenu.
 */
export function getMotivationInfo(
  earnedCount: number,
  progressPercent: number
): MotivationInfo | null {
  if (earnedCount === 0) return null;
  if (progressPercent >= 100)
    return {
      key: "complete",
      color: "from-yellow-500/20 to-amber-500/10 border-yellow-500/30 text-yellow-400",
    };
  if (progressPercent >= 75)
    return {
      key: "legendary",
      color: "from-sky-500/20 to-blue-500/10 border-sky-500/30 text-sky-400",
    };
  if (progressPercent >= 50)
    return {
      key: "great",
      color: "from-primary/20 to-cyan-500/10 border-primary/30 text-primary",
    };
  if (progressPercent >= 25)
    return {
      key: "good",
      color: "from-green-500/20 to-emerald-500/10 border-green-500/30 text-green-400",
    };
  return {
    key: "start",
    color: "from-blue-500/20 to-sky-500/10 border-blue-500/30 text-blue-400",
  };
}

/**
 * Filtre les badges en cours ayant une cible valide et non secrets.
 */
export function getInProgressWithTarget(
  inProgress: BadgeProgressItem[],
  availableBadges: Badge[]
): BadgeProgressItem[] {
  return inProgress.filter((b) => {
    if (b.target == null || b.target <= 0) return false;
    const fullBadge = availableBadges.find((ab) => ab.id === b.id);
    if (fullBadge?.is_secret) return false;
    return true;
  });
}

/**
 * Trie les badges earned en mettant les épinglés en premier.
 */
export function sortEarnedWithPinned(filteredEarned: Badge[], pinnedBadgeIds: number[]): Badge[] {
  const pinned = pinnedBadgeIds
    .map((id) => filteredEarned.find((b) => b.id === id))
    .filter((b): b is Badge => !!b);
  const rest = filteredEarned.filter((b) => !pinnedBadgeIds.includes(b.id));
  return [...pinned, ...rest];
}

/**
 * Calcule la prochaine liste de badges epingles.
 * Toggle l'id demande et limite la liste a 3 elements.
 */
export function getNextPinnedBadgeIds(
  pinnedBadgeIds: number[],
  badgeId: number,
  maxPinned = 3
): number[] {
  const isPinned = pinnedBadgeIds.includes(badgeId);
  if (isPinned) {
    return pinnedBadgeIds.filter((id) => id !== badgeId);
  }

  return [...pinnedBadgeIds, badgeId].slice(0, maxPinned);
}
