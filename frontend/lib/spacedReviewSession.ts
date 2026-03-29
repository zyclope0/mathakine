"use client";

import {
  parseNextReviewApiResponse,
  type NextReviewApiResponse,
  type NextReviewPayload,
} from "@/lib/validation/spacedRepetitionNextReview";
import { readSessionJson, removeSessionKey, STORAGE_KEYS, writeSessionJson } from "@/lib/storage";

export function storeSpacedReviewNext(nextReview: NextReviewPayload): void {
  writeSessionJson(STORAGE_KEYS.spacedReviewNext, {
    has_due_review: true,
    summary: {
      f04_initialized: false,
      active_cards_count: 0,
      due_today_count: 0,
      overdue_count: 0,
      next_review_date: null,
    },
    next_review: nextReview,
  } satisfies Partial<NextReviewApiResponse>);
}

export function readSpacedReviewNext(exerciseId?: number): NextReviewPayload | null {
  const raw = readSessionJson(STORAGE_KEYS.spacedReviewNext);
  if (raw === null) {
    return null;
  }
  const parsed = parseNextReviewApiResponse(raw);
  if (!parsed?.has_due_review || !parsed.next_review) {
    return null;
  }
  if (exerciseId != null && parsed.next_review.exercise_id !== exerciseId) {
    return null;
  }
  return parsed.next_review;
}

export function clearSpacedReviewNext(): void {
  removeSessionKey(STORAGE_KEYS.spacedReviewNext);
}
