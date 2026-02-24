"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  /** Si true, redirige vers /exercises si access_scope === "exercises_only" */
  requireFullAccess?: boolean;
  /** Si true, redirige vers /onboarding si onboarding_completed_at est null */
  requireOnboardingCompleted?: boolean;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  requireAuth = true,
  requireFullAccess = false,
  requireOnboardingCompleted = false,
  redirectTo = "/login",
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const [showContent, setShowContent] = useState(false);

  // Timeout de sécurité : après 1.5 secondes, afficher quand même le contenu
  useEffect(() => {
    if (isLoading && user === null && !hasCheckedAuth) {
      const timer = setTimeout(() => {
        // Log uniquement en développement
        if (process.env.NODE_ENV === "development") {
          console.log("[ProtectedRoute] Timeout sécurité - affichage du contenu");
        }
        setShowContent(true);
        setHasCheckedAuth(true);
      }, 1500);

      return () => clearTimeout(timer);
    } else if (user !== null || !isLoading) {
      // Si on a des données utilisateur ou que le chargement est terminé, afficher immédiatement
      setShowContent(true);
      if (!hasCheckedAuth) {
        setHasCheckedAuth(true);
      }
    }
  }, [isLoading, user, hasCheckedAuth]);

  // Vérifier l'authentification, l'accès complet et l'onboarding
  useEffect(() => {
    if (!hasCheckedAuth) return;
    // Onboarding non complété sur une route qui l'exige
    if (
      requireOnboardingCompleted &&
      user &&
      !user.onboarding_completed_at &&
      user.access_scope !== "exercises_only"
    ) {
      if (process.env.NODE_ENV === "development") {
        console.log("[ProtectedRoute] Onboarding non complété → redirection vers /onboarding");
      }
      setShouldRedirect(true);
      router.push("/onboarding");
      return;
    }
    // Accès limité (exercises_only) sur une route qui exige full
    if (requireFullAccess && user && user.access_scope === "exercises_only") {
      if (process.env.NODE_ENV === "development") {
        console.log("[ProtectedRoute] Accès limité → redirection vers /exercises");
      }
      setShouldRedirect(true);
      router.push("/exercises");
      return;
    }
    // Non authentifié
    if (requireAuth && !isAuthenticated && user === null) {
      if (process.env.NODE_ENV === "development") {
        console.log("[ProtectedRoute] Redirection vers", redirectTo);
      }
      setShouldRedirect(true);
      router.push(redirectTo);
    }
  }, [
    hasCheckedAuth,
    requireAuth,
    requireFullAccess,
    requireOnboardingCompleted,
    isAuthenticated,
    router,
    redirectTo,
    user,
  ]);

  // Si on est en chargement initial ET qu'on n'a pas encore de données utilisateur en cache
  // ET qu'on n'a pas encore dépassé le timeout de sécurité
  // MAIS seulement lors du premier chargement (pas navigation côté client)
  if (isLoading && user === null && !hasCheckedAuth && !showContent) {
    // Log uniquement en développement
    if (process.env.NODE_ENV === "development") {
      console.log("[ProtectedRoute] Affichage du loader");
    }
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    );
  }

  // Si on doit rediriger
  const mustRedirectToLogin = hasCheckedAuth && requireAuth && !isAuthenticated;
  const mustRedirectToExercises =
    hasCheckedAuth && requireFullAccess && user && user.access_scope === "exercises_only";
  const mustRedirectToOnboarding =
    hasCheckedAuth &&
    requireOnboardingCompleted &&
    user &&
    !user.onboarding_completed_at &&
    user.access_scope !== "exercises_only";
  if (
    shouldRedirect ||
    mustRedirectToLogin ||
    mustRedirectToExercises ||
    mustRedirectToOnboarding
  ) {
    return null;
  }

  // Si on a des données utilisateur en cache (même si isLoading est true lors de la navigation),
  // ou si on a fini de charger, afficher le contenu immédiatement
  // Cela permet la navigation côté client fluide sans attendre le rechargement
  return <>{children}</>;
}
