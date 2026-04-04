"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { LoadingState } from "@/components/layout/LoadingState";
import { getDefaultHomeRoute, normalizeUserRole } from "@/lib/auth/userRoles";
import type { UserRole } from "@/lib/auth/userRoles";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  /** Si true, redirige vers /exercises si access_scope === "exercises_only" */
  requireFullAccess?: boolean;
  /** Si true, redirige vers /onboarding si onboarding_completed_at est null */
  requireOnboardingCompleted?: boolean;
  /** Rôles canoniques autorisés sur cette surface. */
  allowedRoles?: UserRole[];
  redirectTo?: string;
  /** Redirection si l'utilisateur est authentifié mais n'a pas le bon rôle. */
  redirectAuthenticatedTo?: string;
}

export function ProtectedRoute({
  children,
  requireAuth = true,
  requireFullAccess = false,
  requireOnboardingCompleted = false,
  allowedRoles,
  redirectTo = "/login",
  redirectAuthenticatedTo,
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const lastRedirectRef = useRef<string | null>(null);

  useEffect(() => {
    if (!(isLoading && user === null) || hasTimedOut) {
      return;
    }

    const timer = window.setTimeout(() => {
      setHasTimedOut(true);
    }, 1500);

    return () => clearTimeout(timer);
  }, [isLoading, user, hasTimedOut]);

  const hasCheckedAuth = hasTimedOut || user !== null || !isLoading;
  const normalizedUserRole = normalizeUserRole(user?.role);
  const mustRedirectToOnboarding =
    hasCheckedAuth &&
    requireOnboardingCompleted &&
    user &&
    !user.onboarding_completed_at &&
    user.access_scope !== "exercises_only";
  const mustRedirectToExercises =
    hasCheckedAuth && requireFullAccess && user && user.access_scope === "exercises_only";
  const mustRedirectToLogin = hasCheckedAuth && requireAuth && !isAuthenticated && user === null;
  const mustRedirectForRole =
    hasCheckedAuth &&
    user !== null &&
    !!allowedRoles &&
    (normalizedUserRole === null || !allowedRoles.includes(normalizedUserRole));
  const authenticatedFallbackRoute = redirectAuthenticatedTo ?? getDefaultHomeRoute(user?.role);

  const redirectTarget = mustRedirectToOnboarding
    ? "/onboarding"
    : mustRedirectToExercises
      ? "/exercises"
      : mustRedirectForRole
        ? authenticatedFallbackRoute
      : mustRedirectToLogin
        ? redirectTo
        : null;

  useEffect(() => {
    if (!redirectTarget) {
      lastRedirectRef.current = null;
      return;
    }

    if (lastRedirectRef.current === redirectTarget) {
      return;
    }

    if (process.env.NODE_ENV === "development") {
      if (redirectTarget === "/onboarding") {
        console.log("[ProtectedRoute] Onboarding non complété → redirection vers /onboarding");
      } else if (redirectTarget === "/exercises") {
        console.log("[ProtectedRoute] Accès limité → redirection vers /exercises");
      } else if (mustRedirectForRole) {
        console.log("[ProtectedRoute] Rôle interdit → redirection vers", redirectTarget);
      } else {
        console.log("[ProtectedRoute] Redirection vers", redirectTarget);
      }
    }

    lastRedirectRef.current = redirectTarget;
    router.replace(redirectTarget);
  }, [mustRedirectForRole, redirectTarget, router]);

  if (isLoading && user === null && !hasCheckedAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <LoadingState className="min-h-0 py-8" />
      </div>
    );
  }

  if (redirectTarget) {
    return null;
  }

  return <>{children}</>;
}
