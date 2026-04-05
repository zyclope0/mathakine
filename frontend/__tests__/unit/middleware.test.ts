/** @vitest-environment node */

import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { proxy } from "@/proxy";
import { resolveRouteAccessUser } from "@/lib/auth/server/routeSession";

vi.mock("@/lib/auth/server/routeSession", () => ({
  resolveRouteAccessUser: vi.fn(),
}));

describe("frontend middleware", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("redirige un apprenant non admin depuis /admin vers /home-learner", async () => {
    vi.mocked(resolveRouteAccessUser).mockResolvedValue({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "apprenant",
      },
    });

    const request = new NextRequest("https://mathakine.test/admin");
    const response = await proxy(request);

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://mathakine.test/home-learner");
  });

  it("redirige un utilisateur sans cookie vers /login sur /dashboard", async () => {
    vi.mocked(resolveRouteAccessUser).mockResolvedValue({
      state: "unauthenticated",
      user: null,
    });

    const request = new NextRequest("https://mathakine.test/dashboard");
    const response = await proxy(request);

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://mathakine.test/login");
  });

  it("laisse passer un apprenant authentifié vers /dashboard", async () => {
    vi.mocked(resolveRouteAccessUser).mockResolvedValue({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "apprenant",
        access_scope: "full",
        onboarding_completed_at: "2026-04-05T10:00:00Z",
      },
    });

    const request = new NextRequest("https://mathakine.test/dashboard");
    const response = await proxy(request);

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("redirige un rôle adulte vers /dashboard depuis /home-learner même sans onboarding", async () => {
    vi.mocked(resolveRouteAccessUser).mockResolvedValue({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "enseignant",
        access_scope: "full",
        onboarding_completed_at: null,
      },
    });

    const request = new NextRequest("https://mathakine.test/home-learner");
    const response = await proxy(request);

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("https://mathakine.test/dashboard");
  });

  it("retombe sur le guard client si la résolution serveur reste indéterminée", async () => {
    vi.mocked(resolveRouteAccessUser).mockResolvedValue({
      state: "indeterminate",
      user: null,
    });

    const request = new NextRequest("https://mathakine.test/home-learner");
    const response = await proxy(request);

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });
});
