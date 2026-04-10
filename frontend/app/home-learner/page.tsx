"use client";

import { HOME_LEARNER_ROUTE_ACCESS } from "@/lib/auth/routeAccess";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { HomeLearnerContent } from "@/components/learner/HomeLearnerContent";

/**
 * Page d'accueil dédiée aux apprenants (rôle canonique `apprenant`). — NI-4 / NI-13
 *
 * Structure linéaire, colonne unique, zéro onglets.
 * Voir `HomeLearnerContent` pour l'ordre conditionnel des sections.
 */
export default function HomeLearnerPage() {
  return (
    <ProtectedRoute
      requireOnboardingCompleted={HOME_LEARNER_ROUTE_ACCESS.requireOnboardingCompleted}
      allowedRoles={HOME_LEARNER_ROUTE_ACCESS.allowedRoles}
      prioritizeRoleRedirect={HOME_LEARNER_ROUTE_ACCESS.prioritizeRoleRedirect}
      redirectAuthenticatedTo={HOME_LEARNER_ROUTE_ACCESS.redirectAuthenticatedTo}
    >
      <HomeLearnerContent />
    </ProtectedRoute>
  );
}
