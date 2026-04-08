"use client";

import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingState } from "@/components/layout";

export interface AdminStatePanelProps {
  hasError: boolean;
  errorMessage: string;
  isLoading: boolean;
  loadingMessage: string;
  /** When true (after error/loading cleared), shows the muted empty card instead of children. */
  isEmpty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
}

/**
 * Shared read-heavy admin branch: error card → loading → optional empty → success children.
 * FFI-L20F — structure only; copy and domain content stay in each page.
 */
export function AdminStatePanel({
  hasError,
  errorMessage,
  isLoading,
  loadingMessage,
  isEmpty = false,
  emptyMessage = "Aucune donnée.",
  children,
}: AdminStatePanelProps) {
  if (hasError) {
    return (
      <Card>
        <CardContent className="py-12">
          <p className="text-center text-destructive">{errorMessage}</p>
        </CardContent>
      </Card>
    );
  }
  if (isLoading) {
    return <LoadingState message={loadingMessage} />;
  }
  if (isEmpty) {
    return (
      <Card>
        <CardContent className="py-12">
          <p className="text-center text-muted-foreground">{emptyMessage}</p>
        </CardContent>
      </Card>
    );
  }
  return <>{children}</>;
}
