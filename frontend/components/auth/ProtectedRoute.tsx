"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { LoadingState } from "@/components/layout/LoadingState";
import { getProtectedRouteRedirect } from "@/lib/auth/routeAccess";
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
  prioritizeRoleRedirect?: boolean;
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
  prioritizeRoleRedirect = false,
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
  const routeAccessUser =
    hasCheckedAuth && user !== null
      ? {
          isAuthenticated,
          role: user.role,
          access_scope: user.access_scope ?? null,
          onboarding_completed_at: user.onboarding_completed_at ?? null,
        }
      : hasCheckedAuth
        ? { isAuthenticated: false }
        : null;
  const redirectTarget = hasCheckedAuth
    ? getProtectedRouteRedirect(routeAccessUser, {
        requireAuth,
        requireFullAccess,
        requireOnboardingCompleted,
        allowedRoles,
        prioritizeRoleRedirect,
        redirectTo,
        redirectAuthenticatedTo,
      })
    : null;
  const mustRedirectForRole =
    redirectTarget !== null &&
    redirectTarget !== redirectTo &&
    redirectTarget !== "/onboarding" &&
    redirectTarget !== "/exercises";

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
