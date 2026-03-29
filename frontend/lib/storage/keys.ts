/**
 * Source of truth for browser storage key strings. Values must remain stable for existing users.
 * themePreferences must match zustand persist `name` in `lib/stores/themeStore.ts`.
 */
export const STORAGE_KEYS = {
  prefExerciseOrder: "pref_exercise_order",
  prefChallengeOrder: "pref_challenge_order",
  /** Legacy session key — spaced repetition next review (F04). */
  spacedReviewNext: "spaced_review_next",
  edtechQuickStartClickedAt: "mathakine_quick_start_clicked_at",
  /** Legacy compat — dashboard view timestamp. */
  edtechDashboardViewedAt: "mathakine_dashboard_viewed_at",
  edtechInterleavedSession: "interleaved_session",
  themePreferences: "theme-preferences",
  darkMode: "dark-mode",
} as const;
