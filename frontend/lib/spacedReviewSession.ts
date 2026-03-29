"use client";

import {
  parseNextReviewApiResponse,
  type NextReviewApiResponse,
  type NextReviewPayload,
} from "@/lib/validation/spacedRepetitionNextReview";

const SPACED_REVIEW_STORAGE_KEY = "spaced_review_next";

function canUseSessionStorage(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

export function storeSpacedReviewNext(nextReview: NextReviewPayload): void {
  if (!canUseSessionStorage()) {
    return;
  }
  try {
    sessionStorage.setItem(
      SPACED_REVIEW_STORAGE_KEY,
      JSON.stringify({
        has_due_review: true,
        summary: {
          f04_initialized: false,
          active_cards_count: 0,
          due_today_count: 0,
          overdue_count: 0,
          next_review_date: null,
        },
        next_review: nextReview,
      } satisfies Partial<NextReviewApiResponse>)
    );
  } catch {
    // Ignore unavailable storage.
  }
}

export function readSpacedReviewNext(exerciseId?: number): NextReviewPayload | null {
  if (!canUseSessionStorage()) {
    return null;
  }
  try {
    const raw = sessionStorage.getItem(SPACED_REVIEW_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = parseNextReviewApiResponse(JSON.parse(raw));
    if (!parsed?.has_due_review || !parsed.next_review) {
      return null;
    }
    if (exerciseId != null && parsed.next_review.exercise_id !== exerciseId) {
      return null;
    }
    return parsed.next_review;
  } catch {
    return null;
  }
}

export function clearSpacedReviewNext(): void {
  if (!canUseSessionStorage()) {
    return;
  }
  try {
    sessionStorage.removeItem(SPACED_REVIEW_STORAGE_KEY);
  } catch {
    // Ignore unavailable storage.
  }
}
