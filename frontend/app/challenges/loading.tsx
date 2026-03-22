"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout } from "@/components/layout/PageLayout";
import { ChallengesListLoadingShell } from "@/components/shared/ListLoadingShells";

/**
 * Chargement segment /challenges — aligné sur la page défis (header + filtres + liste skeleton).
 */
export default function ChallengesLoading() {
  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout compact>
        <ChallengesListLoadingShell />
      </PageLayout>
    </ProtectedRoute>
  );
}
