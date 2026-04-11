"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LeaderboardPageContent } from "@/components/leaderboard/LeaderboardPageContent";

/**
 * Entrée route classement — coque auth. Voir `LeaderboardPageContent` pour hooks et listes.
 */
export default function LeaderboardPage() {
  return (
    <ProtectedRoute requireFullAccess>
      <LeaderboardPageContent />
    </ProtectedRoute>
  );
}
