/**
 * Pure helpers for ExerciseSolver runtime (FFI-L20B).
 * No React, no I/O — derivations and small payloads only.
 */
import type { Exercise } from "@/types/api";
import type {
  NextReviewApiResponse,
  NextReviewPayload,
  ReviewSafeExercisePayload,
} from "@/lib/validation/spacedRepetitionNextReview";

import {
  parseInterleavedSessionFromStorage,
  type InterleavedSessionStored,
  type SessionMode,
} from "@/lib/exercises/exerciseSolverSession";

export type SolverDisplayExercise = Exercise | ReviewSafeExercisePayload;

export function resolveDisplayExercise(
  sessionMode: SessionMode,
  exercise: Exercise | null | undefined,
  reviewExercise: ReviewSafeExercisePayload | null
): SolverDisplayExercise | null {
  if (sessionMode === "spaced-review") {
    return reviewExercise;
  }
  return exercise ?? null;
}

export function filterExerciseChoices(choices: unknown): string[] {
  if (!Array.isArray(choices)) {
    return [];
  }
  return choices.filter((item): item is string => typeof item === "string");
}

/** True when the interleaved session should show the end screen (after current submit). */
export function isInterleavedSessionEndScreen(
  sessionMode: SessionMode,
  sessionData: InterleavedSessionStored | null,
  hasSubmitted: boolean
): boolean {
  return (
    sessionMode === "interleaved" &&
    sessionData !== null &&
    hasSubmitted &&
    sessionData.completedCount + 1 >= sessionData.plan.length
  );
}

export type SpacedReviewApplyPlan =
  | { kind: "error" }
  | { kind: "has_next"; nextReview: NextReviewPayload }
  | { kind: "complete" };

export function spacedReviewApplyPlanFromApi(
  parsed: NextReviewApiResponse | null
): SpacedReviewApplyPlan {
  if (!parsed) {
    return { kind: "error" };
  }
  if (parsed.has_due_review && parsed.next_review) {
    return { kind: "has_next", nextReview: parsed.next_review };
  }
  return { kind: "complete" };
}

export function buildInterleavedSessionStorageJson(params: {
  plan: string[];
  completedCount: number;
  length: number;
  analytics: { firstAttemptTracked?: boolean };
}): string {
  return JSON.stringify({
    plan: params.plan,
    completedCount: params.completedCount,
    length: params.length,
    analytics: params.analytics,
  });
}

export function mergeInterleavedAnalyticsForNextStep(
  sessionData: InterleavedSessionStored,
  currentRawFromStorage: string | null
): { firstAttemptTracked?: boolean } {
  let analytics = sessionData.analytics ?? { firstAttemptTracked: false };
  const current = currentRawFromStorage
    ? parseInterleavedSessionFromStorage(currentRawFromStorage)
    : null;
  if (current?.analytics?.firstAttemptTracked) {
    analytics = { ...analytics, firstAttemptTracked: true };
  }
  return analytics;
}

export function resolveSolverExplanationText(
  submitExplanation: string | undefined,
  fallbackExerciseExplanation: string | null | undefined
): string {
  return submitExplanation || fallbackExerciseExplanation || "";
}
