"use client";

import { Suspense } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout } from "@/components/layout";
import { ExercisesListLoadingShell } from "@/components/shared/ListLoadingShells";
import { ExercisesPageContent } from "@/components/exercises/ExercisesPageContent";

/**
 * Liste exercices — coque `Suspense` + route. Voir `ExercisesPageContent` pour hooks et filtres.
 */
export default function ExercisesPage() {
  return (
    <Suspense
      fallback={
        <ProtectedRoute>
          <PageLayout compact>
            <ExercisesListLoadingShell />
          </PageLayout>
        </ProtectedRoute>
      }
    >
      <ExercisesPageContent />
    </Suspense>
  );
}
