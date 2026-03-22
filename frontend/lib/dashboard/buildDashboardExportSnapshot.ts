/**
 * Snapshot canonique pour les exports PDF/Excel du dashboard.
 * Source unique de vérité côté front : pas de refetch dans le bouton d'export.
 */

import type { TimeRange } from "@/hooks/useUserStats";
import type { ProgressStats } from "@/hooks/useProgressStats";
import type { ChallengesProgress } from "@/hooks/useChallengesProgress";
import type { UserStats } from "@/lib/validation/dashboard";
import type { DailyChallenge, GamificationLevelIndicator } from "@/types/api";

export interface DashboardExportSnapshot {
  username: string;
  timeRange: TimeRange;
  /** Libellé localisé (ex. « 30 derniers jours ») */
  timeRangeLabel: string;
  /** Segment sûr pour nom de fichier (ex. 7d, 30d, 90d, all) */
  timeRangeSlug: string;
  exportedAt: string;
  /** Dernière mise à jour connue côté stats (API ou activité) */
  lastUpdated: string | null;
  /** Niveau gamification compte (persistant), hors période d'export */
  gamification_level: GamificationLevelIndicator | null;

  summary: {
    total_exercises: number;
    total_challenges: number;
    correct_answers: number;
    /** null si non fourni par l’API et non dérivable sans inventer */
    incorrect_answers: number | null;
    /** KPI principal de réussite (période sélectionnée) */
    success_rate: number | null;
    /** Métrique secondaire / legacy — pas le KPI principal */
    average_score: number | null;
    /** total_points compte (GET /me), hors période d’export */
    account_total_points: number | null;
    /** XP dans le palier courant (gamification_level.current_xp) */
    account_xp_in_level: number | null;
    current_streak: number | null;
    highest_streak: number | null;
    average_time_seconds: number | null;
  };

  progressStats: ProgressStats | null;
  challengesProgress: ChallengesProgress | null;
  dailyChallenges: DailyChallenge[];

  recentActivity: NonNullable<UserStats["recent_activity"]>;

  performanceByCategory: ProgressStats["by_category"] | null;
  performanceByType: UserStats["performance_by_type"] | null;
  dailySeries: UserStats["exercises_by_day"] | null;
  timeline: UserStats["progress_over_time"] | null;
}

const TIME_RANGE_SLUG: Record<TimeRange, string> = {
  "7": "7d",
  "30": "30d",
  "90": "90d",
  all: "all",
};

/**
 * Dérive le nombre de réponses incorrectes sans inventer de 0.
 * 1) `incorrect_answers` API si présent
 * 2) sinon `total_attempts - correct_attempts` depuis la progression (global API)
 * 3) sinon null
 */
export function deriveIncorrectAnswersForExport(
  stats: UserStats,
  progress: ProgressStats | null | undefined
): number | null {
  if (typeof stats.incorrect_answers === "number") {
    return stats.incorrect_answers;
  }
  if (
    progress &&
    typeof progress.total_attempts === "number" &&
    typeof progress.correct_attempts === "number"
  ) {
    const incorrect = progress.total_attempts - progress.correct_attempts;
    if (incorrect >= 0) {
      return incorrect;
    }
  }
  return null;
}

export interface BuildDashboardExportSnapshotInput {
  username: string;
  timeRange: TimeRange;
  timeRangeLabel: string;
  stats: UserStats;
  /** Snapshot gamification compte (GET /me) — pas dérivé du timeRange */
  gamificationLevel?: GamificationLevelIndicator | null;
  /** total_points depuis GET /me (persistant) */
  accountTotalPoints?: number | null;
  progressStats?: ProgressStats | null;
  challengesProgress?: ChallengesProgress | null;
  dailyChallenges?: DailyChallenge[];
}

export function buildDashboardExportSnapshot(
  input: BuildDashboardExportSnapshotInput,
  exportedAt: Date = new Date()
): DashboardExportSnapshot {
  const {
    username,
    timeRange,
    timeRangeLabel,
    stats,
    gamificationLevel = null,
    accountTotalPoints = null,
    progressStats = null,
    challengesProgress = null,
    dailyChallenges = [],
  } = input;

  const incorrect = deriveIncorrectAnswersForExport(stats, progressStats);

  const lastUpdated =
    typeof stats.lastUpdated === "string"
      ? stats.lastUpdated
      : (stats.recent_activity?.[0]?.time ?? null);

  return {
    username,
    timeRange,
    timeRangeLabel,
    timeRangeSlug: TIME_RANGE_SLUG[timeRange],
    exportedAt: exportedAt.toISOString(),
    lastUpdated,
    gamification_level: gamificationLevel ?? null,

    summary: {
      total_exercises: stats.total_exercises,
      total_challenges: typeof stats.total_challenges === "number" ? stats.total_challenges : 0,
      correct_answers: stats.correct_answers,
      incorrect_answers: incorrect,
      success_rate: typeof stats.success_rate === "number" ? stats.success_rate : null,
      average_score: typeof stats.average_score === "number" ? stats.average_score : null,
      account_total_points: typeof accountTotalPoints === "number" ? accountTotalPoints : null,
      account_xp_in_level:
        gamificationLevel != null && typeof gamificationLevel.current_xp === "number"
          ? gamificationLevel.current_xp
          : null,
      current_streak: progressStats?.current_streak ?? null,
      highest_streak: progressStats?.highest_streak ?? null,
      average_time_seconds:
        typeof progressStats?.average_time === "number" ? progressStats.average_time : null,
    },

    progressStats,
    challengesProgress,
    dailyChallenges: [...dailyChallenges],

    recentActivity: Array.isArray(stats.recent_activity) ? stats.recent_activity : [],

    performanceByCategory: progressStats?.by_category ? { ...progressStats.by_category } : null,
    performanceByType: stats.performance_by_type ? { ...stats.performance_by_type } : null,
    dailySeries: stats.exercises_by_day ?? null,
    timeline: stats.progress_over_time ?? null,
  };
}

/** Base de nom de fichier : mathakine-dashboard-{user}-{range}-{YYYY-MM-DD} */
export function buildDashboardExportFilenameBase(
  username: string,
  timeRangeSlug: string,
  date = new Date()
): string {
  const safeUser = sanitizeExportFilenameSegment(username);
  const day = date.toISOString().slice(0, 10);
  return `mathakine-dashboard-${safeUser}-${timeRangeSlug}-${day}`;
}

export function sanitizeExportFilenameSegment(value: string): string {
  const cleaned = value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
  return cleaned.length > 0 ? cleaned : "user";
}
