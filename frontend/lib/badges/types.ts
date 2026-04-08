/**
 * Shared badge domain contracts (FFI-L20D) — consumed by cards, grid, sections, and page helpers.
 */
import type { Badge } from "@/types/api";

/** Progress detail when rule is success-rate based (API + progress map). */
export interface SuccessRateProgressDetail {
  type: "success_rate";
  total: number;
  correct: number;
  rate_pct: number;
  min_attempts: number;
  required_rate_pct: number;
}

/** Row from GET badges progress — in_progress item. */
export interface BadgeProgressItem {
  id: number;
  code: string;
  name: string;
  progress?: number;
  current?: number;
  target?: number;
  progress_detail?: SuccessRateProgressDetail;
}

/** Normalized progress entry for maps (locked badge progress UI). */
export interface BadgeProgressSnapshot {
  current: number;
  target: number;
  progress: number;
  progress_detail?: SuccessRateProgressDetail;
}

/** Alias for page helpers — same shape as snapshot. */
export type ProgressMapEntry = BadgeProgressSnapshot;

export interface RarityInfo {
  unlock_count: number;
  unlock_percent: number;
  rarity: string;
}

export type BadgeSortBy = "progress" | "date" | "points" | "category";

export type BadgeWithCriteria = Badge & { criteria_text?: string | null };
