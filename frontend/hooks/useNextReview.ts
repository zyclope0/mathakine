"use client";

import { useCallback, useState } from "react";
import { api, ApiClientError } from "@/lib/api/client";
import {
  parseNextReviewApiResponse,
  type NextReviewApiResponse,
} from "@/lib/validation/spacedRepetitionNextReview";

export type { NextReviewApiResponse };

/**
 * GET /api/users/me/reviews/next — parse côté client, pas de cache React Query ici.
 */
export async function fetchNextReviewApi(): Promise<NextReviewApiResponse | null> {
  const raw = await api.get<unknown>("/api/users/me/reviews/next");
  return parseNextReviewApiResponse(raw);
}

export function useNextReview() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNextReview = useCallback(async (): Promise<NextReviewApiResponse | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const raw = await api.get<unknown>("/api/users/me/reviews/next");
      const parsed = parseNextReviewApiResponse(raw);
      if (!parsed) {
        setError("invalid_payload");
        return null;
      }
      return parsed;
    } catch (e) {
      if (e instanceof ApiClientError) {
        setError(e.message || "request_failed");
      } else {
        setError("request_failed");
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { fetchNextReview, isLoading, error, clearError };
}
