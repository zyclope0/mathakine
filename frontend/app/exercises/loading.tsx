"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout } from "@/components/layout/PageLayout";
import { ExercisesListLoadingShell } from "@/components/shared/ListLoadingShells";

/**
 * Chargement segment /exercises — même structure que la page (header + toolbar + liste skeleton).
 */
export default function ExercisesLoading() {
  return (
    <ProtectedRoute>
      <PageLayout compact>
        <ExercisesListLoadingShell />
      </PageLayout>
    </ProtectedRoute>
  );
}
