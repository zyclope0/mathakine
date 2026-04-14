import { describe, expect, it } from "vitest";
import {
  USER_ROLE_LABELS,
  canAccessDashboardAdulte,
  DASHBOARD_ALLOWED_ROLES,
  getDefaultHomeRoute,
  getDefaultPostLoginRoute,
  getUserRoleLabel,
  isAdminRole,
  isApprenantRole,
  normalizeUserRole,
} from "./userRoles";

describe("userRoles helpers", () => {
  it("normalise les aliases legacy vers les roles canoniques", () => {
    expect(normalizeUserRole("padawan")).toBe("apprenant");
    expect(normalizeUserRole("maitre")).toBe("enseignant");
    expect(normalizeUserRole("gardien")).toBe("moderateur");
    expect(normalizeUserRole("archiviste")).toBe("admin");
  });

  it("conserve les roles canoniques valides", () => {
    expect(normalizeUserRole("apprenant")).toBe("apprenant");
    expect(normalizeUserRole("enseignant")).toBe("enseignant");
    expect(normalizeUserRole("moderateur")).toBe("moderateur");
    expect(normalizeUserRole("admin")).toBe("admin");
  });

  it("derive les bonnes routes par defaut", () => {
    expect(getDefaultHomeRoute("apprenant")).toBe("/home-learner");
    expect(getDefaultHomeRoute("admin")).toBe("/dashboard");
    expect(getDefaultPostLoginRoute("padawan")).toBe("/home-learner");
    expect(getDefaultPostLoginRoute("moderateur")).toBe("/dashboard");
  });

  it("applique correctement les helpers d'audience", () => {
    expect(isApprenantRole("apprenant")).toBe(true);
    expect(isApprenantRole("padawan")).toBe(true);
    expect(isApprenantRole("enseignant")).toBe(false);

    expect(isAdminRole("admin")).toBe(true);
    expect(isAdminRole("archiviste")).toBe(true);
    expect(isAdminRole("moderateur")).toBe(false);

    expect(canAccessDashboardAdulte("apprenant")).toBe(false);
    expect(canAccessDashboardAdulte("enseignant")).toBe(true);
    expect(canAccessDashboardAdulte("gardien")).toBe(true);
  });

  it("retourne des labels UI stables", () => {
    expect(getUserRoleLabel("apprenant")).toBe(USER_ROLE_LABELS.apprenant);
    expect(getUserRoleLabel("enseignant")).toBe(USER_ROLE_LABELS.enseignant);
    expect(getUserRoleLabel("moderateur")).toBe(USER_ROLE_LABELS.moderateur);
    expect(getUserRoleLabel("admin")).toBe(USER_ROLE_LABELS.admin);
  });

  it("autorise une entree discrete au dashboard sans changer la home apprenant", () => {
    expect(DASHBOARD_ALLOWED_ROLES).toContain("apprenant");
    expect(getDefaultHomeRoute("apprenant")).toBe("/home-learner");
  });
});
