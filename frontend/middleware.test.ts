/** @vitest-environment node */

import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { proxy } from "@/proxy";
import { resolveRouteAccessUser } from "@/lib/auth/server/routeSession";
import { CSP_NONCE_REQUEST_HEADER } from "@/lib/security/middlewareCsp";

vi.mock("@/lib/auth/server/routeSession", () => ({
  resolveRouteAccessUser: vi.fn(),
}));

describe("frontend middleware", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
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

  // QF-07C: forwarded nonce must match script-src; RootLayout reads x-nonce for <html nonce> so Next tags inline framework scripts.
  it("applique une CSP dynamique en non-development avec nonce et sans unsafe-inline dans script-src", async () => {
    vi.stubEnv("NODE_ENV", "production");

    const request = new NextRequest("https://mathakine.test/login");
    const response = await proxy(request);

    expect(response.status).toBe(200);
    const csp = response.headers.get("content-security-policy");
    expect(csp).toBeTruthy();
    const scriptSrc = csp!.match(/script-src[^;]+/)?.[0] ?? "";
    expect(scriptSrc).toMatch(/script-src 'self' 'nonce-[^']+'/);
    expect(scriptSrc).not.toContain("unsafe-inline");
    expect(scriptSrc).not.toContain("unsafe-eval");
    expect(csp).toContain("style-src 'self' 'unsafe-inline'");
    const forwardedNonce = response.headers.get(`x-middleware-request-${CSP_NONCE_REQUEST_HEADER}`);
    expect(forwardedNonce).toBeTruthy();
    expect(scriptSrc).toContain(`'nonce-${forwardedNonce}'`);
    expect(response.headers.get("x-middleware-override-headers")).toContain(
      CSP_NONCE_REQUEST_HEADER
    );
  });

  it("applique une CSP pragmatique en development (unsafe-inline et unsafe-eval dans script-src)", async () => {
    vi.stubEnv("NODE_ENV", "development");

    const request = new NextRequest("https://mathakine.test/login");
    const response = await proxy(request);

    const csp = response.headers.get("content-security-policy");
    expect(csp).toBeTruthy();
    const scriptSrc = csp!.match(/script-src[^;]+/)?.[0] ?? "";
    expect(scriptSrc).toContain("'unsafe-inline'");
    expect(scriptSrc).toContain("'unsafe-eval'");
  });
});
