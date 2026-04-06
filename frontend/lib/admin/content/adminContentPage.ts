/**
 * Pure helpers for the admin content shell (FFI-L14 lot A). No React.
 */

import { BADGE_CATEGORIES } from "@/lib/constants/badges";
import { ADMIN_CHALLENGE_TYPE_OPTIONS } from "@/lib/constants/challenges";
import { ADMIN_EXERCISE_TYPES, EXERCISE_TYPE_DISPLAY } from "@/lib/constants/exercises";

export type AdminContentTab = "exercises" | "challenges" | "badges";

export const ADMIN_CONTENT_PAGE_SIZE = 20;

export function parseAdminContentTabParam(tabParam: string | null): AdminContentTab {
  if (tabParam === "challenges") return "challenges";
  if (tabParam === "badges") return "badges";
  return "exercises";
}

export function parseAdminContentEditIdParam(editParam: string | null): number | null {
  if (editParam === null || editParam === "") return null;
  const n = parseInt(editParam, 10);
  if (Number.isNaN(n) || n <= 0) return null;
  return n;
}

export function buildExerciseTypeFilterOptions(): { value: string; label: string }[] {
  return [
    { value: "all", label: "Tous les types" },
    ...ADMIN_EXERCISE_TYPES.map((t) => ({
      value: t,
      label: EXERCISE_TYPE_DISPLAY[t.toLowerCase() as keyof typeof EXERCISE_TYPE_DISPLAY] ?? t,
    })),
  ];
}

export function buildChallengeTypeFilterOptions(): { value: string; label: string }[] {
  return [
    { value: "all", label: "Tous les types" },
    ...ADMIN_CHALLENGE_TYPE_OPTIONS.filter((t) => t.value !== "custom"),
  ];
}

export function buildBadgeCategoryFilterOptions(): { value: string; label: string }[] {
  return [
    { value: "all", label: "Toutes les catégories" },
    ...BADGE_CATEGORIES.map((c) => ({
      value: c,
      label: c.charAt(0).toUpperCase() + c.slice(1),
    })),
  ];
}
