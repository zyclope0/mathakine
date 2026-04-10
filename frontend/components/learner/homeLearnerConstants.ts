import type { SpacedRepetitionUserSummary } from "@/lib/validation/dashboard";

/** Fallback when stats are not loaded — keeps reviews section + page-map anchor stable. */
export const EMPTY_SPACED_REPETITION: SpacedRepetitionUserSummary = {
  f04_initialized: false,
  active_cards_count: 0,
  due_today_count: 0,
  overdue_count: 0,
  next_review_date: null,
};
