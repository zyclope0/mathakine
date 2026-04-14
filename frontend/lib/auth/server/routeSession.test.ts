/** @vitest-environment node */

import { afterEach, describe, expect, it, vi } from "vitest";
import { resolveRouteAccessUser } from "./routeSession";
import { resetValidateTokenRuntimeForTests } from "./validateTokenRuntime";

function toBase64Url(value: string): string {
  return Buffer.from(value).toString("base64url");
}

async function createAccessToken(
  secret: string,
  payload: Record<string, unknown>
): Promise<string> {
  const header = { alg: "HS256", typ: "JWT" };
  const encodedHeader = toBase64Url(JSON.stringify(header));
  const encodedPayload = toBase64Url(JSON.stringify(payload));
  const signingInput = `${encodedHeader}.${encodedPayload}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signingInput));
  const encodedSignature = Buffer.from(new Uint8Array(signature)).toString("base64url");
  return `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
}

describe("resolveRouteAccessUser", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
    resetValidateTokenRuntimeForTests();
  });

  it("revalide /admin via le backend même si le JWT local est valide", async () => {
    vi.stubEnv("SECRET_KEY", "test-secret");
    vi.stubEnv("NODE_ENV", "development");

    const token = await createAccessToken("test-secret", {
      sub: "alice",
      role: "admin",
      exp: Math.floor(Date.now() / 1000) + 600,
      type: "access",
    });
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          role: "admin",
          access_scope: "full",
          onboarding_completed_at: "2026-04-05T10:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await resolveRouteAccessUser("/admin", token);

    expect(result).toEqual({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "admin",
        access_scope: "full",
        onboarding_completed_at: "2026-04-05T10:00:00Z",
      },
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it("refuse /admin si la vérité backend n'est plus admin", async () => {
    vi.stubEnv("SECRET_KEY", "test-secret");
    vi.stubEnv("NODE_ENV", "development");

    const token = await createAccessToken("test-secret", {
      sub: "alice",
      role: "admin",
      exp: Math.floor(Date.now() / 1000) + 600,
      type: "access",
    });

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          role: "enseignant",
          access_scope: "full",
          onboarding_completed_at: "2026-04-05T10:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await resolveRouteAccessUser("/admin", token);

    expect(result).toEqual({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "enseignant",
        access_scope: "full",
        onboarding_completed_at: "2026-04-05T10:00:00Z",
      },
    });
  });

  it("refuse /admin si le backend ne reconnaît plus l'utilisateur", async () => {
    vi.stubEnv("SECRET_KEY", "test-secret");
    vi.stubEnv("NODE_ENV", "development");

    const token = await createAccessToken("test-secret", {
      sub: "alice",
      role: "admin",
      exp: Math.floor(Date.now() / 1000) + 600,
      type: "access",
    });

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response(null, { status: 401 }));

    const result = await resolveRouteAccessUser("/admin", token);

    expect(result).toEqual({
      state: "unauthenticated",
      user: null,
    });
  });

  it("enrichit la session via le backend pour dashboard", async () => {
    vi.stubEnv("SECRET_KEY", "test-secret");
    vi.stubEnv("NODE_ENV", "development");

    const token = await createAccessToken("test-secret", {
      sub: "bob",
      role: "apprenant",
      exp: Math.floor(Date.now() / 1000) + 600,
      type: "access",
    });

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          role: "apprenant",
          access_scope: "full",
          onboarding_completed_at: "2026-04-05T10:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await resolveRouteAccessUser("/dashboard", token);

    expect(result).toEqual({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "apprenant",
        access_scope: "full",
        onboarding_completed_at: "2026-04-05T10:00:00Z",
      },
    });
  });

  it("retombe sur la validation backend quand la clé locale n'est pas disponible", async () => {
    vi.stubEnv("SECRET_KEY", "");
    vi.stubEnv("NODE_ENV", "development");

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ valid: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            role: "admin",
            access_scope: "full",
            onboarding_completed_at: "2026-04-05T10:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );

    const result = await resolveRouteAccessUser("/dashboard", "opaque-token");

    expect(result).toEqual({
      state: "authenticated",
      user: {
        isAuthenticated: true,
        role: "admin",
        access_scope: "full",
        onboarding_completed_at: "2026-04-05T10:00:00Z",
      },
    });
  });
});
