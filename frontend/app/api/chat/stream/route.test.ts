/** @vitest-environment node */
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";
import * as backendUrl from "@/lib/api/backendUrl";

function sseStream(chunk: string): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(chunk));
      controller.close();
    },
  });
}

describe("POST /api/chat/stream", () => {
  beforeEach(() => {
    vi.spyOn(backendUrl, "getBackendUrl").mockReturnValue("https://api.test");
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("returns 401 when access_token cookie is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(401);
    const data = await res.json();
    expect(data.code).toBe("UNAUTHORIZED");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("forwards backend 200 stream as SSE Response with text/event-stream", async () => {
    const body = sseStream('data: {"type":"token","content":"a"}\n\n');
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body,
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=tok; csrf_token=c1",
        "X-CSRF-Token": "c1",
        "Accept-Language": "en",
      },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    expect(res.headers.get("cache-control")).toBe("no-cache");

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    const call = vi.mocked(globalThis.fetch).mock.calls[0];
    expect(call?.[0]).toBe("https://api.test/api/chat/stream");
    const init = call?.[1] as RequestInit;
    const h = init?.headers as Record<string, string>;
    expect(h.Cookie).toContain("access_token=tok");
    expect(h["X-CSRF-Token"]).toBe("c1");
    expect(init?.body).toBe(
      JSON.stringify({
        message: "hi",
        conversation_history: [],
        stream: true,
      })
    );
  });

  it("returns SSE error event when backend responds 200 with an empty stream body", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body: null,
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=tok; csrf_token=c1",
      },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    const text = await res.text();
    expect(text).toContain("error");
  });

  it("returns 500 JSON when getBackendUrl throws (no silent localhost in prod config)", async () => {
    vi.spyOn(backendUrl, "getBackendUrl").mockImplementation(() => {
      throw new Error("NEXT_PUBLIC_API_BASE_URL doit être défini en production.");
    });

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=x",
      },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(500);
    expect(res.headers.get("content-type")).toBe("application/json");
    const data = JSON.parse(await res.text());
    expect(data.error).toContain("NEXT_PUBLIC_API_BASE_URL");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("returns JSON 401 when backend returns 401", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 401,
      text: async () =>
        JSON.stringify({
          code: "UNAUTHORIZED",
          message: "Authentication required",
          error: "Authentication required",
        }),
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=bad",
      },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(401);
    expect(res.headers.get("content-type")).toContain("application/json");
    const data = await res.json();
    expect(data.code).toBe("UNAUTHORIZED");
  });

  it("returns JSON 403 when backend returns 403", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 403,
      text: async () =>
        JSON.stringify({
          code: "FORBIDDEN",
          message: "Token CSRF manquant. Rafraichissez la page et reessayez.",
          error: "Token CSRF manquant. Rafraichissez la page et reessayez.",
        }),
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=bad; csrf_token=stale",
      },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(403);
    expect(res.headers.get("content-type")).toContain("application/json");
    const data = await res.json();
    expect(data.code).toBe("FORBIDDEN");
  });

  it("when backend fetch returns !ok (non-401), returns SSE error event at status 200", async () => {
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    try {
      vi.mocked(globalThis.fetch).mockResolvedValue({
        ok: false,
        status: 502,
        statusText: "Bad Gateway",
      } as Response);

      const req = new NextRequest("http://localhost/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          cookie: "access_token=t",
        },
        body: JSON.stringify({ message: "hi", conversation_history: [] }),
      });

      const res = await POST(req);
      expect(res.status).toBe(200);
      expect(res.headers.get("content-type")).toBe("text/event-stream");
      const text = await res.text();
      expect(text).toContain("error");
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    } finally {
      errSpy.mockRestore();
    }
  });

  it("does not log console.error in production for backend runtime errors", async () => {
    vi.stubEnv("NODE_ENV", "production");
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    try {
      vi.mocked(globalThis.fetch).mockResolvedValue({
        ok: false,
        status: 502,
        statusText: "Bad Gateway",
      } as Response);

      const req = new NextRequest("http://localhost/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          cookie: "access_token=t",
        },
        body: JSON.stringify({ message: "hi", conversation_history: [] }),
      });

      const res = await POST(req);
      expect(res.status).toBe(200);
      expect(await res.text()).toContain("error");
      expect(errSpy).not.toHaveBeenCalled();
    } finally {
      vi.unstubAllEnvs();
      errSpy.mockRestore();
    }
  });

  it("returns 400 when message is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        cookie: "access_token=t",
      },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("returns 400 with English error when Accept-Language prefers English", async () => {
    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept-Language": "en-GB",
        cookie: "access_token=t",
      },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    const data = JSON.parse(await res.text());
    expect(data.error).toBe("Message is required");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });
});
