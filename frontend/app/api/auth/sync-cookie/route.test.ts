/** @vitest-environment node */
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";
import { resetValidateTokenRuntimeForTests } from "@/lib/auth/server/validateTokenRuntime";

describe("POST /api/auth/sync-cookie", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    resetValidateTokenRuntimeForTests();
  });

  it("returns 400 for syntactically invalid JWT before backend validation", async () => {
    const request = new NextRequest("http://localhost/api/auth/sync-cookie", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: "not-a-jwt" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: "Format de token invalide" });
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("validates a well-formed JWT with the backend before setting the cookie", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
    } as Response);

    const token = "aaa.bbb.ccc";
    const request = new NextRequest("http://localhost/api/auth/sync-cookie", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: token }),
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    expect(response.headers.get("Set-Cookie")).toContain(`access_token=${token}`);
  });
});
