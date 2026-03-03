/** Catégories de badges */
export const BADGE_CATEGORIES = [
  "progression",
  "mastery",
  "special",
  "performance",
  "regularity",
  "discovery",
] as const;

export type BadgeCategory = (typeof BADGE_CATEGORIES)[number];

/** Niveaux de difficulté des badges */
export const BADGE_DIFFICULTIES = ["bronze", "silver", "gold", "legendary"] as const;

export type BadgeDifficulty = (typeof BADGE_DIFFICULTIES)[number];
