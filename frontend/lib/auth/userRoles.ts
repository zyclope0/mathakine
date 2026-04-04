export const CANONICAL_USER_ROLES = ["apprenant", "enseignant", "moderateur", "admin"] as const;

export type UserRole = (typeof CANONICAL_USER_ROLES)[number];

export const ADULT_DASHBOARD_ROLES: UserRole[] = ["enseignant", "moderateur", "admin"];

export const DASHBOARD_ALLOWED_ROLES: UserRole[] = ["apprenant", ...ADULT_DASHBOARD_ROLES];

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  apprenant: "Apprenant",
  enseignant: "Enseignant",
  moderateur: "Modérateur",
  admin: "Admin",
};

const LEGACY_TO_CANONICAL_USER_ROLE: Record<string, UserRole> = {
  padawan: "apprenant",
  maitre: "enseignant",
  gardien: "moderateur",
  archiviste: "admin",
};

export function normalizeUserRole(role: string | null | undefined): UserRole | null {
  if (!role) {
    return null;
  }

  const normalized = role.trim().toLowerCase();
  if ((CANONICAL_USER_ROLES as readonly string[]).includes(normalized)) {
    return normalized as UserRole;
  }

  return LEGACY_TO_CANONICAL_USER_ROLE[normalized] ?? null;
}

export function isApprenantRole(role: string | null | undefined): boolean {
  return normalizeUserRole(role) === "apprenant";
}

export function isAdminRole(role: string | null | undefined): boolean {
  return normalizeUserRole(role) === "admin";
}

export function canAccessDashboardAdulte(role: string | null | undefined): boolean {
  const normalizedRole = normalizeUserRole(role);
  return normalizedRole !== null && ADULT_DASHBOARD_ROLES.includes(normalizedRole);
}

export function getDefaultHomeRoute(
  role: string | null | undefined
): "/home-learner" | "/dashboard" {
  return isApprenantRole(role) ? "/home-learner" : "/dashboard";
}

export function getDefaultPostLoginRoute(
  role: string | null | undefined
): "/home-learner" | "/dashboard" {
  return isApprenantRole(role) ? "/home-learner" : "/dashboard";
}

export function getUserRoleLabel(role: string | null | undefined): string {
  const normalizedRole = normalizeUserRole(role);
  if (!normalizedRole) {
    return role ?? "";
  }
  return USER_ROLE_LABELS[normalizedRole];
}
