import type { UserRole } from "@/lib/auth/userRoles";
import {
  DASHBOARD_ALLOWED_ROLES,
  getDefaultHomeRoute,
  normalizeUserRole,
} from "@/lib/auth/userRoles";

export interface RouteAccessRequirements {
  requireAuth?: boolean | undefined;
  requireFullAccess?: boolean | undefined;
  requireOnboardingCompleted?: boolean | undefined;
  requireServerProfile?: boolean | undefined;
  allowedRoles?: UserRole[] | undefined;
  redirectTo?: string | undefined;
  redirectAuthenticatedTo?: string | undefined;
  prioritizeRoleRedirect?: boolean | undefined;
}

export interface RouteAccessUser {
  role?: string | null;
  access_scope?: string | null;
  onboarding_completed_at?: string | null;
  isAuthenticated: boolean;
}

export const HOME_LEARNER_ROUTE_ACCESS = {
  requireAuth: true,
  requireOnboardingCompleted: true,
  allowedRoles: ["apprenant"],
  redirectAuthenticatedTo: "/dashboard",
  prioritizeRoleRedirect: true,
} satisfies RouteAccessRequirements;

export const DASHBOARD_ROUTE_ACCESS = {
  requireAuth: true,
  requireFullAccess: true,
  requireOnboardingCompleted: true,
  allowedRoles: DASHBOARD_ALLOWED_ROLES,
} satisfies RouteAccessRequirements;

export const ADMIN_ROUTE_ACCESS = {
  requireAuth: true,
  allowedRoles: ["admin"],
  requireServerProfile: true,
} satisfies RouteAccessRequirements;

export function getRouteAccessRequirementsForPath(
  pathname: string
): RouteAccessRequirements | null {
  if (pathname === "/dashboard" || pathname.startsWith("/dashboard/")) {
    return DASHBOARD_ROUTE_ACCESS;
  }

  if (pathname === "/home-learner" || pathname.startsWith("/home-learner/")) {
    return HOME_LEARNER_ROUTE_ACCESS;
  }

  if (pathname === "/admin" || pathname.startsWith("/admin/")) {
    return ADMIN_ROUTE_ACCESS;
  }

  return null;
}

export function routeNeedsServerProfile(requirements: RouteAccessRequirements): boolean {
  return (
    !!requirements.requireFullAccess ||
    !!requirements.requireOnboardingCompleted ||
    !!requirements.requireServerProfile
  );
}

export function getProtectedRouteRedirect(
  user: RouteAccessUser | null,
  requirements: RouteAccessRequirements
): string | null {
  const {
    requireAuth = true,
    requireFullAccess = false,
    requireOnboardingCompleted = false,
    requireServerProfile = false,
    allowedRoles,
    redirectTo = "/login",
    redirectAuthenticatedTo,
    prioritizeRoleRedirect = false,
  } = requirements;

  const isAuthenticated = user?.isAuthenticated === true;
  if (requireAuth && !isAuthenticated) {
    return redirectTo;
  }

  if (!user) {
    return null;
  }

  const normalizedRole = normalizeUserRole(user.role);
  const roleRedirectTarget =
    allowedRoles && (!normalizedRole || !allowedRoles.includes(normalizedRole))
      ? (redirectAuthenticatedTo ?? getDefaultHomeRoute(user.role))
      : null;

  if (prioritizeRoleRedirect && roleRedirectTarget) {
    return roleRedirectTarget;
  }

  if (
    requireOnboardingCompleted &&
    !user.onboarding_completed_at &&
    user.access_scope !== "exercises_only"
  ) {
    return "/onboarding";
  }

  if (requireFullAccess && user.access_scope === "exercises_only") {
    return "/exercises";
  }

  if (roleRedirectTarget) {
    return roleRedirectTarget;
  }

  if (requireServerProfile && !user.role) {
    return redirectAuthenticatedTo ?? getDefaultHomeRoute(user.role);
  }

  return null;
}
