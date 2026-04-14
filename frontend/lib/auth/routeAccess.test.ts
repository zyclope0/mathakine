import { describe, expect, it } from "vitest";
import {
  ADMIN_ROUTE_ACCESS,
  DASHBOARD_ROUTE_ACCESS,
  getProtectedRouteRedirect,
  getRouteAccessRequirementsForPath,
  HOME_LEARNER_ROUTE_ACCESS,
} from "./routeAccess";

describe("routeAccess helpers", () => {
  it("retourne la configuration attendue selon la route", () => {
    expect(getRouteAccessRequirementsForPath("/dashboard")).toBe(DASHBOARD_ROUTE_ACCESS);
    expect(getRouteAccessRequirementsForPath("/home-learner")).toBe(HOME_LEARNER_ROUTE_ACCESS);
    expect(getRouteAccessRequirementsForPath("/admin/users")).toBe(ADMIN_ROUTE_ACCESS);
    expect(getRouteAccessRequirementsForPath("/exercises")).toBeNull();
  });

  it("redirige vers /login sans session pour une route protégée", () => {
    expect(getProtectedRouteRedirect(null, DASHBOARD_ROUTE_ACCESS)).toBe("/login");
  });

  it("redirige un rôle adulte vers /dashboard avant l'onboarding sur /home-learner", () => {
    expect(
      getProtectedRouteRedirect(
        {
          isAuthenticated: true,
          role: "enseignant",
          access_scope: "full",
          onboarding_completed_at: null,
        },
        HOME_LEARNER_ROUTE_ACCESS
      )
    ).toBe("/dashboard");
  });

  it("redirige un accès limité vers /exercises avant toute autre surface", () => {
    expect(
      getProtectedRouteRedirect(
        {
          isAuthenticated: true,
          role: "apprenant",
          access_scope: "exercises_only",
          onboarding_completed_at: null,
        },
        DASHBOARD_ROUTE_ACCESS
      )
    ).toBe("/exercises");
  });

  it("redirige un non-admin authentifié vers sa surface par défaut", () => {
    expect(
      getProtectedRouteRedirect(
        {
          isAuthenticated: true,
          role: "apprenant",
        },
        ADMIN_ROUTE_ACCESS
      )
    ).toBe("/home-learner");
  });
});
