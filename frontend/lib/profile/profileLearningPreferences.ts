/**
 * Pure helpers for profile learning preferences UI (grade system transitions, labels).
 * No React — FFI-L18A.
 */

import { AGE_GROUPS, type AgeGroup } from "@/lib/constants/exercises";
import type { GradeSystem } from "@/lib/profile/profilePage";
import { LEARNING_GOALS, PRACTICE_RHYTHMS } from "@/lib/profile/profilePage";

/** Slice used when reconciling grade_system changes with level / age_group. */
export interface LearningPrefsGradeSlice {
  grade_system: GradeSystem;
  grade_level: string;
  age_group: string;
}

/**
 * Mirrors the previous inline handler: switching notation system clears age band for suisse
 * and resets grade_level when it exceeds the new max.
 */
export function buildPatchWhenGradeSystemChanges(
  current: LearningPrefsGradeSlice,
  nextSystem: GradeSystem
): Partial<LearningPrefsGradeSlice> {
  const max = nextSystem === "suisse" ? 11 : 12;
  const parsed = current.grade_level ? parseInt(current.grade_level, 10) : NaN;
  const levelTooHigh = !Number.isNaN(parsed) && parsed > max;
  return {
    grade_system: nextSystem,
    age_group: nextSystem === "suisse" ? "" : current.age_group,
    grade_level: current.grade_level && levelTooHigh ? "" : current.grade_level,
  };
}

export function gradeLevelSelectOptionCount(system: GradeSystem): number {
  return system === "suisse" ? 11 : 12;
}

export function formatGradeLevelReadValue(
  gradeSystem: string | null | undefined,
  gradeLevel: number | null | undefined
): string {
  if (!gradeLevel) return "-";
  return gradeSystem === "suisse" ? `${gradeLevel}H` : String(gradeLevel);
}

export function resolvePreferredDifficultyReadLabel(
  preferred: string | null | undefined,
  getAgeDisplay: (group: string) => string
): string {
  if (!preferred) return "-";
  if (Object.values(AGE_GROUPS).includes(preferred as AgeGroup)) {
    return getAgeDisplay(preferred);
  }
  return preferred;
}

export function isKnownLearningGoal(value: string): value is (typeof LEARNING_GOALS)[number] {
  return LEARNING_GOALS.includes(value as (typeof LEARNING_GOALS)[number]);
}

export function isKnownPracticeRhythm(value: string): value is (typeof PRACTICE_RHYTHMS)[number] {
  return PRACTICE_RHYTHMS.includes(value as (typeof PRACTICE_RHYTHMS)[number]);
}
