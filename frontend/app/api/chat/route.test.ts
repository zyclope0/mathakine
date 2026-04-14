/** @vitest-environment node */
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";
import * as backendUrl from "@/lib/api/backendUrl";

describe("POST /api/chat", () => {
  beforeEach(() => {
    vi.spyOn(backendUrl, "getBackendUrl").mockReturnValue("https://api.test");
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("returns 401 when access_token cookie is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "x", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(401);
    const data = await res.json();
    expect(data.code).toBe("UNAUTHORIZED");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("proxies POST JSON to backend with cookies and CSRF when authenticated", async () => {
    const backendPayload = { response: "Réponse backend" };
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => backendPayload,
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": "csrf-val",
        "Accept-Language": "fr-FR",
        cookie: "access_token=jwt-here; csrf_token=csrf-val",
      },
      body: JSON.stringify({
        message: "Bonjour",
        conversation_history: [{ role: "user", content: "a" }],
      }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual(backendPayload);

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    const call = vi.mocked(globalThis.fetch).mock.calls[0];
    expect(call?.[0]).toBe("https://api.test/api/chat");
    const init = call?.[1] as RequestInit;
    expect(init?.method).toBe("POST");
    const h = init?.headers as Record<string, string>;
    expect(h["Content-Type"]).toBe("application/json");
    expect(h["X-CSRF-Token"]).toBe("csrf-val");
    expect(h["Accept-Language"]).toBe("fr-FR");
    expect(h.Cookie).toContain("access_token=jwt-here");
    expect(h.Cookie).toContain("csrf_token=csrf-val");
    expect(init?.body).toBe(
      JSON.stringify({
        message: "Bonjour",
        conversation_history: [{ role: "user", content: "a" }],
      })
    );
  });

  it("returns 400 when message is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=t",
      },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("Message requis");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("returns 400 with English copy when Accept-Language prefers English", async () => {
    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        cookie: "access_token=t",
      },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("Message is required");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("forwards backend 401 without masking as 200 fallback", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({
        code: "UNAUTHORIZED",
        message: "Authentication required",
        error: "Authentication required",
      }),
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=expired",
      },
      body: JSON.stringify({ message: "x", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(401);
    const data = await res.json();
    expect(data.code).toBe("UNAUTHORIZED");
  });

  it("forwards backend 403 without masking as assistant fallback", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        code: "FORBIDDEN",
        message: "Token CSRF manquant. Rafraichissez la page et reessayez.",
        error: "Token CSRF manquant. Rafraichissez la page et reessayez.",
      }),
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=expired; csrf_token=stale",
      },
      body: JSON.stringify({ message: "x", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(403);
    const data = await res.json();
    expect(data.code).toBe("FORBIDDEN");
  });

  it("when backend fetch returns !ok (non-401), returns fallback assistant JSON (status 200)", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=t",
      },
      body: JSON.stringify({ message: "x", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(typeof data.response).toBe("string");
    expect(data.response.length).toBeGreaterThan(0);
  });
});
