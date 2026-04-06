/**
 * Pure helpers for admin exercise list + form coherence (FFI-L14).
 * Single place for display strings and age-group normalization — no React.
 *
 * Difficulty list display: `difficulty` is legacy transport (see DIFFICULTY_AND_RANKS_MANIFEST).
 * Until the admin list API reliably exposes `difficulty_tier`, we show neutral level labels
 * for known legacy codes — not Star Wars product wording.
 */

import {
  ADMIN_DIFFICULTIES,
  ADMIN_EXERCISE_AGE_GROUP_OPTIONS,
  EXERCISE_TYPE_DISPLAY,
  getAgeGroupDisplay,
} from "@/lib/constants/exercises";

/** Stable fallback when difficulty is missing (admin table cell). */
export const ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL = "—";

/**
 * Stable fallback when difficulty is not in the known admin/API set.
 * Includes the raw value so admins can report or fix data.
 */
export const ADMIN_EXERCISE_DIFFICULTY_UNKNOWN_PREFIX = "Non répertorié";

/** Default age group aligned with create modal initial state. */
export const DEFAULT_ADMIN_EXERCISE_AGE_GROUP = "9-11" as const;

/** F42 pedagogical tier range (manifest). */
const DIFFICULTY_TIER_MIN = 1;
const DIFFICULTY_TIER_MAX = 12;

const ADMIN_EXERCISE_TYPE_UNKNOWN_PREFIX = "Non répertorié";

const CANONICAL_AGE_VALUES: Set<string> = new Set(
  ADMIN_EXERCISE_AGE_GROUP_OPTIONS.map((o) => o.value as string)
);

/** Maps legacy / alternate spellings to canonical option values. */
const AGE_GROUP_ALIASES: Record<string, string> = {
  "6_8": "6-8",
  "8_10": "9-11",
  "9_11": "9-11",
  "12_14": "12-14",
  "15_17": "15-17",
};

/**
 * Transitional neutral labels for legacy `difficulty` strings (admin list only).
 * Order matches ascending difficulty of ADMIN_DIFFICULTIES.
 */
const LEGACY_EXERCISE_DIFFICULTY_NEUTRAL: Record<string, string> = {
  INITIE: "Niveau 1",
  PADAWAN: "Niveau 2",
  CHEVALIER: "Niveau 3",
  MAITRE: "Niveau 4",
  GRAND_MAITRE: "Niveau 5",
};

/**
 * Normalizes age_group for admin Select binding and API round-trip.
 * - Trims input
 * - Maps a few legacy aliases (underscores, etc.)
 * - Returns default when empty
 * - Unknown values are returned as-is so the edit UI can show a legacy SelectItem
 */
export function normalizeAdminExerciseAgeGroup(input: string | null | undefined): string {
  const t = input?.trim() ?? "";
  if (!t) return DEFAULT_ADMIN_EXERCISE_AGE_GROUP;
  if (CANONICAL_AGE_VALUES.has(t)) return t;
  const alias = AGE_GROUP_ALIASES[t] ?? AGE_GROUP_ALIASES[t.toLowerCase()];
  if (alias && CANONICAL_AGE_VALUES.has(alias)) return alias;
  const lower = t.toLowerCase();
  if (lower === "adult" || lower === "adults") return "adulte";
  return t;
}

/**
 * Label for the admin exercises table — matches option labels when possible,
 * otherwise reuses global age display for values like `tous-ages`.
 */
export function getAdminExerciseAgeGroupListDisplay(raw: string | null | undefined): string {
  const trimmed = raw?.trim();
  if (!trimmed) return ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL;
  const normalized = normalizeAdminExerciseAgeGroup(raw);
  const opt = ADMIN_EXERCISE_AGE_GROUP_OPTIONS.find((o) => o.value === normalized);
  if (opt) return opt.label;
  const globalDisplay = getAgeGroupDisplay(normalized);
  const defaultDisplay = getAgeGroupDisplay(undefined);
  if (globalDisplay === defaultDisplay && normalized !== "tous-ages") return normalized;
  return globalDisplay;
}

export interface AdminExerciseDifficultyDisplayOptions {
  /** When present on the list payload, preferred over legacy `difficulty` string. */
  difficultyTier?: number | null;
}

/**
 * Admin exercises table — difficulty column.
 * Prefers `difficulty_tier` (F42 palier 1..12) when provided; otherwise maps legacy
 * `difficulty` codes to neutral "Niveau n" labels (transitional).
 */
export function getAdminExerciseDifficultyDisplay(
  legacyDifficulty: string | null | undefined,
  options?: AdminExerciseDifficultyDisplayOptions
): string {
  const tierRaw = options?.difficultyTier;
  if (tierRaw != null && Number.isFinite(Number(tierRaw))) {
    const t = Math.trunc(Number(tierRaw));
    if (t >= DIFFICULTY_TIER_MIN && t <= DIFFICULTY_TIER_MAX) {
      return `Palier ${t}`;
    }
  }

  const v = legacyDifficulty?.trim() ?? "";
  if (!v) return ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL;

  const upper = v.toUpperCase();
  const neutral = LEGACY_EXERCISE_DIFFICULTY_NEUTRAL[upper];
  if (neutral) return neutral;

  const matched = ADMIN_DIFFICULTIES.find((d) => d === v || d === upper);
  if (matched && LEGACY_EXERCISE_DIFFICULTY_NEUTRAL[matched]) {
    return LEGACY_EXERCISE_DIFFICULTY_NEUTRAL[matched]!;
  }

  return `${ADMIN_EXERCISE_DIFFICULTY_UNKNOWN_PREFIX} (${v})`;
}

export function getAdminExerciseTypeDisplay(raw: string | null | undefined): string {
  const val = raw?.trim() ?? "";
  if (!val) return ADMIN_EXERCISE_DIFFICULTY_EMPTY_LABEL;
  const key = val.toLowerCase() as keyof typeof EXERCISE_TYPE_DISPLAY;
  if (key in EXERCISE_TYPE_DISPLAY) return EXERCISE_TYPE_DISPLAY[key];
  return `${ADMIN_EXERCISE_TYPE_UNKNOWN_PREFIX} (${val})`;
}
