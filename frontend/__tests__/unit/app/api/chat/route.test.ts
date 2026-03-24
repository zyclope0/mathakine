/** @vitest-environment node */
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/chat/route";
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

  it("proxies POST JSON to backend and returns backend JSON payload", async () => {
    const backendPayload = { response: "Réponse backend" };
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => backendPayload,
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Bonjour",
        conversation_history: [{ role: "user", content: "a" }],
      }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual(backendPayload);

    expect(globalThis.fetch).toHaveBeenCalledWith("https://api.test/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Bonjour",
        conversation_history: [{ role: "user", content: "a" }],
      }),
    });
  });

  it("returns 400 when message is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe("Message requis");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("when backend fetch returns !ok, returns fallback assistant JSON (status 200)", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
    } as Response);

    const req = new NextRequest("http://localhost/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "x", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(typeof data.response).toBe("string");
    expect(data.response.length).toBeGreaterThan(0);
  });
});
