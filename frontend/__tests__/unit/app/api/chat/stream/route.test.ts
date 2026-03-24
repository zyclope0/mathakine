/** @vitest-environment node */
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/chat/stream/route";
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

  it("forwards backend 200 stream as SSE Response with text/event-stream", async () => {
    const body = sseStream('data: {"type":"token","content":"a"}\n\n');
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body,
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    expect(res.headers.get("cache-control")).toBe("no-cache");

    expect(globalThis.fetch).toHaveBeenCalledWith("https://api.test/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "hi",
        conversation_history: [],
        stream: true,
      }),
    });
  });

  it("returns 500 JSON when getBackendUrl throws (no silent localhost in prod config)", async () => {
    vi.spyOn(backendUrl, "getBackendUrl").mockImplementation(() => {
      throw new Error("NEXT_PUBLIC_API_BASE_URL doit être défini en production.");
    });

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(500);
    expect(res.headers.get("content-type")).toBe("application/json");
    const data = JSON.parse(await res.text());
    expect(data.error).toContain("NEXT_PUBLIC_API_BASE_URL");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("when backend fetch returns !ok, returns SSE error event at status 200", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
    } as Response);

    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "hi", conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    const text = await res.text();
    expect(text).toContain("error");
    expect(globalThis.fetch).toHaveBeenCalledOnce();
  });

  it("returns 400 when message is missing", async () => {
    const req = new NextRequest("http://localhost/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_history: [] }),
    });

    const res = await POST(req);
    expect(res.status).toBe(400);
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });
});
