"use client";

/**
 * useBadgesPageController — logique runtime locale de la page badges.
 *
 * Porte :
 *   - états d'expansion (statsExpanded, toUnlockExpanded, collectionExpanded)
 *   - filtres et tri (filterStatus, filterCategory, filterDifficulty, sortBy)
 *   - navigation par onglets (activeTab, defaultTab)
 *   - confetti first-run (localStorage + canvas-confetti)
 *   - clearFilters
 *
 * Ne fait aucun fetch, aucun rendu JSX.
 * Reçoit les données déjà chargées par useBadges / useBadgesProgress.
 *
 * FFI-L12 — extraction depuis app/badges/page.tsx.
 */

import { useState, useEffect, useRef, useMemo } from "react";
import type { Badge, UserBadge } from "@/types/api";
import type { BadgeProgressItem } from "@/hooks/useBadgesProgress";
import {
  type FilterStatus,
  type SortBy,
  type ProgressMapEntry,
  type FilteredBadgesResult,
  type MotivationInfo,
  type RankInfo,
  buildProgressMap,
  filterBadges,
  countCloseBadges,
  hasActiveFilters as calcHasActiveFilters,
  getClosestBadges,
  getLastExploits,
  getMotivationInfo,
  getInProgressWithTarget,
  calcProgressPercent,
} from "@/lib/badges/badgesPage";

// ─── Constantes ───────────────────────────────────────────────────────────────

export const TO_UNLOCK_PREVIEW = 12;
export const COLLECTION_PREVIEW_COUNT = 12;
const CONFETTI_STORAGE_KEY = "mathakine_badges_last_count";

// ─── Types ────────────────────────────────────────────────────────────────────

interface UseBadgesPageControllerArgs {
  earnedBadges: UserBadge[];
  availableBadges: Badge[];
  inProgress: BadgeProgressItem[];
  earnedCount: number;
  isLoading: boolean;
  rankInfo: RankInfo;
}

export interface BadgesPageControllerState {
  // Expansions
  statsExpanded: boolean;
  setStatsExpanded: (v: boolean) => void;
  toUnlockExpanded: boolean;
  setToUnlockExpanded: (v: boolean) => void;
  collectionExpanded: boolean;
  setCollectionExpanded: (v: boolean) => void;

  // Filtres
  filterStatus: FilterStatus;
  setFilterStatus: (v: FilterStatus) => void;
  filterCategory: string;
  setFilterCategory: (v: string) => void;
  filterDifficulty: string;
  setFilterDifficulty: (v: string) => void;
  sortBy: SortBy;
  setSortBy: (v: SortBy) => void;
  clearFilters: () => void;
  hasActiveFilters: boolean;

  // Tabs
  activeTab: string;
  setActiveTab: (v: string) => void;
  defaultTab: string;
  isToUnlockTab: boolean;

  // Dérivés
  progressMap: Record<number, ProgressMapEntry>;
  filtered: FilteredBadgesResult;
  closeCount: number;
  inProgressWithTarget: BadgeProgressItem[];
  closestBadges: BadgeProgressItem[];
  lastExploits: Badge[];
  motivationInfo: MotivationInfo | null;
  progressPercent: number;
  earnedBadgeIds: Set<number>;
  earnedBadgesList: Badge[];
  lockedBadgesList: Badge[];
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useBadgesPageController({
  earnedBadges,
  availableBadges,
  inProgress,
  earnedCount,
  isLoading,
}: UseBadgesPageControllerArgs): BadgesPageControllerState {
  // ─── Expansions ────────────────────────────────────────────────────────────
  const [statsExpanded, setStatsExpanded] = useState(false);
  const [toUnlockExpanded, setToUnlockExpanded] = useState(false);
  const [collectionExpanded, setCollectionExpanded] = useState(false);

  // ─── Filtres ───────────────────────────────────────────────────────────────
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterDifficulty, setFilterDifficulty] = useState<string>("all");
  const [sortBy, setSortBy] = useState<SortBy>("category");

  const clearFilters = () => {
    setFilterStatus("all");
    setFilterCategory("all");
    setFilterDifficulty("all");
    setSortBy("category");
  };

  const activeFilters = calcHasActiveFilters(
    filterStatus,
    filterCategory,
    filterDifficulty,
    sortBy
  );

  // ─── Dérivés badges ────────────────────────────────────────────────────────

  const earnedBadgeIds = useMemo(() => new Set(earnedBadges.map((ub) => ub.id)), [earnedBadges]);

  const visibleTotal = useMemo(
    () => availableBadges.filter((b) => !(b.is_secret === true) || earnedBadgeIds.has(b.id)).length,
    [availableBadges, earnedBadgeIds]
  );

  const progressPercent = calcProgressPercent(earnedCount, visibleTotal);

  const earnedBadgesList = useMemo(
    () => availableBadges.filter((b) => earnedBadgeIds.has(b.id)),
    [availableBadges, earnedBadgeIds]
  );

  const lockedBadgesList = useMemo(
    () => availableBadges.filter((b) => !earnedBadgeIds.has(b.id) && !(b.is_secret === true)),
    [availableBadges, earnedBadgeIds]
  );

  const progressMap = useMemo(() => buildProgressMap(inProgress), [inProgress]);

  const filtered = useMemo(
    () =>
      filterBadges({
        availableBadges,
        earnedBadgeIds,
        filterStatus,
        filterCategory,
        filterDifficulty,
        progressMap,
      }),
    [availableBadges, earnedBadgeIds, filterStatus, filterCategory, filterDifficulty, progressMap]
  );

  const closeCount = useMemo(
    () => countCloseBadges(lockedBadgesList, progressMap),
    [lockedBadgesList, progressMap]
  );

  const inProgressWithTarget = useMemo(
    () => getInProgressWithTarget(inProgress, availableBadges),
    [inProgress, availableBadges]
  );

  const closestBadges = useMemo(
    () => getClosestBadges(inProgressWithTarget),
    [inProgressWithTarget]
  );

  const lastExploits = useMemo(
    () => getLastExploits(earnedBadgesList, earnedBadges),
    [earnedBadgesList, earnedBadges]
  );

  const motivationInfo = useMemo(
    () => getMotivationInfo(earnedCount, progressPercent),
    [earnedCount, progressPercent]
  );

  // ─── Tabs ──────────────────────────────────────────────────────────────────

  const defaultTab = inProgressWithTarget.length > 0 ? "inProgress" : "toUnlock";
  const [activeTab, setActiveTab] = useState<string>(defaultTab);
  const isToUnlockTab = activeTab === "toUnlock";

  useEffect(() => {
    setActiveTab(defaultTab);
  }, [defaultTab]);

  // ─── Confetti first-run ────────────────────────────────────────────────────

  const confettiRef = useRef(false);
  useEffect(() => {
    if (confettiRef.current || isLoading || earnedCount === 0) return;
    const lastCount = parseInt(localStorage.getItem(CONFETTI_STORAGE_KEY) ?? "0", 10);
    if (earnedCount > lastCount) {
      confettiRef.current = true;
      localStorage.setItem(CONFETTI_STORAGE_KEY, String(earnedCount));
      import("canvas-confetti").then(({ default: confetti }) => {
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.4 },
          colors: ["#facc15", "#a78bfa", "#34d399", "#60a5fa"],
        });
      });
    }
  }, [earnedCount, isLoading]);

  // ─── Retour ────────────────────────────────────────────────────────────────

  return {
    statsExpanded,
    setStatsExpanded,
    toUnlockExpanded,
    setToUnlockExpanded,
    collectionExpanded,
    setCollectionExpanded,

    filterStatus,
    setFilterStatus,
    filterCategory,
    setFilterCategory,
    filterDifficulty,
    setFilterDifficulty,
    sortBy,
    setSortBy,
    clearFilters,
    hasActiveFilters: activeFilters,

    activeTab,
    setActiveTab,
    defaultTab,
    isToUnlockTab,

    progressMap,
    filtered,
    closeCount,
    inProgressWithTarget,
    closestBadges,
    lastExploits,
    motivationInfo,
    progressPercent,
    earnedBadgeIds,
    earnedBadgesList,
    lockedBadgesList,
  };
}
