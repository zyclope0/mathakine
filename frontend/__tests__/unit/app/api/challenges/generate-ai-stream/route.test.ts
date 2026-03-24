/** @vitest-environment node */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/challenges/generate-ai-stream/route";
import * as backendUrl from "@/lib/api/backendUrl";

import { createPostJsonRequest } from "../../_testRequest";

describe("POST /api/challenges/generate-ai-stream", () => {
  beforeEach(() => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(backendUrl, "getBackendUrl").mockReturnValue("https://api.test");
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("forwards JSON body, Cookie, X-CSRF-Token and Accept-Language to backend SSE", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: true,
      status: 200,
      body: new ReadableStream({
        start(c) {
          c.close();
        },
      }),
    } as Response);

    const payload = { challenge_type: "sequence", age_group: "9-11", prompt: "p" };
    const req = createPostJsonRequest("/api/challenges/generate-ai-stream", payload, {
      Cookie: "access_token=tok99",
      "X-CSRF-Token": "csrf-z",
      "Accept-Language": "en",
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "https://api.test/api/challenges/generate-ai-stream",
      expect.objectContaining({
        method: "POST",
        headers: {
          Cookie: "access_token=tok99",
          "Content-Type": "application/json",
          "X-CSRF-Token": "csrf-z",
          "Accept-Language": "en",
        },
        body: JSON.stringify(payload),
        redirect: "manual",
      })
    );
  });

  it("returns JSON error with backend status when backend response is not ok", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
    } as Response);

    const req = createPostJsonRequest(
      "/api/challenges/generate-ai-stream",
      { challenge_type: "sequence", age_group: "9-11" },
      { Cookie: "access_token=x" }
    );

    const res = await POST(req);
    expect(res.status).toBe(502);
    const data = JSON.parse(await res.text());
    expect(data.error).toContain("502");
    expect(data.error).toContain("Bad Gateway");
  });

  it("returns SSE error when access_token cookie is missing (no backend call)", async () => {
    const req = createPostJsonRequest("/api/challenges/generate-ai-stream", {
      challenge_type: "sequence",
      age_group: "9-11",
    });

    const res = await POST(req);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("text/event-stream");
    const text = await res.text();
    expect(text).toContain("Non authentifié");
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it("returns 500 JSON when getBackendUrl throws after auth cookie present", async () => {
    vi.spyOn(backendUrl, "getBackendUrl").mockImplementation(() => {
      throw new Error("NEXT_PUBLIC_API_BASE_URL manquant");
    });

    const req = createPostJsonRequest(
      "/api/challenges/generate-ai-stream",
      { challenge_type: "sequence", age_group: "9-11" },
      { Cookie: "access_token=y" }
    );

    const res = await POST(req);
    expect(res.status).toBe(500);
    const data = JSON.parse(await res.text());
    expect(data.error).toBe("Erreur lors de la connexion au backend");
    expect(data.details).toContain("NEXT_PUBLIC_API_BASE_URL");
  });
});
