"use client";

import type { ReactNode } from "react";

export interface LeaderboardCardStateProps {
  error: unknown | null;
  isLoading: boolean;
  isEmpty: boolean;
  errorContent: ReactNode;
  loadingContent: ReactNode;
  emptyContent: ReactNode;
  children: ReactNode;
}

/**
 * Branches error / loading / empty / success — même ordre et structure que l’historique page leaderboard.
 */
export function LeaderboardCardState({
  error,
  isLoading,
  isEmpty,
  errorContent,
  loadingContent,
  emptyContent,
  children,
}: LeaderboardCardStateProps) {
  if (error) return errorContent;
  if (isLoading) return loadingContent;
  if (isEmpty) return emptyContent;
  return children;
}
